from states import PastState, FutureState, RiskState, MergedState
from server.database.utils import execute_query
from data_processing.utils import run_llm
from typing import Literal
from prompts import PAST_PERFORMANCE_SYSTEM_MESSAGE, FUTURE_OUTLOOK_SYSTEM_MESSAGE, RISK_FACTORS_SYSTEM_MESSAGE, HUMAN_PROMPT_TEMPLATE, PAST_PERFORMANCE_QUERIES, FUTURE_OUTLOOK_QUERIES, RISK_FACTORS_QUERIES
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from functools import partial
import json

load_dotenv()

# Retriever Node
def retriever(state: Literal[PastState, FutureState, RiskState], query_texts: list[str]) -> dict:
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    all_chunks = []
    all_scores = []
    seen_chunks = set()
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
            WHERE c.tic = '{state.tic}' 
                AND c.fiscal_year = {state.fiscal_year} 
                AND c.fiscal_quarter = {state.fiscal_quarter}
            ORDER BY e.embedding <=> '{vec_str}'::vector
            LIMIT {state.top_k};
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

    # print(f"Retrieved {len(all_chunks)} unique chunks.")
    return {"queries": query_texts, "chunks": all_chunks, "chunks_score": all_scores}

# Past Analysis Node
def past_analysis(state: PastState) -> dict:

    # Format context as a numbered list
    context = "\n".join([f"{i+1}. {chunk}" for i, chunk in enumerate(state.chunks)])
    prompt = HUMAN_PROMPT_TEMPLATE.format(
        tic=state.tic,
        company_name=state.company_name or '',
        industry=state.industry or '',
        sector=state.sector or '',
        company_description=state.company_description or '',
        fiscal_year=state.fiscal_year,
        fiscal_quarter=state.fiscal_quarter,
        stage="past_analysis",
        context=context
    )
    response = json.loads(run_llm(prompt, PAST_PERFORMANCE_SYSTEM_MESSAGE).content)
    return {**response}

# Future Analysis Node
def future_analysis(state: FutureState) -> dict:

    # Format context as a numbered list
    context = "\n".join([f"{i+1}. {chunk}" for i, chunk in enumerate(state.chunks)])
    prompt = HUMAN_PROMPT_TEMPLATE.format(
        tic=state.tic,
        company_name=state.company_name or '',
        industry=state.industry or '',
        sector=state.sector or '',
        company_description=state.company_description or '',
        fiscal_year=state.fiscal_year,
        fiscal_quarter=state.fiscal_quarter,
        stage="future_analysis",
        context=context
    )
    response = json.loads(run_llm(prompt, FUTURE_OUTLOOK_SYSTEM_MESSAGE).content)
    return {**response}

# Risk Analysis Node
def risk_analysis(state: RiskState) -> dict:

    # Format context as a numbered list
    context = "\n".join([f"{i+1}. {chunk}" for i, chunk in enumerate(state.chunks)])
    prompt = HUMAN_PROMPT_TEMPLATE.format(
        tic=state.tic,
        company_name=state.company_name or '',
        industry=state.industry or '',
        sector=state.sector or '',
        company_description=state.company_description or '',
        fiscal_year=state.fiscal_year,
        fiscal_quarter=state.fiscal_quarter,
        stage="risk_analysis",
        context=context
    )
    response = json.loads(run_llm(prompt, RISK_FACTORS_SYSTEM_MESSAGE).content)
    return {**response}


retriever_past_analysis = partial(retriever, query_texts=PAST_PERFORMANCE_QUERIES)
retriever_future_analysis = partial(retriever, query_texts=FUTURE_OUTLOOK_QUERIES)
retriever_risk_analysis = partial(retriever, query_texts=RISK_FACTORS_QUERIES)



