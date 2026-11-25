from typing import Literal
from datetime import datetime, timezone, timedelta
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver  

#1.Tools
@tool
def cong(a: int, b: int) -> int:
    """Cộng hai số nguyên a và b."""
    return a + b

@tool
def nhan(a: int, b: int) -> int:
    """Nhân hai số nguyên a và b."""
    return a * b

@tool
def gio_hien_tai() -> str:
    """Trả về ngày và giờ hiện tại theo múi giờ Việt Nam (UTC+7)."""
    vn_tz = timezone(timedelta(hours=7))
    return datetime.now(vn_tz).strftime("%H:%M:%S %d/%m/%Y (GMT+7)")

tools = [cong, nhan, gio_hien_tai]

#2.LLM
llm = ChatOllama(model="qwen3:1.7b", temperature=0, reasoning=False)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = SystemMessage(
    content="Bạn là trợ lý thân thiện, có các tool: cong, nhan, gio_hien_tai. "
            "KHÔNG được tự tính toán hay tự đoán ngày giờ — PHẢI gọi tool. "
            "Hãy nhớ thông tin người dùng kể trong cuộc trò chuyện. "
            "Trả lời ngắn gọn bằng tiếng Việt."
)

#3. Node
def chatbot(state :MessagesState):
    response = llm_with_tools.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": [response]}

#4. Router
def should_continue(state: MessagesState) ->  Literal["tools", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "tools"
    return "__end__"

#5. Graph
builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", should_continue)
builder.add_edge("tools", "chatbot")

#Checkpointer
graph = builder.compile(checkpointer = InMemorySaver())

#6.Chat
thread_id = input("Nhập tên của bạn (thread_id): ")
config = {"configurable": {"thread_id": thread_id}}   

print("Chat với agent ('exit' thoát | 'doi' đổi người | 'xem' xem bộ nhớ)")
while True:
    text = input(f"\n[{thread_id}] Bạn: ").strip()
    if text.lower() == "exit": 
        break   
    if text.lower() == "doi":
        thread_id = input("Tên mới: ")
        config = {"configurable": {"thread_id": thread_id}}
        continue
    if text.lower() == "xem":
        state = graph.get_state(config)                   
        for m in state.values.get("messages", []):
            m.pretty_print()
        continue

    result = graph.invoke({"messages": [("user", text)]}, config)
    for m in result["messages"][-4:]:
        if isinstance(m, AIMessage) and m.tool_calls:
            for tc in m.tool_calls:
                print(f"   🔧 {tc['name']}({tc['args']})")
    print("Bot:", result["messages"][-1].content.strip())
    print(f"   (thread '{thread_id}' đang có {len(result['messages'])} tin nhắn)")