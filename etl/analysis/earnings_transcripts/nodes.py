from states import PastState, FutureState, RiskState, RiskResponseState, MergedState
from database.utils import execute_query
from etl.utils import parse_json_with_fallback, run_llm
from typing import Literal, Optional
from prompts import PAST_PERFORMANCE_SYSTEM_MESSAGE, FUTURE_OUTLOOK_SYSTEM_MESSAGE, \
                    RISK_FACTORS_SYSTEM_MESSAGE, RISK_RESPONSE_SYSTEM_MESSAGE, \
                    HUMAN_PROMPT_TEMPLATE, RISK_RESPONSE_QUERY_GEN_SYSTEM_MESSAGE, \
                    RISK_RESPONSE_QUERY_GEN_HUMAN_MESSAGE
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from functools import partial
import json
import os
import database.config


STAGES = {
    "past": {
        "retriever": "past_retriever",
        "analysis": "past_analysis",
        "base_model": PastState,
        "system_message": PAST_PERFORMANCE_SYSTEM_MESSAGE,
        "max_chunks": 10,
    },
    "future": {
        "retriever": "future_retriever",
        "analysis": "future_analysis",
        "base_model": FutureState,
        "system_message": FUTURE_OUTLOOK_SYSTEM_MESSAGE,
        "max_chunks": 10,
    },
    "risk": {
        "retriever": "risk_retriever",
        "analysis": "risk_analysis",
        "base_model": RiskState,
        "system_message": RISK_FACTORS_SYSTEM_MESSAGE,
        "max_chunks": 12,  # Higher cap to capture both operational and strategic risks
    },
    "risk_response": {
        "retriever": "risk_response_retriever",
        "analysis": "risk_response_analysis",
        "base_model": RiskResponseState,
        "system_message": RISK_RESPONSE_SYSTEM_MESSAGE,
        "max_chunks": 15,  # Higher cap to reduce query-variance sensitivity
        "query_gen_system_message": RISK_RESPONSE_QUERY_GEN_SYSTEM_MESSAGE,
        "query_gen_human_message": RISK_RESPONSE_QUERY_GEN_HUMAN_MESSAGE,
    },
}

# Retrieval constants
MIN_SIMILARITY = 0.25  # Minimum cosine similarity threshold for chunk inclusion

# Boilerplate phrases to filter out (e.g., legal safe-harbor disclaimers)
BOILERPLATE_PHRASES = [
    "forward-looking statements",
    "form 10-q",
    "form 10-k",
    "form 8-k",
    "risk factors discussed in",
    "assumes no obligation to update",
    "speak only as of the date",
]


# ---- Helpers ----

def _to_dict(obj) -> dict:
    """Convert a Pydantic model or dict-like object to a plain dict."""
    return obj.model_dump() if hasattr(obj, 'model_dump') else dict(obj)


def _build_company_prompt(company_info: dict, context: str = '') -> str:
    """Format the shared human prompt template from company_info."""
    return HUMAN_PROMPT_TEMPLATE.format(
        tic=company_info["tic"],
        company_name=company_info["company_name"] or '',
        industry=company_info["industry"] or '',
        sector=company_info["sector"] or '',
        calendar_year=company_info["calendar_year"] or '',
        calendar_quarter=company_info["calendar_quarter"] or '',
        context=context,
    )


# ---- Retriever Node ----

def retriever(state: MergedState,
              type: Literal["past", "future", "risk", "risk_response"]
              ) -> dict:
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    all_chunks = []
    all_scores = []
    seen_chunks = set()
    company_info = state.company_info
    retriever_cfg = getattr(state, STAGES[type]["retriever"])
    query_texts = retriever_cfg["queries"]

    if len(query_texts) == 0:
        raise ValueError("query_texts cannot be empty.")

    # Batch embed all queries at once for efficiency
    query_vecs = embedding_model.embed_documents(query_texts)

    for query_vec in query_vecs:
        vec_str = "[" + ",".join(map(str, query_vec)) + "]"
        sql = """
            SELECT
                c.tic,
                c.calendar_year,
                c.calendar_quarter,
                c.chunk_id,
                c.chunk,
                1 - (e.embedding <=> %s::vector) AS similarity
            FROM core.earnings_transcript_embeddings e
            JOIN core.earnings_transcript_chunks c
            USING (tic, calendar_year, calendar_quarter, chunk_id)
            WHERE c.tic = %s 
                AND c.calendar_year = %s 
                AND c.calendar_quarter = %s
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s;
        """
        params = (vec_str, company_info["tic"], company_info["calendar_year"],
                  company_info["calendar_quarter"], vec_str, retriever_cfg["top_k"])

        results = execute_query(sql, params)

        for row in results.itertuples():
            # Skip boilerplate/safe-harbor disclaimer chunks
            if any(bp in row.chunk.lower() for bp in BOILERPLATE_PHRASES):
                continue
            if row.chunk_id not in seen_chunks and row.similarity >= MIN_SIMILARITY:
                all_chunks.append(row.chunk)
                all_scores.append(row.similarity)
                seen_chunks.add(row.chunk_id)

    if not all_chunks:
        raise RuntimeError("No chunks found for the given parameters.")

    # Sort by score descending and cap at max_chunks for this stage
    max_cap = STAGES[type]["max_chunks"]
    sorted_pairs = sorted(zip(all_scores, all_chunks), key=lambda x: x[0], reverse=True)[:max_cap]
    all_scores = [s for s, _ in sorted_pairs]
    all_chunks = [c for _, c in sorted_pairs]

    return { STAGES[type]["retriever"]: {"top_k": retriever_cfg["top_k"], 
                                         "queries": query_texts,
                                         "chunks": all_chunks, 
                                         "chunks_score": all_scores} }



# ---- Analysis Nodes ----

MAX_LLM_RETRIES = 2  # Retries within analysis node before raising to outer retry logic

def analysis_node(state: MergedState,
                  type: Literal['past', 'future', 'risk', 'risk_response'],
                  history: Optional[Literal['past', 'future', 'risk', 'risk_response']] = None
                  ) -> dict:
    cfg = STAGES[type]
    company_info = state.company_info
    retriever_data = getattr(state, cfg["retriever"])

    # Format context as a numbered list and build prompt
    context = "\n".join(f"{i+1}. {chunk}" for i, chunk in enumerate(retriever_data["chunks"]))
    prompt = _build_company_prompt(company_info, context)

    system_prompt = SystemMessage(content=cfg["system_message"])
    human_prompt = HumanMessage(content=prompt)
    if history:
        history_data = _to_dict(getattr(state, STAGES[history]['analysis']))
        messages = [system_prompt, AIMessage(content=json.dumps(history_data)), human_prompt]
    else:
        messages = [system_prompt, human_prompt]

    # Retry loop with Pydantic validation (enforces structured output)
    model_cls = cfg["base_model"]
    last_error = None
    raw_response = None
    for attempt in range(MAX_LLM_RETRIES):
        try:
            raw_response = run_llm(messages).content
            output = parse_json_with_fallback(raw_response)
            if not output:
                raise ValueError("Empty or unparseable JSON from LLM")
            # Pydantic validation: rejects wrong types, out-of-range enums, etc.
            validated = model_cls(**output)
            return {cfg["analysis"]: validated.model_dump()}
        except Exception as e:
            last_error = e
            if attempt < MAX_LLM_RETRIES - 1:
                print(f"[analysis_node] '{type}' attempt {attempt + 1} failed: {e}. Retrying...")
    raise RuntimeError(
        f"Analysis node failed for type '{type}' after {MAX_LLM_RETRIES} attempts: {last_error}\n"
        f"Raw response:\n{raw_response}"
    )


past_analysis_node = partial(analysis_node, type='past')
future_analysis_node = partial(analysis_node, type='future')
risk_analysis_node = partial(analysis_node, type='risk')
risk_response_analysis_node = partial(analysis_node, type='risk_response', history='risk')

past_retriever_node = partial(retriever, type='past')
future_retriever_node = partial(retriever, type='future')
risk_retriever_node = partial(retriever, type='risk')
risk_response_retriever_node = partial(retriever, type='risk_response')


def queries_powered_by_llm(state: MergedState,
                           type: Literal['past', 'future', 'risk', 'risk_response']) -> dict:
    cfg = STAGES[type]
    company_info = state.company_info
    prompt = cfg["query_gen_human_message"].format(
        tic=company_info["tic"],
        company_name=company_info["company_name"] or '',
        industry=company_info["industry"] or '',
        sector=company_info["sector"] or '',
        calendar_year=company_info["calendar_year"],
        calendar_quarter=company_info["calendar_quarter"],
    )
    messages = [
        SystemMessage(content=cfg["query_gen_system_message"]),
        AIMessage(content=json.dumps(_to_dict(state.risk_analysis))),
        HumanMessage(content=prompt),
    ]
    raw = run_llm(messages).content
    response = parse_json_with_fallback(raw)
    if not response or "queries" not in response:
        raise ValueError(f"Failed to parse queries from LLM response: {raw[:200]}")
    return {cfg["retriever"]: {
        "top_k": state.risk_response_retriever["top_k"],
        "queries": response["queries"],
        "chunks": [],
        "chunks_score": [],
    }}

risk_response_queries_powered_by_llm = partial(queries_powered_by_llm, type='risk_response')
