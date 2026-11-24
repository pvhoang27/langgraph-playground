from typing import TypedDict
from langgraph.graph import StateGraph, START, END


#1. State
class State(TypedDict):
    name: str
    greeting: str

#2. Node
def say_hello(state: State):
    return {"greeting": f"Xin chào, {state['name']}!"}

def add_emoji(state: State):
    return {"greeting": state["greeting"] +" 👋"} 

#3.Tạo graph builder vs State
builder = StateGraph(State)

#4. Thêm node 
builder.add_node("say_hello", say_hello)
builder.add_node("add_emoji", add_emoji)

#5. Edge : nối các node theo thứ tự
builder.add_edge(START,"say_hello")
builder.add_edge("say_hello", "add_emoji")
builder.add_edge("add_emoji", END)

#6.Compile
graph = builder.compile()

#.7 chạy nền 
# result = graph.invoke({"name" : "Hai"})
# print(result)

for step in graph.stream({"name": "Hai"}):
    print(step)

