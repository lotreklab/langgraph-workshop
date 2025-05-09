from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
# from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# Load environment variables from .env file
load_dotenv()

# llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)
llm = ChatOllama(model="llama3.1")

def multiply(a:int, b:int) -> int:
    """multiply a and b

    Args:
        a (int): fisrt int
        b (int): second int

    Returns:
        int: result int
    """
    return a * b

def add(a:int, b:int):
    """Add a and b

    Args:
        a (int): first int
        b (int): second int

    Returns:
        int: result int
    """
    return a + b

def divide(a:int, b:int):
    """Divide a and b

    Args:
        a (int): first int
        b (int): second int

    Returns:
        int: result int
    """
    return a / b


tools = [add, divide, multiply]

llm_with_tools = llm.bind_tools(tools)

from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")


# Node 
def tool_calling_llm(state: MessagesState):
   return {"messages": llm_with_tools.invoke([sys_msg] + state["messages"])}

def custom_tools_condition(state: MessagesState):
    result = tools_condition(state)
    print(result)
    if result == "tools" and state["messages"][-1].tool_calls[0] == "multiply":
        return "__end__"
    return result

builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode(tools))
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tools", "tool_calling_llm")



db_path = "memory.db"
connection = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(connection)

graph = builder.compile(checkpointer=memory)
config = { "configurable": { "thread_id": "000"}}



result = graph.invoke({"messages": [ HumanMessage(content="What is 2 * 3?")]}, config=config)


result = graph.invoke({"messages": [HumanMessage(content="Now add 2"),]}, config=config)
print(len(result["messages"]))
for message in result["messages"]:
    message.pretty_print()

