from typing_extensions import TypedDict
import random
from typing import Literal
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    graph_state: str
    

def node_1(state: State) -> str:
    print("--- node_1 ---")
    return {"graph_state": state["graph_state"] + "I am"}

def node_2(state: State) -> str:
    print("--- node_2 ---")
    return {"graph_state": state["graph_state"] + " happy!"}

def node_3(state: State) -> str:
    print("--- node_3 ---")
    return {"graph_state": state["graph_state"] + " sad!"}



def decide_mood(state: State) -> Literal["node_2", "node_3"]:
    print("--- decide_mood ---")
    user_input = state["graph_state"] # Often we use state to decide where to go
    if random.random() > 0.5:
        return "node_2"
    return "node_3"



builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

graph = builder.compile()


result = graph.invoke({"graph_state": "Hello! "})

print(result)








    


