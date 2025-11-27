import uuid
from database.utils import execute_query
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from typing import Literal, Optional, Union
from prompts import CATALYST_QUERIES, STAGE1_HUMAN_PROMPT, STAGE2_HUMAN_PROMPT, STAGE1_SYSTEM_MESSAGE, STAGE2_SYSTEM_MESSAGE
from states import CatalystSession, CatalystContext, Catalyst, catalyst_session_factory
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from etl_pipeline.utils import run_llm
import json
load_dotenv()




# Retriever Node
def retriever_node(state: CatalystSession) -> dict:
    # print("Starting retriever_node...")
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    tic = state.query_params.tic
    top_k = state.query_params.top_k
    source_type = state.query_params.source_type
    catalyst_type = state.query_params.catalyst_type
    calendar_year = state.query_params.calendar_year
    calendar_quarter = state.query_params.calendar_quarter
    calendar_month = state.query_params.calendar_month
    
    catalysts = []
    seen_chunks = set()

    query_texts = CATALYST_QUERIES[catalyst_type]

    for query_text in query_texts:
        query_vec = embedding_model.embed_query(query_text)
        vec_str = "[" + ",".join(map(str, query_vec)) + "]"

        sql = get_sql_query(source_type, tic, calendar_year, calendar_quarter, calendar_month,
                            vec_str, top_k)

        results = execute_query(sql)
        if results is None:
            return {}

        for i in range(len(results)):
            event_id = str(results.iloc[i]['event_id'])
            chunk_id = results.iloc[i]['chunk_id']
            id = f"{event_id}_{chunk_id}"
            chunk = results.iloc[i]['chunk']
            date = str(results.iloc[i]['date'])
            score = results.iloc[i]['cosine_sim']
            source = results.iloc[i]['source']
            url = results.iloc[i]['url']
            raw_json_sha256 = results.iloc[i]['raw_json_sha256']
    
            if id not in seen_chunks:
                catalyst = CatalystContext.create_from_chunk(
                    event_id=event_id,
                    chunk_id=chunk_id,
                    source_type=source_type,
                    catalyst_type=catalyst_type,
                    retrieval_query=query_text,
                    date=date,
                    content=chunk,
                    score=score,
                    source=str(source),
                    url=url,
                    raw_json_sha256=str(raw_json_sha256)
                )
                catalysts.append(catalyst)
                seen_chunks.add(id)
    return {"catalysts": catalysts}


def current_catalysts_retriever_node(state: CatalystSession) -> dict:
    # print("Starting current_catalysts_retriever_node...") 
    # print(f"Total chunks retrieved: {len(state.catalysts)}")  
    tic = state.query_params.tic
    catalyst_type = state.query_params.catalyst_type

    sql = f"""
        SELECT catalyst_id, catalyst_type, state, title, summary, evidence, time_horizon,
               certainty, impact_area, sentiment, impact_magnitude
        FROM core.catalyst_master
        WHERE tic = '{tic}' AND catalyst_type = '{catalyst_type}';
    """

    results = execute_query(sql)
    if results is None:
        return {}

    current_catalysts = []
    for i in range(len(results)):
        catalyst = Catalyst(
            is_catalyst=True,
            rationale="",
            catalyst_type=results.iloc[i]['catalyst_type'],
            catalyst_id=str(results.iloc[i]['catalyst_id']),
            state=results.iloc[i]['state'],
            title=results.iloc[i]['title'],
            summary=results.iloc[i]['summary'],
            evidence=results.iloc[i]['evidence'],
            time_horizon=results.iloc[i]['time_horizon'],
            certainty=results.iloc[i]['certainty'],
            impact_area=results.iloc[i]['impact_area'],
            sentiment=results.iloc[i]['sentiment'],
            impact_magnitude=results.iloc[i]['impact_magnitude'],
        )
        current_catalysts.append(catalyst)
    return {"current_catalysts": current_catalysts} 

def get_sql_query(source_type: str, tic: str, calendar_year: int, calendar_quarter: Optional[int], 
                  calendar_month: Optional[int], vec_str: str, top_k: int = 3) -> str:
    if source_type == "earnings_transcript":
        sql = f"""
            SELECT
            c.tic, t.earnings_date AS date, c.event_id, c.chunk_id, c.chunk,
            1 - (e.embedding <=> '{vec_str}'::vector)   AS cosine_sim,
            t.source, NULL AS url, t.raw_json_sha256
            FROM core.earnings_transcript_chunks  AS c
            JOIN core.earnings_transcript_embeddings AS e
            ON c.event_id = e.event_id AND c.chunk_id = e.chunk_id
            JOIN core.earnings_transcripts AS t
            ON c.event_id = t.event_id
            WHERE c.tic = '{tic}' 
                AND c.calendar_year = {calendar_year}
                AND c.calendar_quarter = {calendar_quarter}
                AND (1 - (e.embedding <=> '{vec_str}'::vector)) > 0.3
            ORDER BY cosine_sim DESC
            LIMIT {top_k};
        """
    elif source_type == "news":
        sql = f"""
            SELECT
            c.tic, c.published_at::DATE as date, c.event_id, c.chunk_id, c.chunk,
            1 - (e.embedding <=> '{vec_str}'::vector)  AS cosine_sim,
            n.source, n.url, n.raw_json_sha256
            FROM core.news_chunks  AS c
            JOIN core.news_embeddings AS e
            ON c.event_id = e.event_id AND c.chunk_id = e.chunk_id
            JOIN core.news AS n
            ON c.event_id = n.event_id
            WHERE c.tic = '{tic}' 
                AND EXTRACT(YEAR FROM c.published_at) = {calendar_year}
                AND EXTRACT(MONTH FROM c.published_at) = {calendar_month}
                AND (1 - (e.embedding <=> '{vec_str}'::vector)) > 0.3
            ORDER BY cosine_sim DESC
            LIMIT {top_k};
        """
    else:
        raise ValueError(f"Unsupported source_type: {source_type}") 

    return sql


def stage1_node(state: CatalystSession) -> dict:
    updated_contexts = []

    for ctx in state.catalysts:  # ctx is a CatalystContext
        catalyst_type = ctx.chunk.catalyst_type
        retrieval_query = ctx.chunk.retrieval_query
        content = ctx.chunk.content

        # make sure we have a candidate shell
        if ctx.candidate is None:
            ctx.candidate = Catalyst.init()

        # dump company info as JSON so the LLM gets a proper structure
        company_info_json = json.dumps(
            state.company_info.model_dump(), ensure_ascii=False
        )

        human_prompt = STAGE1_HUMAN_PROMPT.format(
            company_info=company_info_json,
            catalyst_type=catalyst_type,
            retrieval_query=retrieval_query,
            content=content,
        )
        system_prompt = SystemMessage(content=STAGE1_SYSTEM_MESSAGE)
        messages = [system_prompt, HumanMessage(content=human_prompt)]

        llm_raw = run_llm(messages).content
        llm_dict = json.loads(llm_raw)

        # normalize is_catalyst: model promises 0|1, but be defensive
        is_cat_val = llm_dict.get("is_catalyst")
  

        # build a validated Catalyst out of stage1
        stage1_catalyst = Catalyst(
            is_catalyst=is_cat_val,
            rationale=llm_dict.get("rationale", "")[:200],  # hard cap, just in case
            catalyst_type=catalyst_type,
        )

        # write back
        ctx.candidate = stage1_catalyst
        updated_contexts.append(ctx)

    return {"catalysts": updated_contexts}


def stage2_node(state: CatalystSession) -> dict:
    current_catalysts = state.current_catalysts

    # we will build a new list so we don't accidentally mutate weirdly
    updated_contexts = []

    for ctx in state.catalysts:  # ctx is a CatalystContext
        cand = ctx.candidate
        # skip if stage 1 said "no"
        if not cand or not cand.is_catalyst:
            updated_contexts.append(ctx)
            continue

        catalyst_type = ctx.chunk.catalyst_type
        retrieval_query = ctx.chunk.retrieval_query
        content = ctx.chunk.content
        rationale = cand.rationale

        # send REAL json to the model
        current_catalysts_json = [c.model_dump() for c in current_catalysts]
        # print(f"No. of Current catalysts JSON: {len(current_catalysts_json)}")

        human_prompt = STAGE2_HUMAN_PROMPT.format(
            company_info=json.dumps(state.company_info.model_dump(), ensure_ascii=False),
            catalyst_type=catalyst_type,
            retrieval_query=retrieval_query,
            content=content,
            rationale=rationale,
            current_catalysts_json=json.dumps(current_catalysts_json, ensure_ascii=False),
        )
        system_prompt = SystemMessage(content=STAGE2_SYSTEM_MESSAGE[catalyst_type])
        messages = [system_prompt, HumanMessage(content=human_prompt)]

        # 1) call LLM
        llm_raw = run_llm(messages).content

        # 2) parse json
        llm_dict = json.loads(llm_raw)

        new_catalyst_flag = llm_dict.get("catalyst_id") is None
        llm_dict["catalyst_id"] = str(uuid.uuid4()) if new_catalyst_flag else llm_dict.get("catalyst_id")

        # 3) VALIDATE with your Pydantic Catalyst
        #    this is the part that will raise if sentiment="positive" but model wants IntEnum
        stage2_catalyst = Catalyst.model_validate({
            # keep stage1 info
            "is_catalyst": cand.is_catalyst,
            "rationale": cand.rationale,
            "catalyst_type": catalyst_type,
            # stage2 info from llm
            **llm_dict,
        })

        # 4) write back to context
        ctx.candidate = stage2_catalyst
        if new_catalyst_flag:
            state.current_catalysts.append(stage2_catalyst)
        else:
            # update existing catalyst in current_catalysts
            for i, existing_cat in enumerate(state.current_catalysts):
                if existing_cat.catalyst_id == stage2_catalyst.catalyst_id:
                    state.current_catalysts[i] = stage2_catalyst
                    break
        updated_contexts.append(ctx)

    return {"catalysts": updated_contexts}

