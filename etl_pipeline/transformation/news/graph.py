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

if __name__ == "__main__":
    start_time = time.time()  # Record the start time
    graph = create_graph()
    app = graph.compile()

    # Sample records for testing
    sample_records = [
        News(
            tic="AAPL",
            company_name="Apple Inc.",
            industry="Technology",
            sector="Consumer Electronics",
            company_description="Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
            headline="Apple Releases New iPhone Model",
            summary="Apple has announced the release of its latest iPhone model, featuring advanced technology and improved performance.",
            url="https://example.com/apple-iphone-release",
            publisher="Tech News Daily",
            published_at="2024-01-01T10:00:00Z"
        ),
        News(
            tic="TSLA",
            company_name="Tesla, Inc.",
            industry="Automotive",
            sector="Electric Vehicles",
            company_description="Tesla, Inc. designs, develops, manufactures, and sells electric vehicles and energy generation and storage systems.",
            headline="Tesla Unveils New Electric Truck",
            summary="Tesla has unveiled its new electric truck, which promises to revolutionize the trucking industry with its innovative design and capabilities.",
            url="https://example.com/tesla-electric-truck",
            publisher="Auto World",
            published_at="2024-01-02T12:00:00Z"
        )
    ]
    for record in sample_records:
        final_state = app.invoke(record)
        print(final_state)

    end_time = time.time()  # Record the end time
    print(f"Graph created in {end_time - start_time:.6f} seconds")  # Print the time taken

