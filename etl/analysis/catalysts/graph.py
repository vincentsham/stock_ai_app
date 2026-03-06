import time
from typing import Dict, List, Literal
from langgraph.graph import START, END, StateGraph

# Nodes and State imports
from states import CatalystSession, Catalyst, catalyst_session_factory
from nodes import (
    retriever_node, 
    stage1_node, 
    stage2_node, 
    stage3_node
)

# --- Routing Logic ---

def should_continue(state: CatalystSession) -> Literal["stage1_node", END]:
    """
    Check if the retriever found any data. 
    If raw_chunks is empty, we stop to save tokens and time.
    """
    if not state.get("raw_chunks"):
        print(f">>> No data found for {state['company_info'].ticker}. Exiting graph.")
        return END
    return "stage1_node"

# --- Graph Construction ---

def create_graph() -> StateGraph:
    graph = StateGraph(CatalystSession)

    # Define Nodes
    graph.add_node("retriever_node", retriever_node)
    graph.add_node("stage1_node", stage1_node)
    graph.add_node("stage2_node", stage2_node)
    graph.add_node("stage3_node", stage3_node)

    # Define Edges
    graph.add_edge(START, "retriever_node")
    
    # Use the conditional gate after retrieval
    graph.add_conditional_edges(
        "retriever_node",
        should_continue
    )

    graph.add_edge("stage1_node", "stage2_node")
    graph.add_edge("stage2_node", "stage3_node")
    graph.add_edge("stage3_node", END)

    return graph

# --- Main Execution Loop ---

if __name__ == "__main__":
    # 1. Create the session using your factory (now imported from states.py)
    # state = catalyst_session_factory(
    #     tic="AAPL",
    #     company_name="Apple Inc.",
    #     industry="Technology Hardware",
    #     sector="Information Technology",
    #     company_description="Apple designs personal computers and smartphones.",
    #     calendar_year=2026,
    #     calendar_month=1,
    #     # catalyst_type and top_k are handled by the factory
    # )
    # state = catalyst_session_factory(
    #     tic="TSLA",
    #     company_name="Tesla, Inc.",
    #     industry="Automobile Manufacturers",
    #     sector="Consumer Discretionary",
    #     company_description="Tesla designs and manufactures electric vehicles and energy storage systems.",
    #     calendar_year=2026,
    #     calendar_month=1,
    #     # catalyst_type and top_k are handled by the factory
    # )
    state = catalyst_session_factory(
        tic="NVDA",
        company_name="NVIDIA Corporation",
        industry="Semiconductors",
        sector="Information Technology",
        company_description="NVIDIA designs GPUs and AI computing platforms.",
        calendar_year=2026,
        calendar_month=1,
        # catalyst_type and top_k are handled by the factory
    )
    # 2. Compile the Graph
    graph = create_graph()
    app = graph.compile()
    
    # 3. Invoke and Time the Run
    print(f"🚀 Processing {state['company_info'].ticker}...")
    start_t = time.time()
    result = app.invoke(state)
    elapsed = time.time() - start_t

    # 4. Final Reporting
    print(f"\n✅ Done in {elapsed:.2f}s")
    print("=" * 60)

    # Access the final_catalysts list from the state
    catalysts: List[Catalyst] = result.get("final_catalysts", [])
    
    for i, cat in enumerate(catalysts):
        status = "PASS" if cat.is_valid else "FAIL"
        print(f"[{status}] {cat.title}")
        print(f"Impact: {cat.impact_area} | Sentiment: {cat.sentiment}")
        print(f"Summary: {cat.summary}")
        print(f"Citations: {len(cat.citations)} quote(s) found.")
        if not cat.is_valid:
            print(f"Rejection Reason: {cat.rejection_reason}")
        print("-" * 20)

    if result.get("errors"):
        print(f"\n⚠️ Logged Errors: {result['errors']}")
    print("\n" + "=" * 60)
    print("result", result)