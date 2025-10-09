from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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

