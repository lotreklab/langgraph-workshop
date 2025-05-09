# Set up the state
from langgraph.graph import MessagesState, START

# Set up the tool
# We will have one real tool - a search tool
# We'll also have one "fake" tool - a "ask_human" tool
# Here we define any ACTUAL tools
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt, Command
from typing_extensions import Annotated
from langgraph.prebuilt import create_react_agent, InjectedState
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage

@tool
def search(query: str):
    """Call to surf the web."""
    # This is a placeholder for the actual implementation
    # Don't let the LLM know this though 😊
    return f"I looked up: {query}. Result: It's sunny in San Francisco, but you better look out if you're a Gemini 😈."



@tool
async def ask_human(
    question: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Create a research canvas and set it as current research canvas then returns its link."""
    context = get_slack_context(state["slack_context_ts"])
    channel_id = context.channel_id
    try:
        canvas_id = await create_canvas(context, title, channel_id=channel_id)
        team_id, workspace = await team_info(context=context)
    except Exception as e:
        traceback.print_exc()
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        f"Failed to create canvas: {e}", tool_call_id=tool_call_id
                    )
                ]
            }
        )
    canvas_link = f"https://{workspace}.slack.com/docs/{team_id}/{canvas_id}"
    return Command(
        update={
            "canvas_content": "",
            "canvas_id": canvas_id,
            "messages": [ToolMessage(canvas_link, tool_call_id=tool_call_id)],
        }
    )



tools = [search]
tool_node = ToolNode(tools)

# Set up the model
from langchain_ollama import ChatOllama

model = ChatOllama(model="llama3.1")

from pydantic import BaseModel


# We are going "bind" all tools to the model
# We have the ACTUAL tools from above, but we also need a mock tool to ask a human
# Since `bind_tools` takes in tools but also just tool definitions,
# We can define a tool definition for `ask_human`
class AskHuman(BaseModel):
    """Ask the human a question"""

    question: str


model = model.bind_tools(tools + [AskHuman])

# Define nodes and conditional edges



# We define a fake node to ask the human
def ask_human(state):
    tool_call_id = state["messages"][-1].tool_calls[0]["id"]
    ask = AskHuman.model_validate(state["messages"][-1].tool_calls[0]["args"])
    location = interrupt(ask.question)
    tool_message = [{"tool_call_id": tool_call_id, "type": "tool", "content": location}]
    return {"messages": tool_message}


# Build the graph

from langgraph.graph import END, StateGraph

# Define a new graph
workflow = StateGraph(MessagesState)

# Define the three nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_node("ask_human", ask_human)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.add_edge(START, "agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    path_map=["ask_human", "action", END],
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# After we get back the human response, we go back to the agent
workflow.add_edge("ask_human", "agent")

# Set up memory
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile(checkpointer=memory)

display(Image(app.get_graph().draw_mermaid_png()))