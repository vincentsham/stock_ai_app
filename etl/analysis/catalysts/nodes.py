import uuid
from database.utils import execute_query
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from typing import Literal, Optional, Union
from prompts import CATALYST_QUERIES, STAGE1_HUMAN_PROMPT, STAGE2A_HUMAN_PROMPT, \
    STAGE2B_HUMAN_PROMPT, STAGE1_SYSTEM_MESSAGE, STAGE2A_SYSTEM_MESSAGE, STAGE2B_SYSTEM_MESSAGE, STAGE3_HUMAN_PROMPT, STAGE3_SYSTEM_MESSAGE
from states import CatalystSession, CatalystContext, Catalyst, catalyst_session_factory
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from etl.utils import run_llm, parse_json_from_llm
import json
import os
load_dotenv()

# Helper function to build SQL query
def get_sql_query(source_type: str, tic: str, calendar_year: int, calendar_quarter: Optional[int], 
                  calendar_month: Optional[int], vec_str: str, top_k: int = 3) -> str:
    # if source_type == "earnings_transcript":
    #     sql = f"""
    #         SELECT
    #         c.tic, t.earnings_date AS date, c.event_id, c.chunk_id, c.chunk,
    #         1 - (e.embedding <=> '{vec_str}'::vector)   AS cosine_sim,
    #         t.source, NULL AS url, e.embedding, t.raw_json_sha256
    #         FROM core.earnings_transcript_chunks  AS c
    #         JOIN core.earnings_transcript_chunk_signal AS s
    #         ON c.event_id = s.event_id AND c.chunk_id = s.chunk_id
    #         JOIN core.earnings_transcript_embeddings AS e
    #         ON c.event_id = e.event_id AND c.chunk_id = e.chunk_id
    #         JOIN core.earnings_transcripts AS t
    #         ON c.event_id = t.event_id
    #         WHERE c.tic = '{tic}' 
    #             AND (s.is_signal = 1
    #                 OR (1 - (e.embedding <=> '{vec_str}'::vector)) > 0.5)
    #             AND c.calendar_year = {calendar_year}
    #             AND c.calendar_quarter = {calendar_quarter}
    #             AND NOT EXISTS (
    #                     SELECT 1 
    #                     FROM core.catalyst_versions v 
    #                     WHERE v.event_id = c.event_id 
    #                     AND v.chunk_id = c.chunk_id
    #                 )
    #         ORDER BY cosine_sim DESC
    #         LIMIT {top_k};
    #     """

    # elif source_type == "news":
    #     sql = f"""
    #         SELECT
    #         c.tic, c.published_at::DATE as date, c.event_id, c.chunk_id, c.chunk,
    #         1 - (e.embedding <=> '{vec_str}'::vector)  AS cosine_sim,
    #         n.source, n.url, e.embedding, n.raw_json_sha256
    #         FROM core.news_chunks  AS c
    #         JOIN core.news_chunk_signal AS s
    #         ON c.event_id = s.event_id AND c.chunk_id = s.chunk_id
    #         JOIN core.news_embeddings AS e
    #         ON c.event_id = e.event_id AND c.chunk_id = e.chunk_id
    #         JOIN core.news AS n
    #         ON c.event_id = n.event_id
    #         WHERE c.tic = '{tic}' 
    #             AND (s.is_signal = 1
    #                 OR (1 - (e.embedding <=> '{vec_str}'::vector)) > 0.5)
    #             AND EXTRACT(YEAR FROM c.published_at) = {calendar_year}
    #             AND EXTRACT(MONTH FROM c.published_at) = {calendar_month}
    #             AND NOT EXISTS (
    #                     SELECT 1 
    #                     FROM core.catalyst_versions v 
    #                     WHERE v.event_id = c.event_id 
    #                     AND v.chunk_id = c.chunk_id
    #                 )
    #         ORDER BY cosine_sim DESC
    #         LIMIT {top_k};
    #     """
    if source_type == "earnings_transcript":
        sql = f"""
            SELECT
            c.tic, t.earnings_date AS date, c.event_id, c.chunk_id, c.chunk,
            1 - (e.embedding <=> '{vec_str}'::vector)   AS cosine_sim,
            t.source, NULL AS url, e.embedding, t.raw_json_sha256
            FROM core.earnings_transcript_chunks  AS c
            JOIN core.earnings_transcript_embeddings AS e
            ON c.event_id = e.event_id AND c.chunk_id = e.chunk_id
            JOIN core.earnings_transcripts AS t
            ON c.event_id = t.event_id
            WHERE c.tic = '{tic}' 
                AND c.calendar_year = {calendar_year}
                AND c.calendar_quarter = {calendar_quarter}
                AND (1 - (e.embedding <=> '{vec_str}'::vector)) > 0.2
                AND NOT EXISTS (
                        SELECT 1 
                        FROM core.catalyst_versions v 
                        WHERE v.event_id = c.event_id 
                        AND v.chunk_id = c.chunk_id
                    )
            ORDER BY cosine_sim DESC
            LIMIT {top_k};
        """

    elif source_type == "news":
        sql = f"""
            SELECT
            c.tic, c.published_at::DATE as date, c.event_id, c.chunk_id, c.chunk,
            1 - (e.embedding <=> '{vec_str}'::vector)  AS cosine_sim,
            n.source, n.url, e.embedding, n.raw_json_sha256
            FROM core.news_chunks  AS c
            JOIN core.news_embeddings AS e
            ON c.event_id = e.event_id AND c.chunk_id = e.chunk_id
            JOIN core.news AS n
            ON c.event_id = n.event_id
            WHERE c.tic = '{tic}' 
                AND EXTRACT(YEAR FROM c.published_at) = {calendar_year}
                AND EXTRACT(MONTH FROM c.published_at) = {calendar_month}
                AND (1 - (e.embedding <=> '{vec_str}'::vector)) > 0.2
                AND NOT EXISTS (
                        SELECT 1 
                        FROM core.catalyst_versions v 
                        WHERE v.event_id = c.event_id 
                        AND v.chunk_id = c.chunk_id
                    )
            ORDER BY cosine_sim DESC
            LIMIT {top_k};
        """
    else:
        raise ValueError(f"Unsupported source_type: {source_type}") 

    return sql


# Retriever Node
def retriever_node(state: CatalystSession) -> dict:
    # print("Starting retriever_node...")
    embedding_model = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL"))
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
        if results is None or len(results) == 0:
            print(f"No results found for query: {source_type}, {tic}, {calendar_year}, {calendar_quarter}, {calendar_month}")
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
            embedding = results.iloc[i]['embedding']
            # process the embedding from string to list of floats
            if isinstance(embedding, str):
                embedding = json.loads(embedding)
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
                    embedding=embedding,
                    raw_json_sha256=str(raw_json_sha256)
                )
                catalysts.append(catalyst)
                seen_chunks.add(id)
    return {"catalysts": catalysts}


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
        company_dict = state.company_info.model_dump()
        company_info_json = json.dumps(company_dict, ensure_ascii=False)
        # provide specific fields used in the prompt formatting
        company_tic = company_dict.get("tic", "")
        company_name = company_dict.get("company_name", company_dict.get("name", ""))

        human_prompt = STAGE1_HUMAN_PROMPT.format(
            company_info=company_info_json,
            company_tic=company_tic,
            company_name=company_name,
            catalyst_type=catalyst_type,
            retrieval_query=retrieval_query,
            content=content,
        )
        system_prompt = SystemMessage(content=STAGE1_SYSTEM_MESSAGE)
        messages = [system_prompt, HumanMessage(content=human_prompt)]

        llm_raw = run_llm(messages).content
        llm_dict = parse_json_from_llm(llm_raw)

        # normalize is_catalyst: model promises 0|1, but be defensive
        is_cat_val = llm_dict.get("is_catalyst")
  

        # build a validated Catalyst out of stage1
        stage1_catalyst = Catalyst(
            is_catalyst=is_cat_val,
            rationale=llm_dict.get("rationale", "")[:200],  # hard cap, just in case
            catalyst_type=catalyst_type,
            evidence=llm_dict.get("evidence", ""),
        )

        # write back
        ctx.candidate = stage1_catalyst
        if not is_cat_val:
            ctx.action = "skip"
        updated_contexts.append(ctx)

    return {"catalysts": updated_contexts}


def stage2a_node(state: CatalystSession) -> dict:
    updated_contexts = []

    # total_catalysts = sum(1 for ctx in state.catalysts if ctx.candidate and ctx.candidate.is_catalyst)
    # print(f"Total catalyst chunks from stage1: {total_catalysts}/{len(state.catalysts)}")

    for ctx in state.catalysts:  # ctx is a CatalystContext
        cand = ctx.candidate
        # skip if stage 1 said "no"
        if not cand.is_catalyst:
            ctx.action = "skip"
            ctx.current_catalysts = []
            updated_contexts.append(ctx)
            continue

        catalyst_type = ctx.chunk.catalyst_type
        evidence = cand.evidence
        rationale = cand.rationale

        chunk_date = ctx.chunk.date
        # date_filter = f"AND date::DATE >= '{chunk_date}'::DATE - INTERVAL '6 months'"
        date_filter = f"AND ABS(date::DATE - '{chunk_date}'::DATE) <= 180"
        tic = state.query_params.tic
        vec_str = ctx.chunk.embedding

        sql = f"""
            WITH e AS (
            SELECT cm.catalyst_id, cm.catalyst_type, cm.state, cm.date, cm.title, cm.summary, cm.time_horizon,
                cm.certainty, cm.impact_area, cm.sentiment, cm.impact_magnitude,
                1 - (cme.embedding <=> '{vec_str}'::vector)   AS cosine_sim
            FROM core.catalyst_master cm
            JOIN core.catalyst_master_embeddings cme
                ON cm.catalyst_id = cme.catalyst_id
            WHERE tic = '{tic}'
                {date_filter if chunk_date else ''}
            )
            SELECT catalyst_id, catalyst_type, state, date, title, summary, time_horizon,
                certainty, impact_area, sentiment, impact_magnitude
            FROM e
            ORDER BY cosine_sim DESC
            LIMIT 5;
        """

        results = execute_query(sql)
        if results is None or len(results) == 0:
            ctx.action = "create"
            ctx.current_catalysts = []
            updated_contexts.append(ctx)
            continue

        current_catalysts = []
        for i in range(len(results)):
            catalyst = Catalyst(
                is_catalyst=True,
                rationale="",
                catalyst_type=results.iloc[i]['catalyst_type'],
                catalyst_id=str(results.iloc[i]['catalyst_id']),
                state=results.iloc[i]['state'],
                date=results.iloc[i]['date'].strftime("%Y-%m-%d"),
                title=results.iloc[i]['title'],
                summary=results.iloc[i]['summary'],
                time_horizon=results.iloc[i]['time_horizon'],
                certainty=results.iloc[i]['certainty'],
                impact_area=results.iloc[i]['impact_area'],
                sentiment=results.iloc[i]['sentiment'],
                impact_magnitude=results.iloc[i]['impact_magnitude'],
            )
            current_catalysts.append(catalyst)

        current_catalysts_dict = [c.model_dump() for c in current_catalysts]
        # print(f"No. of Current catalysts JSON: {len(current_catalysts_json)}")

        human_prompt = STAGE2A_HUMAN_PROMPT.format(
            company_info=json.dumps(state.company_info.model_dump(), ensure_ascii=False),
            evidence=evidence,
            current_catalysts_json=json.dumps(current_catalysts_dict, ensure_ascii=False),
        )
        system_prompt = SystemMessage(content=STAGE2A_SYSTEM_MESSAGE[catalyst_type])
        messages = [system_prompt, HumanMessage(content=human_prompt)]

        # 1) call LLM
        llm_raw = run_llm(messages).content
        llm_dict = parse_json_from_llm(llm_raw)

        # 2)
        if llm_dict.get("action").lower() == "update":
            catalyst_id = llm_dict.get("catalyst_id")
            # find the matching existing catalyst
            matching_catalyst = next((c for c in current_catalysts if str(c.catalyst_id) == str(catalyst_id)), None)
            if not matching_catalyst:
                raise ValueError(f"Could not find matching catalyst to update with ID: {catalyst_id}")
            if matching_catalyst.date > chunk_date:
                # if existing catalyst date is more recent than chunk date, skip update
                llm_dict['action'] = "keep"
                matching_catalyst.state = "updated"
                matching_catalyst.is_valid = 1
            else:
                if llm_dict.get("catalyst_type").lower() == "keep":
                    pass
                else:
                    matching_catalyst.catalyst_type = llm_dict.get("catalyst_type")
                if llm_dict.get("impact_area").lower() == "keep":
                    pass
                else:
                    matching_catalyst.impact_area = ""
        elif llm_dict.get("action").lower() == "create":
            matching_catalyst = None
        elif llm_dict.get("action").lower() == "keep":
            catalyst_id = llm_dict.get("catalyst_id")
            matching_catalyst = next((c for c in current_catalysts if str(c.catalyst_id) == str(catalyst_id)), None)
            if matching_catalyst:
                matching_catalyst.state = "updated"
                matching_catalyst.is_valid = 1
            else:
                raise ValueError(f"Could not find matching catalyst to keep with ID: {catalyst_id}")
        else:
            raise ValueError(f"Unsupported action from LLM: {llm_dict.get('action')}")


        if matching_catalyst:
            cand = matching_catalyst
            matching_catalyst.evidence = evidence
            matching_catalyst.rationale = rationale

        # 4) write back to context
        ctx.candidate = cand
        ctx.action = llm_dict.get("action").lower() 
        ctx.current_catalysts = current_catalysts
        updated_contexts.append(ctx)

    return {"catalysts": updated_contexts}



def stage2b_node(state: CatalystSession) -> dict:
    updated_contexts = []
    for ctx in state.catalysts:  # ctx is a CatalystContext
        cand = ctx.candidate
        # skip if stage 1 said "no"
        if not cand or not cand.is_catalyst or ctx.action.lower() in ["skip", "keep"]:
            updated_contexts.append(ctx)
            continue

        catalyst_type = cand.catalyst_type
        retrieval_query = ctx.chunk.retrieval_query
        evidence = cand.evidence
        rationale = cand.rationale
        action = ctx.action
        target_catalyst = cand.model_dump()

        human_prompt = STAGE2B_HUMAN_PROMPT.format(
            company_info=json.dumps(state.company_info.model_dump(), ensure_ascii=False),
            action=action,
            evidence=evidence,
            target_catalyst_json=json.dumps(target_catalyst, ensure_ascii=False),
        )
        system_prompt = SystemMessage(content=STAGE2B_SYSTEM_MESSAGE[catalyst_type])
        messages = [system_prompt, HumanMessage(content=human_prompt)]

        # 1) call LLM
        llm_raw = run_llm(messages).content
        llm_dict = parse_json_from_llm(llm_raw)

        new_catalyst_flag = llm_dict.get("catalyst_id") is None \
                            or llm_dict.get("catalyst_id") == "" \
                            or llm_dict.get("catalyst_id") == "null" \
                            or llm_dict.get("catalyst_id") == "None"
        llm_dict["catalyst_id"] = str(uuid.uuid4()) if new_catalyst_flag else llm_dict.get("catalyst_id")

        # 2) VALIDATE with your Pydantic Catalyst
        #    this is the part that will raise if sentiment="positive" but model wants IntEnum
        stage2b_catalyst = Catalyst.model_validate({
            # keep stage1 info
            "is_catalyst": cand.is_catalyst,
            "rationale": rationale,
            "catalyst_type": catalyst_type,
            # stage2 info from llm
            **llm_dict,
        })

        # 4) write back to context
        ctx.candidate = stage2b_catalyst
        updated_contexts.append(ctx)

    return {"catalysts": updated_contexts}


def stage3_node(state: CatalystSession) -> dict:
    updated_contexts = []
    for ctx in state.catalysts:  # ctx is a CatalystContext
        cand = ctx.candidate
        content = ctx.chunk.content
        catalyst_type = ctx.chunk.catalyst_type

        if not cand or not cand.is_catalyst or ctx.action.lower() in ["skip", "keep"]:
            updated_contexts.append(ctx)
            continue

        human_prompt = STAGE3_HUMAN_PROMPT[catalyst_type](
            company_info=json.dumps(state.company_info.model_dump(), ensure_ascii=False),
            chunk_text=content,
            stage2_json_output=json.dumps(cand.model_dump(), ensure_ascii=False),
        )
        system_prompt = SystemMessage(content=STAGE3_SYSTEM_MESSAGE)
        messages = [system_prompt, HumanMessage(content=human_prompt)]

        # 1) call LLM
        llm_raw = run_llm(messages).content

        # 2) parse json
        llm_dict = parse_json_from_llm(llm_raw)
        is_valid = llm_dict.get("is_valid", 1)
        rejection_reason = llm_dict.get("rejection_reason", None)

        # if is_valid == 0:
        #     continue  # skip invalid catalysts

        cand.is_valid = is_valid
        cand.rejection_reason = rejection_reason

        # 3) VALIDATE with your Pydantic Catalyst
        #    this is the part that will raise if sentiment="positive" but model wants IntEnum
        stage3_catalyst = Catalyst.model_validate({
            **cand.model_dump()
        })

        # 4) write back to context
        ctx.candidate = stage3_catalyst
        updated_contexts.append(ctx)

    return {"catalysts": updated_contexts}

