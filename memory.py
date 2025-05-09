from langchain_ollama import ChatOllama

from langgraph.graph import START, StateGraph, MessagesState, END
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    RemoveMessage,
)

llm = ChatOllama(model="llama3.1")


class SummaryMessagesState(MessagesState):
    summary: str


def conversation(state: SummaryMessagesState):

    summary = state.get("summary", "")

    if summary:

        system_message = f"You are an AI assistant and you have allready had a conversation with this human and this is the summary of conversation earlier: \n\n{summary}\n\n Use this information to answer the human's next questions."

        messages = [SystemMessage(content=system_message)] + state["messages"]

    else:
        messages = state["messages"]

    print(messages)
    response = llm.invoke(messages)
    return {"messages": response}


def summarize_conversation(state: SummaryMessagesState):

    summary = state.get("summary", "")

    if summary:

        summary_message = (
            f"This is a summary of the conversation so far: {summary}. \n\n",
            "Extend the summary by taking into account the new messages above:",
        )

    else:
        summary_message = (
            "Create a summary of the conversation above and return only the summary:"
        )

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)
    summary = response.content

    message_to_delete = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": summary, "messages": message_to_delete}


def should_continue(state: SummaryMessagesState):
    messages = state["messages"]
    if len(messages) > 6:
        return "summarize_conversation"
    return END


builder = StateGraph(SummaryMessagesState)
builder.add_node("conversation", conversation)
builder.add_node("summarize_conversation", summarize_conversation)


builder.add_edge(START, "conversation")
builder.add_conditional_edges("conversation", should_continue)
builder.add_edge("summarize_conversation", END)


graph = builder.compile()
