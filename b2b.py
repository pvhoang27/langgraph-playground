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

def senior_node(state: State):
    return {"greeting": state["greeting"] +" Mời bạn tham gia câu lạc bộ người cao tuổi 👴👵"}

def add_emoji(state: State):
    return {"greeting": state["greeting"] +" 👋"}

#Hàm router
def route_by_age(state: State) -> Literal["adult_node", "kid_node", "senior_node"]:
    if state["age"] >= 60:
       return "senior_node"
    
    elif state["age"] >= 18:
        return "adult_node"
    
    return "kid_node"
    
#Graph
builder = StateGraph(State)
builder.add_node("say_hello", say_hello)
builder.add_node("adult_node", adult_node)
builder.add_node("kid_node", kid_node)
builder.add_node("senior_node", senior_node)
builder.add_node("add_emoji", add_emoji)

#Edge
builder.add_edge(START, "say_hello")
builder.add_conditional_edges("say_hello",route_by_age)
builder.add_edge("adult_node", "add_emoji")
builder.add_edge("kid_node", "add_emoji")
builder.add_edge("senior_node", "add_emoji")
builder.add_edge("add_emoji", END)

#Compile 
graph = builder.compile()
# for age in [25, 10, 80]:
#     print(f"--- age = {age} ---")
#     for step in graph.stream({"name": "Hai", "age": age}):
#         print(step)
result = graph.invoke({"name": "Hai", "age": 25})
print(result)   

# print(graph.get_graph().draw_mermaid())