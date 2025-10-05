from langgraph.graph import START, END
from langgraph.graph import StateGraph
from nodes import stage1, stage2
from state import News
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
    import pandas as pd
    from server.database.utils import connect_to_db  # Updated import to reflect package structure

    # Connect to the database
    with connect_to_db() as conn:
        query = "SELECT * FROM news WHERE tic = 'NVDA' LIMIT 100;"  
        df = pd.read_sql_query(query, conn)

    # Construct states from the retrieved records
    states = [
        News(
            headline=row['title'],
            summary=row['content'],
            ticker=row['tic'],
            publisher=row['publisher'],
            publish_date=str(row['published_date'])  # Convert to string
        )
        for _, row in df.iterrows()
    ]

    # Run the graph for each state
    graph = create_graph()
    app = graph.compile()

    start_time = time.time()  # Start timing
    
    no_major_news = 0
    for state in states:
        final_state = app.invoke(state)
        print("===============================================")
        if "impact_magnitude" in final_state and final_state["impact_magnitude"] == "major":
            print("************************************")
            no_major_news += 1
        print("Final state:", final_state)

    end_time = time.time()  # End timing
    print(f"Processed 10 records in {end_time - start_time:.2f} seconds.")
    print(f"Total number of major news is {no_major_news}.")