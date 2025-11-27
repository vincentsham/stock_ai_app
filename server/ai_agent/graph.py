from langgraph.graph import add_messages, StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessageChunk, ToolMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from tools import get_stock_info_yfinance, tavily_search_results_json
from uuid import uuid4
import json
from fastapi import APIRouter
from typing import Optional, TypedDict, Annotated, AsyncGenerator

# Initialize router
tools_router = APIRouter()

# Initialize memory saver for checkpointing
memory = MemorySaver()

# Update State to inherit from TypedDict and define its structure
class State(TypedDict):
    """
    Represents the state of the graph.

    Attributes:
        messages (list): A list of messages to be processed by the graph.
    """
    messages: Annotated[list, add_messages]

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(
    tools=[tavily_search_results_json, get_stock_info_yfinance]
)

def graph() -> StateGraph:
    """
    Creates and compiles a StateGraph instance.

    Returns:
        StateGraph: The compiled state graph.
    """
    graph_builder = StateGraph(State)

    async def model(state: State) -> dict:
        """
        Processes the state using the language model with tools.

        Args:
            state (State): The current state of the graph.

        Returns:
            dict: The updated state with the model's response.
        """
        system_message = HumanMessage(content=(
            "You are an AI assistant specialized in stock analysis and general information retrieval. "
            "If the user input is a stock ticker (e.g., AAPL, TSLA), use the `get_stock_info_yfinance` tool to fetch stock information. "
            "For other queries, use the `tavily_search_results_json`."
        ))
        messages = [system_message] + state["messages"]
        result = await llm_with_tools.ainvoke(messages)
        return {"messages": [result]}

    async def tools_router(state: State) -> str:
        """
        Determines the next node based on the presence of tool calls.

        Args:
            state (State): The current state of the graph.

        Returns:
            str: The next node to transition to.
        """
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
            return "tool_node"
        else:
            return END

    async def tool_node(state: State) -> dict:
        """
        Processes tool calls and generates tool messages.

        Args:
            state (State): The current state of the graph.

        Returns:
            dict: The updated state with tool messages.
        """
        tool_calls = state["messages"][-1].tool_calls
        tool_messages = []
        tools = {
            "tavily_search_results_json": tavily_search_results_json,
            "get_stock_info_yfinance": get_stock_info_yfinance,
        }

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            # Dynamically call the tool function using the tools dictionary
            tool_function = tools.get(tool_name)
            if not tool_function:
                raise ValueError(f"Tool {tool_name} not found in tools dictionary.")

            tool_result = await tool_function.ainvoke(tool_args)
            tool_message = ToolMessage(
                tool_call_id=tool_id,
                name=tool_name,
                content=json.dumps({"result": str(tool_result), "args": tool_args}),
            )
            tool_messages.append(tool_message)
        return {"messages": tool_messages}

    graph_builder.add_node("model", model)
    graph_builder.add_node("tool_node", tool_node)
    graph_builder.set_entry_point("model")
    graph_builder.add_conditional_edges("model", tools_router)
    graph_builder.add_edge("tool_node", "model")

    return graph_builder.compile(checkpointer=memory)

# Initialize the graph
lang_graph = graph()

# Function to serialize AIMessageChunk
def serialise_ai_message_chunk(chunk: AIMessageChunk):
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk).__name__} is not correctly formatted for serialisation"
        )


# Enhance the LLM prompt to prioritize get_stock_info for stock tickers
async def generate_chat_responses(message: str, checkpoint_id: Optional[str] = None) -> AsyncGenerator[str, None]:
    """
    Generates chat responses based on the input message and checkpoint ID.

    Args:
        message (str): The input message to process.
        checkpoint_id (Optional[str]): The checkpoint ID for the conversation.

    Yields:
        str: The generated chat responses in a streaming format.
    """
    is_new_conversation = checkpoint_id is None
    if is_new_conversation:
        new_checkpoint_id = str(uuid4())
        config = {"configurable": {"thread_id": new_checkpoint_id}}
        events = lang_graph.astream_events(  # Use precompiled lang_graph
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )
        yield f"data: {{\"type\": \"checkpoint\", \"checkpoint_id\": \"{new_checkpoint_id}\"}}\n\n"
    else:
        config = {"configurable": {"thread_id": checkpoint_id}}
        events = lang_graph.astream_events(  # Use precompiled lang_graph
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )
    log_file = "tests/events.log"
    with open(log_file, "w") as f:
        async for event in events:
            f.write(str(event) + "\n")  # Serialize event to JSON string before writing

            event_type = event["event"]
            if event_type == "on_chat_model_stream":
                chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
                safe_content = chunk_content.replace("'", "\\'").replace("\n", "\\n")
                yield f"data: {{\"type\": \"content\", \"content\": \"{safe_content}\"}}\n\n"
 
            elif event_type == "on_tool_start":
                yield f"data: {{\"type\": \"tool_call\", \"tool_name\": \"{event['name']}\", \"tool_input\": \"{event['data']['input']}\"}}\n\n"


        yield f"data: {{\"type\": \"end\"}}\n\n"
