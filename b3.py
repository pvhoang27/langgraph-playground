from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    logs_ghi_de: list[str]                              # không reducer → ghi đè
    logs_noi_them: Annotated[list[str], operator.add]   # reducer = operator.add → nối list

def node_a(state: State):
    return {"logs_ghi_de": ["A đã chạy"], "logs_noi_them": ["A đã chạy"]}

def node_b(state: State):
    return {"logs_ghi_de": ["B đã chạy"], "logs_noi_them": ["B đã chạy"]}

builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)
graph = builder.compile()

print(graph.invoke({"logs_ghi_de": [], "logs_noi_them": []}))