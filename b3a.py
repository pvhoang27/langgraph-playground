from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

#State 
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

#Bot gia lap
def fake_bot(state: State):
    last = state["messages"][-1]
    reply = f"Ban vua noi: '{last.content}'. Minh la bot gia lap"
    return {"messages": [AIMessage(content=reply)]}

#Node
builder = StateGraph(State)
builder.add_node("bot", fake_bot)

#Edge
builder.add_edge(START, "bot")
builder.add_edge("bot", END)

#Compile
graph = builder.compile()

#Cach 1 : dung object HumanMessage
# result = graph.invoke({"messages": [HumanMessage(content = "Xin chao")]})
# for msg in result["messages"]:
#     print(f"[{msg.type}] {msg.content}")

#Cach 2 : dang rut gon (role, content)
result = graph.invoke({"messages": [("user", "Hom nay troi dep qua")]})
for msg in result["messages"]:
    msg.pretty_print() 
