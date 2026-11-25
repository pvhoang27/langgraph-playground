from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

def bot(state: MessagesState):
    so_tin = len(state["messages"])
    tin_cuoi = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Bạn vừa nói '{tin_cuoi}'. Mình đang nhớ {so_tin} tin nhắn.")]}

builder = StateGraph(MessagesState)
builder.add_node("bot", bot)
builder.add_edge(START, "bot")
builder.add_edge("bot", END)
graph = builder.compile(checkpointer=InMemorySaver())

# 2 người = 2 thread_id
hoang = {"configurable": {"thread_id": "hoang"}}
lan   = {"configurable": {"thread_id": "lan"}}

graph.invoke({"messages": [("user", "Tôi là Hoàng")]}, hoang)
graph.invoke({"messages": [("user", "Tôi 25 tuổi")]}, hoang)
r = graph.invoke({"messages": [("user", "Chào bot")]}, lan)
print("lan  :", r["messages"][-1].content)
r = graph.invoke({"messages": [("user", "Còn tôi?")]}, hoang)
print("hoang:", r["messages"][-1].content)

# Xem bộ nhớ của một thread
print("\n--- Bộ nhớ của thread 'hoang' ---")
state = graph.get_state(hoang)                 # ⭐ đọc trang "hoang"
for m in state.values["messages"]:
    print(f"[{m.type}] {m.content}")