from state import News
from server.ai_agent.news_ai_agent.old_prompts import STAGE1_PROMPT, STAGE2_PROMPT, STAGE1_SYSTEM_MESSAGE, STAGE2_SYSTEM_MESSAGE
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize the LLM model with structured output
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, response_format={"type": "json_object"})

def run_llm(prompt: str, system_message: str) -> dict:
    """Interact with the LLM using a system message and a human prompt."""
    try:
        system_prompt = SystemMessage(content=system_message)
        human_prompt = HumanMessage(content=prompt)

        messages = [system_prompt, human_prompt]
        response = llm.invoke(messages)
        return response
    except Exception as e:
        # Raise an exception to be handled by the graph or caller
        raise RuntimeError(f"LLM invocation failed: {e}")

def stage1(state: News) -> dict:
    """Run Stage 1 LLM classifier.
    Description: This stage classifies the news into a category and event type based on the headline and summary.
    Input: News (headline, summary, etc.)
    Output: {"category": <str>, "event_type": <str>} 
    """
    prompt = STAGE1_PROMPT.format(
        headline=state.headline,
        summary=state.summary,
        ticker=state.ticker,
        publisher=state.publisher,
        publish_date=state.publish_date
    )

    response = json.loads(run_llm(prompt, STAGE1_SYSTEM_MESSAGE).content)
    category = response.get("category")
    event_type = response.get("event_type")
    return {
        "category": category, 
        "event_type": event_type
    }

def stage2(state: News) -> dict:
    """Run Stage 2 LLM analysis using Stage 1 outputs.
    Description: This stage analyzes the impact, duration, and sentiment of the news based on Stage 1 outputs.
    Input: News + Stage 1 results
    Output: {
        "time_horizon": <str>,
        "duration": <str>,
        "impact_magnitude": <str>,
        "affected_dimensions": <list>,
        "sentiment": <str>
    }
    """
    prompt = STAGE2_PROMPT.format(
        headline=state.headline,
        summary=state.summary,
        ticker=state.ticker,
        publisher=state.publisher,
        publish_date=state.publish_date,
        category=state.category,
        event_type=state.event_type
    )
    response = json.loads(run_llm(prompt, STAGE2_SYSTEM_MESSAGE).content)
    time_horizon = response.get("time_horizon")
    duration = response.get("duration")
    impact_magnitude = response.get("impact_magnitude")
    affected_dimensions = response.get("affected_dimensions")
    sentiment = response.get("sentiment")
    return {
        "time_horizon": time_horizon,
        "duration": duration,
        "impact_magnitude": impact_magnitude,
        "affected_dimensions": affected_dimensions,
        "sentiment": sentiment
    }


if __name__ == "__main__":
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    print(llm.invoke("Hello"))