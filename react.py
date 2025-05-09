


from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
from datetime import datetime
from langchain_ollama import ChatOllama


tavily_tool = TavilySearch(
    max_results=5,
    search_depth="advanced",
    chunks_per_source=1,
)

llm = ChatOllama(model="llama3.1")

prompt = (
    "You are a researcher and your task is to search the web to produce strategic reports with useful insights. ",
    "Make sure to always attach the source of the information you provide in the report. ",
    f"The current date is: {datetime.now().strftime('%Y-%m-%d')} ",
)

graph = create_react_agent(
    llm, tools=[tavily_tool], prompt="\n".join(prompt), name="research_agent"
)

