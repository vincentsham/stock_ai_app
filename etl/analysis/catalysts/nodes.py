import uuid
from database.utils import execute_query
from langchain_openai import OpenAIEmbeddings
from typing import Dict, List, Literal, Optional, Union
from prompts import CATALYST_QUERIES, CATALYST_CONFIG, STAGE1_HUMAN_PROMPT, STAGE2_HUMAN_PROMPT, \
    STAGE1_SYSTEM_MESSAGE, STAGE2_SYSTEM_MESSAGE, STAGE3_HUMAN_PROMPT, STAGE3_SYSTEM_MESSAGE
from states import CatalystSession, Catalyst, Chunk, CompanyInfo
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from etl.utils import run_llm, parse_json_from_llm
import json
import os
from datetime import date, timedelta
import database.config

embedding_model = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL"))
MIN_COSINE_SIMILARITY = 0.35  # Minimum similarity threshold for retrieved chunks

# Helper function to build SQL query
def get_sql_query(source_type: str, tic: str, calendar_year: int,  
                  calendar_month: int, vec_str: str, top_k: int = 3) -> str:
    
    month = calendar_month
    # Two-month lookback window: from start of previous month to end of current month
    if month == 1:
        lookback_start = date(calendar_year - 1, 12, 1)
    else:
        lookback_start = date(calendar_year, month - 1, 1)

    if month == 12:
        target_month_end = date(calendar_year + 1, 1, 1) - timedelta(days=1)
    else:
        target_month_end = date(calendar_year, month + 1, 1) - timedelta(days=1)

    # Change: Replace '{vec_str}' with {vec_val} in the template to avoid confusion
    base_select = """
        SELECT
            c.tic, {date_col} AS date, c.chunk_id, c.event_id, c.chunk_no, c.chunk,
            1 - (e.embedding <=> '{vec_val}'::vector) AS cosine_sim,
            {source_meta}.source, {url_val} AS url, e.embedding, {source_meta}.raw_json_sha256
    """

    if source_type == "earnings_transcript":
        # Pass vec_val=vec_str here
        sql = base_select.format(
            date_col="t.earnings_date", 
            source_meta="t", 
            url_val="NULL",
            vec_val=vec_str
        ) + f"""
            FROM core.earnings_transcript_chunks AS c
            JOIN core.earnings_transcript_embeddings AS e ON c.chunk_id = e.chunk_id
            JOIN core.earnings_transcripts AS t ON c.event_id = t.event_id
            WHERE c.tic = '{tic}' 
                AND t.earnings_date >= '{lookback_start}'
                AND t.earnings_date <= '{target_month_end}'
                AND (1 - (e.embedding <=> '{vec_str}'::vector)) > {MIN_COSINE_SIMILARITY}
            ORDER BY cosine_sim DESC
            LIMIT {top_k};
        """

    elif source_type == "news":
        # Pass vec_val=vec_str here
        sql = base_select.format(
            date_col="c.published_at::DATE", 
            source_meta="n", 
            url_val="n.url",
            vec_val=vec_str
        ) + f"""
            FROM core.news_chunks AS c
            JOIN core.news_embeddings AS e ON c.chunk_id = e.chunk_id
            JOIN core.news AS n ON c.event_id = n.event_id
            WHERE c.tic = '{tic}' 
                AND c.published_at >= '{lookback_start}'
                AND c.published_at <= '{target_month_end}'
                AND (1 - (e.embedding <=> '{vec_str}'::vector)) > {MIN_COSINE_SIMILARITY}
            ORDER BY cosine_sim DESC
            LIMIT {top_k};
        """
    else:
        raise ValueError(f"Unsupported source_type: {source_type}") 

    return sql

# Retriever Node
def retriever_node(state: CatalystSession) -> Dict:
    """
    Synchronous execution of 36 vector searches.
    Deduplicates results by chunk_id and preserves the highest similarity score.
    """
    tic = state["company_info"].ticker
    # Configuration pulled from state or environment
    year = state["query_params"].calendar_year
    month = state["query_params"].calendar_month
    top_k = state["query_params"].top_k
    
    # Store unique chunks in a dictionary keyed by chunk_id
    deduplicated_chunks = {}

    # Iterate through all category keys in your CATALYST_QUERIES dictionary
    for category, queries in CATALYST_QUERIES.items():
        for query_text in queries:
            # 1. Generate the embedding for the query string
            # Replace 'get_embedding' with your actual embedding function/API call
            query_vec = embedding_model.embed_query(query_text)
            vec_str = "[" + ",".join(map(str, query_vec)) + "]"
            
            # 2. Search both News and Earnings Transcripts
            for s_type in ["news", "earnings_transcript"]:
                # Generate the SQL using your previously defined function
                sql = get_sql_query(
                    source_type=s_type,
                    tic=tic,
                    calendar_year=year,
                    calendar_month=month,
                    vec_str=vec_str,
                    top_k=top_k
                )
                
                # Execute the query
                results = execute_query(sql)
                if results is None or results.empty:
                    continue

                for _, row in results.iterrows():
                    chunk_id = str(row['chunk_id'])
                    
                    # Deduplication Logic: 
                    # If we see the same chunk again, keep the one with higher similarity
                    if chunk_id not in deduplicated_chunks or row['cosine_sim'] > deduplicated_chunks[chunk_id]['cosine_sim']:
                        deduplicated_chunks[chunk_id] = {
                            "chunk_id": str(row['chunk_id']),
                            "event_id": str(row['event_id']),    
                            "chunk_no": row['chunk_no'],
                            "source_type": s_type,
                            "date": row['date'].isoformat() if hasattr(row['date'], 'isoformat') else row['date'],
                            "content": row['chunk'],
                            "source": row['source'],
                            "url": row.get('url'), # News has URL, Transcripts usually don't
                            "raw_json_sha256": row['raw_json_sha256'],
                            "cosine_sim": row['cosine_sim']
                        }
    # print(f">>> Retrieved {len(deduplicated_chunks)} unique chunks for {tic} from both sources.")
    # 3. Finalize: Convert the dict back into a sorted list
    # Sorting by similarity ensures Stage 1 sees the "best" matches first
    final_raw_chunks = list(deduplicated_chunks.values())
    final_raw_chunks.sort(key=lambda x: (x['date'], x['cosine_sim']), reverse=True)

    # Return the update to the State
    return {"raw_chunks": final_raw_chunks}



def stage1_node(state: CatalystSession) -> Dict:
    """
    Refined Stage 1 logic using proper JSON structures and 
    mapping logic for integer-to-UUID resolution.
    """
    # 1. Access state data
    raw_chunks: List[Chunk] = state["raw_chunks"]
    if not raw_chunks:
        return {"uuid_groups": [], "errors": ["No chunks available for grouping."]}

    # 2. Structure Company Info for the LLM
    # state["company_info"] is a Pydantic model
    company_dict = state["company_info"].model_dump()
    company_info_json = json.dumps(company_dict, ensure_ascii=False)
    
    # Extract specific fields for the prompt template
    company_tic = state["company_info"].ticker
    company_name = state["company_info"].name

    # 3. Map Chunks to Temporary IDs and format content block
    # This keeps the prompt clean: LLM sees '1', we know it's 'uuid-123'
    temp_id_to_uuid = {i + 1: chunk['chunk_id'] for i, chunk in enumerate(raw_chunks)}
    
    content_block = ""
    for i, chunk in enumerate(raw_chunks):
        content_block += f"ID: {i+1}\nDate: {chunk['date']}\nContent: {chunk['content']}\n---\n"

    # 4. Construct the Prompt
    # Note: retrieval_query and catalyst_type can be pulled from state if stored
    human_prompt = STAGE1_HUMAN_PROMPT.format(
        company_info=company_info_json,
        company_tic=company_tic,
        company_name=company_name,
        id_mapping_block=content_block
    )
    
    messages = [
        SystemMessage(content=STAGE1_SYSTEM_MESSAGE),
        HumanMessage(content=human_prompt)
    ]

    # 5. Run LLM and Parse
    try:
        llm_raw = run_llm(messages).content
        # parse_json_from_llm handles markdown backticks and whitespace
        llm_groups = parse_json_from_llm(llm_raw) 
        
        # 6. Re-map Temporary IDs back to real UUIDs
        final_uuid_groups = []
        for group in llm_groups:
            # Only include IDs that actually exist in our mapping
            uuid_group = [temp_id_to_uuid[tid] for tid in group if tid in temp_id_to_uuid]
            if uuid_group:
                # Limit enforced here as a safety check (max 3 per group)
                final_uuid_groups.append(uuid_group[:3])

        # Limit to top 4 unique groups total as per your Stage 1 instructions
        return {"uuid_groups": final_uuid_groups[:4]}

    except Exception as e:
        return {"errors": [f"Stage 1 Error: {str(e)}"]}
    

def retrieve_existing_catalyst(tic: str, chunk_id: str) -> List[Dict]:
    """
    Fetch existing catalysts from core.catalyst_master filtered by ticker
    and where chunk_id is contained in the row's chunk_ids array.
    Returns the most recent match.
    """
    sql = f"""
        SELECT catalyst_id::TEXT, tic, date, catalyst_type, title, summary,
               sentiment, impact_area, magnitude, time_horizon, chunk_ids
        FROM core.catalyst_master
        WHERE tic = '{tic}'
          AND '{chunk_id}' = ANY(chunk_ids)
        ORDER BY date DESC
        LIMIT 1;
    """
    df = execute_query(sql)
    if df is None or df.empty:
        return []
    return df.to_dict(orient="records")

def stage2_node(state: CatalystSession) -> Dict:
    """
    Iterates through uuid_groups, synthesizes each into a CatalystRecord,
    and handles reconciliation with existing catalysts.
    """
    uuid_groups = state["uuid_groups"]
    raw_chunks = state["raw_chunks"]
    company_info = state["company_info"]

    # 1. Index raw_chunks by composite ID (event_id:chunk_id) for fast lookup
    chunk_map = {chunk['chunk_id']: chunk for chunk in raw_chunks}
    
    new_catalysts = []
    existing_catalysts = []
    node_errors = []

    # 2. Process each group (Max 4 groups from Stage 1)
    for group_uuids in uuid_groups:
        try:
            # Gather the 1-3 chunks for this specific event, sorted oldest-first for narrative flow
            group_chunks = [chunk_map[uid] for uid in group_uuids if uid in chunk_map]
            group_chunks.sort(key=lambda x: (x['date'], x['cosine_sim']), reverse=False)

            # 3. Retrieve existing catalyst by iterating through chunks until a match is found
            matched_existing = None
            for chunk in group_chunks:
                existing = retrieve_existing_catalyst(
                    tic=company_info.ticker,
                    chunk_id=str(chunk['chunk_id'])
                )
                if existing:
                    matched_existing = existing[0]
                    break

            # Skip if all group chunks are already known to this catalyst (no new evidence)
            if matched_existing:
                existing_chunk_ids = set(matched_existing.get('chunk_ids', []))
                if set(group_uuids).issubset(existing_chunk_ids):
                    # print(f"  ⏭️  Skipping group — all chunks already in catalyst: {matched_existing['catalyst_id']}")
                    continue

            existing_catalysts.append(matched_existing)

            # Format evidence block for the prompt
            evidence_text = ""
            for chunk in group_chunks:
                evidence_text += f"Source ID: {chunk['chunk_id']}\nDate: {chunk['date']}\nContent: {chunk['content']}\n---\n"

            # 4. Build the Analyst Prompt with existing catalyst context
            human_prompt = STAGE2_HUMAN_PROMPT.format(
                company_info=company_info.model_dump_json(),
                existing_catalyst_json=json.dumps(matched_existing if matched_existing else {}, default=str),
                chunks_for_this_group=evidence_text
            )

            messages = [
                SystemMessage(content=STAGE2_SYSTEM_MESSAGE),
                HumanMessage(content=human_prompt)
            ]

            # 5. Run LLM and Parse into Pydantic Model
            llm_raw = run_llm(messages).content
            catalyst_json = parse_json_from_llm(llm_raw)
            
            # This validation step ensures the LLM didn't hallucinate a tag 
            # outside of your Literal ImpactArea or CatalystType
            record = Catalyst(**catalyst_json)

            # Enforce 1 citation per chunk_id (keep first, drop duplicates)
            seen_chunks = set()
            deduped = []
            for c in record.citations:
                if c.chunk_id not in seen_chunks:
                    seen_chunks.add(c.chunk_id)
                    deduped.append(c)
            record.citations = deduped

            new_catalysts.append(record)

        except Exception as e:
            node_errors.append(f"Failed synthesizing group {group_uuids}: {str(e)}")

    # 5. Return the additions to the final_catalysts list
    # Annotated[List, operator.add] in states.py handles the append automatically
    return {
        "final_catalysts": new_catalysts,
        "existing_catalysts": existing_catalysts,
        "errors": node_errors
    }

def stage3_node(state: CatalystSession) -> Dict:
    """
    Validates synthesized catalysts against their source chunks.
    Uses the proper STAGE3 prompts from prompts.py and cross-references
    citations against original raw_chunks.
    
    Returns validated catalysts via set_reducer (overwrites, not appends)
    to avoid duplicating the Stage 2 output.
    """
    catalysts: List[Catalyst] = state["final_catalysts"]
    raw_chunks = state["raw_chunks"]
    company_info = state["company_info"]
    existing_catalysts = state.get("existing_catalysts", [])
    new_errors = []

    # Build lookup: catalyst_id -> existing catalyst record (for sentiment check)
    existing_map = {}
    for ec in existing_catalysts:
        if ec and isinstance(ec, dict) and 'catalyst_id' in ec:
            existing_map[ec['catalyst_id']] = ec

    # Build a lookup from composite ID -> chunk content for source verification
    chunk_map = {chunk['chunk_id']: chunk for chunk in raw_chunks}

    for record in catalysts:
        try:
            # 1. Gather source text using citation chunk IDs
            source_text_parts = []
            for cid in [c.chunk_id for c in record.citations]:
                chunk = chunk_map.get(cid)
                if chunk:
                    source_text_parts.append(
                        f"[ID: {cid}] [Date: {chunk['date']}] \"{chunk['content']}\""
                    )
            source_text_block = "\n".join(source_text_parts)

            # 2. Build the Stage 2 output JSON for the prompt
            stage2_json = json.dumps(record.model_dump(), ensure_ascii=False, default=str)

            # 3. Construct the prompt using the designed templates
            # Look up definition from CATALYST_CONFIG, fallback to formatted name
            definition = CATALYST_CONFIG.get(record.catalyst_type, {}).get(
                "definition", record.catalyst_type.replace("_", " ").title()
            )
            # Resolve prior sentiment for update actions
            prior_sentiment_str = "N/A (new catalyst)"
            if record.action == "update" and record.catalyst_id:
                prior = existing_map.get(record.catalyst_id)
                if prior:
                    prior_sentiment_str = str(prior.get('sentiment', 'unknown'))

            human_prompt = STAGE3_HUMAN_PROMPT.format(
                catalyst_type=record.catalyst_type,
                definition=definition,
                company_info=company_info.model_dump_json(),
                source_text_chunks=source_text_block,
                stage2_json_output=stage2_json,
                prior_sentiment=prior_sentiment_str
            )

            messages = [
                SystemMessage(content=STAGE3_SYSTEM_MESSAGE),
                HumanMessage(content=human_prompt)
            ]

            # 4. Run Validation LLM
            llm_raw = run_llm(messages).content
            val_result = parse_json_from_llm(llm_raw)

            # 5. Update the record — LLM returns is_valid: 0|1
            is_valid = val_result.get("is_valid", 0)
            record.is_valid = bool(is_valid)
            record.rejection_reason = val_result.get("rejection_reason", "")

        except Exception as e:
            error_msg = f"Validation failed for '{record.title[:30]}...': {str(e)}"
            new_errors.append(error_msg)
            record.is_valid = False
            record.rejection_reason = f"System Error: {str(e)}"

    # Use set_reducer semantics: return the full validated list to REPLACE stage 2 output
    # This avoids doubling catalysts via the add_reducer
    return {
        "final_catalysts": catalysts, 
        "errors": new_errors 
    }