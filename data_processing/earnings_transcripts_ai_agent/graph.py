from langgraph.graph import START, END
from langgraph.graph import StateGraph
from langgraph.types import Command
from typing import Literal
import time  # Import the time module for timing
from nodes import (
    retriever_past_analysis, retriever_future_analysis, retriever_risk_analysis,
    past_analysis, future_analysis, risk_analysis
)
from states import merged_state_factory, MergedState, PastState, FutureState, RiskState




# # Update the create_graph function to use StateGraph with parallel branches
def create_past_graph() -> StateGraph:
    graph = StateGraph(PastState)

    graph.add_node("retriever_past", retriever_past_analysis)
    graph.add_node("past_analysis", past_analysis)
    graph.add_edge(START, "retriever_past")
    graph.add_edge("retriever_past", "past_analysis")
    graph.add_edge("past_analysis", END)

    return graph

def create_future_graph() -> StateGraph:
    graph = StateGraph(FutureState)

    graph.add_node("retriever_future", retriever_future_analysis)
    graph.add_node("future_analysis", future_analysis)
    graph.add_edge(START, "retriever_future")
    graph.add_edge("retriever_future", "future_analysis")
    graph.add_edge("future_analysis", END)

    return graph

def create_risk_graph() -> StateGraph:
    graph = StateGraph(RiskState)

    graph.add_node("retriever_risk", retriever_risk_analysis)
    graph.add_node("risk_analysis", risk_analysis)
    graph.add_edge(START, "retriever_risk")
    graph.add_edge("retriever_risk", "risk_analysis")
    graph.add_edge("risk_analysis", END)

    return graph



def create_graph() -> StateGraph:

    def past_node(state: MergedState) -> dict:
        response = create_past_graph().compile().invoke(state.past)
        return {"past": response}

    def future_node(state: MergedState) -> dict:
        response = create_future_graph().compile().invoke(state.future)
        return {"future": response}

    def risk_node(state: MergedState) -> dict:
        response = create_risk_graph().compile().invoke(state.risk)
        return {"risk": response}

    def fanout(_: dict) -> Command[Literal["past_node", "future_node", "risk_node"]]:
        # Send execution to all three retriever nodes concurrently
        return Command(goto=["past_node", "future_node", "risk_node"])

    graph = StateGraph(MergedState)

    # fan-out trigger
    graph.add_node("fanout", fanout)

    # branch nodes
    graph.add_node("past_node", past_node)
    graph.add_node("future_node", future_node)
    graph.add_node("risk_node", risk_node)


    # wiring
    graph.add_edge(START, "fanout")
    graph.add_edge("fanout", "past_node")
    graph.add_edge("fanout", "future_node")
    graph.add_edge("fanout", "risk_node")

    # all three analysis branches converge to merge_results
    graph.add_edge("past_node", END)
    graph.add_edge("future_node", END)
    graph.add_edge("risk_node", END)

    return graph



if __name__ == "__main__":
    graph = create_graph()
    app = graph.compile()
    start_time = time.time()
    # Example: initialize state for AAPL Q3 2025
    state = merged_state_factory(
                tic="AAPL",
                company_name="Apple Inc.",
                industry="Technology",
                sector="Consumer Electronics",
                company_description="Apple Inc. is a leading technology company known for its innovative products and services.",
                fiscal_year=2025,
                fiscal_quarter=2,
                earnings_date="2025-10-28"
        )
    
    result = app.invoke(state)
    print("===========past===============")
    print(result['past'])
    print("===========future===============")
    print(result['future'])
    print("===========risk===============")
    print(result['risk'])
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")