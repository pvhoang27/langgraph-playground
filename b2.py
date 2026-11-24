from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

#State
class State(TypedDict):
    name: str
    age :int
    greeting: str

#Node
def say_hello(state: State):
    return {"greeting": f"Xin chào, {state['name']}!"}

def adult_node(state: State):
    return {"greeting": state["greeting"] + " Mời bạn mở tài khoản ngân hàng 💳"}

def kid_node(state: State):
    return {"greeting": state["greeting"] + " Mời bạn xem hoạt hình 🧸"}

#Hàm router
def route_by_age(state: State) -> Literal["adult_node", "kid_node"]:
    if state["age"] >= 18:
        return "adult_node"
    return "kid_node"
    
#Graph
builder = StateGraph(State)
builder.add_node("say_hello", say_hello)
builder.add_node("adult_node", adult_node)
builder.add_node("kid_node", kid_node)

#Edge
builder.add_edge(START, "say_hello")
builder.add_conditional_edges("say_hello",route_by_age)
builder.add_edge("adult_node", END)
builder.add_edge("kid_node", END)

#Compile 
graph = builder.compile()
for age in [25, 10]:
    print(f"--- age = {age} ---")
    for step in graph.stream({"name": "Hai", "age": age}):
        print(step)
