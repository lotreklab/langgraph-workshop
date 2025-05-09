
from langchain_core.tools import tool
from langgraph.types import interrupt, Command
from typing_extensions import Annotated
from langgraph.prebuilt import create_react_agent
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage, HumanMessage
from langchain_ollama import ChatOllama

model = ChatOllama(model="llama3.1")

@tool
def search(query: str):
    """Call to surf the web."""
    return f"I looked up: {query}. Result: It's sunny in San Francisco."

@tool
def ask_human(
    question: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Ask the human a question"""
    location = interrupt(question)
    tool_message = [ToolMessage(location, tool_call_id=tool_call_id)]
    return Command(
        update={
            "messages": tool_message
        },
        goto="agent"
    )

app = create_react_agent(
    model,
    tools=[search, ask_human],
    prompt="You are a research assistant. You can search the web for information. Ask human if you need more information.",
    name="research_agent",
)

