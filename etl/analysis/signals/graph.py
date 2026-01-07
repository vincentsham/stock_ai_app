from langgraph.graph import StateGraph, START, END
from states import Signal
from nodes import is_signal_node
import json


def create_graph() -> StateGraph:
    """
    Creates a simple StateGraph for company profile summarization.
    The graph has a single node: summarize_company_profile.
    """
    graph = StateGraph(Signal)
    graph.add_node("is_signal_node", is_signal_node)
    graph.add_edge(START, "is_signal_node")
    graph.add_edge("is_signal_node", END)
    return graph

# Example usage (uncomment for testing):
if __name__ == "__main__":
    state = Signal(
        company_info={
            "tic": "AAPL",
            "company_name": "Apple Inc.",
            "industry": "Consumer Electronics",
            "sector": "Technology",
            "short_description": "Apple Inc. designs, manufactures, and markets consumer electronics, software, and services worldwide."
        },
        content=(
            "In its latest earnings call, Apple Inc. announced a 10% increase in quarterly revenue, driven by strong iPhone sales and growth in its services segment. "
            "The company also provided optimistic guidance for the next quarter, expecting continued growth despite supply chain challenges. "
            "Additionally, Apple revealed plans to launch new products, including updated MacBooks and a new line of AirPods, later this year."
        ),
        is_signal=0,
        reason=""
    )
    graph = create_graph()
    app = graph.compile()
    result = app.invoke(state)
    print(json.dumps(result, indent=2))



