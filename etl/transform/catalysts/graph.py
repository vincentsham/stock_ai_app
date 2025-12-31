from langgraph.graph import START, END
from langgraph.graph import StateGraph
from langgraph.types import Command
from typing import Literal
import time  # Import the time module for timing
from nodes import (retriever_node, stage1_node, stage2a_node, stage2b_node, stage3_node)
from states import CatalystSession, catalyst_session_factory




def create_graph() -> StateGraph:

    graph = StateGraph(CatalystSession)

    # Add nodes
    graph.add_node("retriever_node", retriever_node)
    graph.add_node("stage1_node", stage1_node)
    graph.add_node("stage2a_node", stage2a_node)
    graph.add_node("stage2b_node", stage2b_node)
    graph.add_node("stage3_node", stage3_node)

    def no_retrieval(state: CatalystSession) -> str:
        if len(state.catalysts) == 0:
            return END
        else:
            return "current_catalysts_retriever_node"

    # wiring
    graph.add_edge(START, "retriever_node")
    graph.add_edge("retriever_node", "stage1_node")
    graph.add_edge("stage1_node", "stage2a_node")
    graph.add_edge("stage2a_node", "stage2b_node")
    graph.add_edge("stage2b_node", "stage3_node")
    graph.add_edge("stage3_node", END)

    return graph



if __name__ == "__main__":
    state = catalyst_session_factory(
        tic="AAPL",
        company_name="Apple Inc.",
        industry="Technology Hardware, Storage & Peripherals",
        sector="Information Technology",
        company_description="Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
        calendar_year=2024,
        calendar_quarter=4,
        source_type="earnings_transcript",
        catalyst_type="partnership_deal",
        top_k=1,
    )
    graph = create_graph()
    app = graph.compile()
    start_time = time.time()
    result = app.invoke(state)
    end_time = time.time()
    # import pdb; pdb.set_trace()
    print(f"Execution Time: {end_time - start_time} seconds")
    print("===========================================================\n")
    print(result)
    print("\n===========================================================\n")

    n_skip = 0
    n_keep = 0
    n_create = 0
    n_update = 0
    n_valid = 0
    n = 0   
    for catalyst in result.get("catalysts", []):
        n_skip += 1 if catalyst.action == "skip" else 0
        n_keep += 1 if catalyst.action == "keep" else 0
        n_create += 1 if catalyst.action == "create" else 0
        n_update += 1 if catalyst.action == "update" else 0
        n_valid += 1 if catalyst.candidate.is_valid == 1 else 0
        n += 1
        # import pdb; pdb.set_trace()
        print("Score:", catalyst.chunk.score, "Date:", catalyst.chunk.date)
        print("\n")
        print("Content:", catalyst.chunk.content)
        print("\n")
        print("Is Catalyst:", catalyst.candidate.is_catalyst)
        print("Rationale:", catalyst.candidate.rationale)
        print("\n===")
        print("Action:", catalyst.action)
        print("\n===")
        print("Catalyst ID:", catalyst.candidate.catalyst_id)
        print("Catalyst:", catalyst.candidate)
        print("\n-----------------------------------------------------------\n")
        print(f"Actions so far - Skip: {n_skip}, Keep: {n_keep}, Create: {n_create}, Update: {n_update}, Valid: {n_valid}, Total Processed Catalysts: {n}")

