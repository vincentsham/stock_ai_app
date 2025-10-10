from states import PastState, FutureState, RiskState, RiskResponseState, MergedState
from server.database.utils import execute_query
from data_processing.utils import run_llm
from typing import Literal, Optional, Union
from prompts import PAST_PERFORMANCE_SYSTEM_MESSAGE, FUTURE_OUTLOOK_SYSTEM_MESSAGE, \
                    RISK_FACTORS_SYSTEM_MESSAGE, RISK_RESPONSE_SYSTEM_MESSAGE, \
                    HUMAN_PROMPT_TEMPLATE, RISK_RESPONSE_QUERY_GEN_SYSTEM_MESSAGE, \
                    RISK_RESPONSE_QUERY_GEN_HUMAN_MESSAGE
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.types import Command 
from dotenv import load_dotenv
from functools import partial
import json

load_dotenv()

STAGES = {
    "past": {
        "retriever": "past_retriever",
        "analysis": "past_analysis",
        "system_message": PAST_PERFORMANCE_SYSTEM_MESSAGE
    },
    "future": {
        "retriever": "future_retriever",
        "analysis": "future_analysis",
        "system_message": FUTURE_OUTLOOK_SYSTEM_MESSAGE
    },
    "risk": {
        "retriever": "risk_retriever",
        "analysis": "risk_analysis",
        "system_message": RISK_FACTORS_SYSTEM_MESSAGE
    },
    "risk_response": {
        "retriever": "risk_response_retriever",
        "analysis": "risk_response_analysis",
        "system_message": RISK_RESPONSE_SYSTEM_MESSAGE
    },
}



# Retriever Node
def retriever(state: MergedState, 
              type: Literal["past", "future", "risk", "risk_response"]
              ) -> dict:
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    all_chunks = []
    all_scores = []
    seen_chunks = set()
    company_info = state.company_info
    retriever = getattr(state, STAGES[type]["retriever"])
    query_texts = retriever.queries

    if len(query_texts) == 0:
        raise ValueError("query_texts cannot be empty.")
    for query_text in query_texts:
        query_vec = embedding_model.embed_query(query_text)
        vec_str = "[" + ",".join(map(str, query_vec)) + "]"
        sql = f"""
            SELECT
                c.tic,
                c.fiscal_year,
                c.fiscal_quarter,
                c.chunk_id,
                c.chunk,
                1 - (e.embedding <=> '{vec_str}'::vector) AS similarity
            FROM core.earnings_transcript_embeddings e
            JOIN core.earnings_transcript_chunks c
            USING (tic, fiscal_year, fiscal_quarter, chunk_id)
            WHERE c.tic = '{company_info.tic}' 
                AND c.fiscal_year = {company_info.fiscal_year} 
                AND c.fiscal_quarter = {company_info.fiscal_quarter}
            ORDER BY e.embedding <=> '{vec_str}'::vector
            LIMIT {retriever.top_k};
        """

        results = execute_query(sql)

        for i in range(len(results)):
            chunk_id = results.iloc[i]['chunk_id']
            chunk = results.iloc[i]['chunk']
            score = results.iloc[i]['similarity']
            if chunk_id not in seen_chunks:
                all_chunks.append(chunk)
                all_scores.append(score)
                seen_chunks.add(chunk_id)
    if not all_chunks:
        raise RuntimeError("No chunks found for the given parameters.")

    return { STAGES[type]["retriever"]: {"chunks": all_chunks, "chunks_score": all_scores} }


# Analysis Nodes
def analysis_node(state: MergedState, 
                  type: Literal['past', 'future', 'risk', 'risk_response'],
                  history: Optional[Literal['past', 'future', 'risk', 'risk_response']] = None
                  ) -> dict:

    # Format context as a numbered list
    company_info = state.company_info
    retriever = getattr(state, STAGES[type]["retriever"])

    context = "\n".join([f"{i+1}. {chunk}" for i, chunk in enumerate(retriever.chunks)])
    prompt = HUMAN_PROMPT_TEMPLATE.format(
        tic=company_info.tic,
        company_name=company_info.company_name or '',
        industry=company_info.industry or '',
        sector=company_info.sector or '',
        company_description=company_info.company_description or '',
        fiscal_year=company_info.fiscal_year,
        fiscal_quarter=company_info.fiscal_quarter,
        stage=type,
        context=context
    )

    system_prompt = SystemMessage(content=STAGES[type]["system_message"])
    human_prompt = HumanMessage(content=prompt)
    if history:
        ai_prompt = AIMessage(content=getattr(state, STAGES[history]['analysis']).json())
        messages = [system_prompt, ai_prompt, human_prompt]
    else:
        messages = [system_prompt, human_prompt]
    response = json.loads(run_llm(messages).content)
    return { STAGES[type]["analysis"]: {**response} }




past_analysis_node = partial(analysis_node, type='past')
future_analysis_node = partial(analysis_node, type='future')
risk_analysis_node = partial(analysis_node, type='risk')
risk_response_analysis_node = partial(analysis_node, type='risk_response', history='risk')

past_retriever_node = partial(retriever, type='past')
future_retriever_node = partial(retriever, type='future')
risk_retriever_node = partial(retriever, type='risk')
risk_response_retriever_node = partial(retriever, type='risk_response')


def queries_powered_by_llm(state: MergedState) -> dict:
    company_info = state.company_info
    prompt = RISK_RESPONSE_QUERY_GEN_HUMAN_MESSAGE.format(
        tic=company_info.tic,
        company_name=company_info.company_name or '',
        industry=company_info.industry or '',
        sector=company_info.sector or '',
        company_description=company_info.company_description or '',
        fiscal_year=company_info.fiscal_year,
        fiscal_quarter=company_info.fiscal_quarter,
    )
    system_prompt = SystemMessage(content=RISK_RESPONSE_QUERY_GEN_SYSTEM_MESSAGE)
    ai_message = AIMessage(content=state.risk_analysis.json())
    human_prompt = HumanMessage(content=prompt)
    messages = [system_prompt, ai_message, human_prompt]
    response = json.loads(run_llm(messages).content)
    return {"risk_response_retriever": {"queries": response['queries']}}


