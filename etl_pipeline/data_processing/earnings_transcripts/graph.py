from langgraph.graph import START, END
from langgraph.graph import StateGraph
from langgraph.types import Command
from typing import Literal
import time  # Import the time module for timing
from nodes import (
    past_retriever_node, future_retriever_node, risk_retriever_node,
    past_analysis_node, future_analysis_node, risk_analysis_node,
    risk_response_analysis_node, risk_response_retriever_node,
    risk_response_queries_powered_by_llm
)
from states import merged_state_factory, MergedState, PastState, FutureState, RiskState




def create_graph() -> StateGraph:

    def fanout(_: dict) -> Command[Literal["past_retriever_node", 
                                           "future_retriever_node", 
                                           "risk_retriever_node"]]:
        # Send execution to all three retriever nodes concurrently
        return Command(goto=["past_retriever_node", 
                             "future_retriever_node", 
                             "risk_retriever_node"])

    graph = StateGraph(MergedState)

    # fan-out trigger
    graph.add_node("fanout", fanout)

    # branch nodes
    graph.add_node("past_retriever_node", past_retriever_node)
    graph.add_node("future_retriever_node", future_retriever_node)
    graph.add_node("risk_retriever_node", risk_retriever_node)

    graph.add_node("past_analysis_node", past_analysis_node)
    graph.add_node("future_analysis_node", future_analysis_node)
    graph.add_node("risk_analysis_node", risk_analysis_node)

    graph.add_node("risk_response_queries_powered_by_llm", risk_response_queries_powered_by_llm)
    graph.add_node("risk_response_retriever_node", risk_response_retriever_node)
    graph.add_node("risk_response_analysis_node", risk_response_analysis_node)

    # wiring
    graph.add_edge(START, "fanout")
    graph.add_edge("fanout", "past_retriever_node")
    graph.add_edge("fanout", "future_retriever_node")
    graph.add_edge("fanout", "risk_retriever_node")

    graph.add_edge("past_retriever_node", "past_analysis_node")
    graph.add_edge("future_retriever_node", "future_analysis_node")
    graph.add_edge("risk_retriever_node", "risk_analysis_node")

    graph.add_edge("risk_analysis_node", "risk_response_queries_powered_by_llm")
    graph.add_edge("risk_response_queries_powered_by_llm", "risk_response_retriever_node")
    graph.add_edge("risk_response_retriever_node", "risk_response_analysis_node")

    # all three analysis branches converge to merge_results
    graph.add_edge("past_analysis_node", END)
    graph.add_edge("future_analysis_node", END)
    graph.add_edge("risk_response_analysis_node", END)

    return graph



if __name__ == "__main__":
    graph = create_graph()
    app = graph.compile()
    start_time = time.time()
    # Example: initialize state for AAPL Q2 2025
    # state = merged_state_factory(
    #             tic="AAPL",
    #             company_name="Apple Inc.",
    #             industry="Technology",
    #             sector="Consumer Electronics",
    #             company_description="Apple Inc. is a leading technology company known for its innovative products and services.",
    #             calendar_year=2025,
    #             calendar_quarter=2,
    #             earnings_date="2025-10-28"
    #     )

    # Example: initialize state for NVDA Q2 2025
    # state = merged_state_factory(
    #             tic="NVDA",
    #             company_name="NVIDIA Corporation",
    #             industry="Semiconductors",
    #             sector="Technology",
    #             company_description="NVIDIA Corporation is a global leader in AI computing.",
    #             calendar_year=2025,
    #             calendar_quarter=2,
    #             earnings_date="2025-08-15"
    #         )

    # Example: initialize state for TSLA Q2 2025
    state = merged_state_factory(
                tic="TSLA",
                company_name="Tesla, Inc.",
                industry="Automotive",
                sector="Consumer Discretionary",
                company_description="Tesla, Inc. is a leading electric vehicle and clean energy company.",
                calendar_year=2025,
                calendar_quarter=2,
                earnings_date="2025-07-24"
            )

    # import pdb; pdb.set_trace()
    result = app.invoke(state)

    print(result)
    print("===========past===============")
    print(result['past_analysis'])
    print("===========future===============")
    print(result['future_analysis'])
    print("===========risk===============")
    print(result['risk_analysis'])
    print("===========risk response===============")
    print(result['risk_response_analysis'])
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")