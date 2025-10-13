from states import News
from prompts import STAGE1_PROMPT, STAGE2_PROMPT, STAGE1_SYSTEM_MESSAGE, STAGE2_SYSTEM_MESSAGE
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from etl_pipeline.utils import run_llm
from dotenv import load_dotenv
import json



def stage1(state: News) -> dict:
    """Run Stage 1 LLM classifier.
    Description: This stage classifies the news into a category and event type based on the headline and summary.
    Input: News (headline, summary, etc.)
    Output: {"category": <str>, "event_type": <str>} 
    """
    prompt = STAGE1_PROMPT.format(
        tic=state.tic,
        company_name=state.company_name,
        industry=state.industry,
        sector=state.sector,
        company_description=state.company_description,
        headline=state.headline,
        summary=state.summary,
        publisher=state.publisher,
        publish_date=state.publish_date
    )
    system_prompt = SystemMessage(content=STAGE1_SYSTEM_MESSAGE)
    human_prompt = HumanMessage(content=prompt)
    messages = [system_prompt, human_prompt]
    response = json.loads(run_llm(messages).content)
    
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
        tic=state.tic,
        company_name=state.company_name,
        industry=state.industry,
        sector=state.sector,
        company_description=state.company_description,
        headline=state.headline,
        summary=state.summary,
        publisher=state.publisher,
        publish_date=state.publish_date,
        category=state.category,
        event_type=state.event_type
    )

    system_prompt = SystemMessage(content=STAGE2_SYSTEM_MESSAGE)
    human_prompt = HumanMessage(content=prompt)
    messages = [system_prompt, human_prompt]
    response = json.loads(run_llm(messages).content)

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