from langgraph.graph import START, END
from langgraph.graph import StateGraph
from langgraph.types import Command
from typing import Literal
import time  # Import the time module for timing
from nodes import (retriever_node, stage1_node, stage2_node,
                   current_catalysts_retriever_node)
from states import CatalystSession, catalyst_session_factory




def create_graph() -> StateGraph:

    graph = StateGraph(CatalystSession)

    # Add nodes
    graph.add_node("retriever_node", retriever_node)
    graph.add_node("current_catalysts_retriever_node", current_catalysts_retriever_node)
    graph.add_node("stage1_node", stage1_node)
    graph.add_node("stage2_node", stage2_node)

    def no_retrieval(state: CatalystSession) -> str:
        if len(state.catalysts) == 0:
            return END
        else:
            return "current_catalysts_retriever_node"

    # wiring
    graph.add_edge(START, "retriever_node")
    graph.add_conditional_edges("retriever_node", no_retrieval)
    graph.add_edge("current_catalysts_retriever_node", "stage1_node")
    graph.add_edge("stage1_node", "stage2_node")
    graph.add_edge("stage2_node", END)

    return graph



if __name__ == "__main__":
    state = catalyst_session_factory(
        tic="AAPL",
        company_name="Apple Inc.",
        industry="Technology Hardware, Storage & Peripherals",
        sector="Information Technology",
        company_description="Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
        calendar_year=2025,
        calendar_month=10,
        source_type="news",
        catalyst_type="product_initiative",
        top_k=1,
    )
    graph = create_graph()
    app = graph.compile()
    start_time = time.time()
    result = app.invoke(state)
    end_time = time.time()
    print(f"Execution Time: {end_time - start_time} seconds")
    print("===========================================================\n")
    print(result)
    print("\n===========================================================\n")
    for catalyst in result.get("catalysts"):
        print("Score:", catalyst.chunk.score, "Date:", catalyst.chunk.date)
        print("\n")
        print("Content:", catalyst.chunk.content)
        print("\n")
        print("Is Catalyst:", catalyst.candidate.is_catalyst)
        print("Rationale:", catalyst.candidate.rationale)
        print("\n===")
        print("Catalyst:", catalyst.candidate)
        print("\n-----------------------------------------------------------\n")

