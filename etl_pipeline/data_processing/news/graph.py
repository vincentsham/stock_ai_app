from langgraph.graph import START, END
from langgraph.graph import StateGraph
from nodes import stage1, stage2
from states import News
import time  # Import the time module for timing


# Update the create_graph function to use StateGraph
def create_graph() -> StateGraph:
    """Create a LangGraph pipeline for news analysis using StateGraph."""
    graph = StateGraph(News)
    STAGE1 = "stage1"
    STAGE2 = "stage2"


    # Add Stage 1 node
    graph.add_node(STAGE1, stage1)
    graph.add_edge(START, STAGE1)

    # Conditional edge based on Stage 1 output
    def is_noise(state: News) -> str:
        if state.category == "noise":
            return END
        return STAGE2

    graph.add_conditional_edges(STAGE1, is_noise)

    # Add Stage 2 node
    graph.add_node(STAGE2, stage2)


    # Final end node
    graph.add_edge(STAGE2, END)

    return graph
