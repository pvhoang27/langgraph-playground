from typing import Literal
from datetime import datetime, timezone, timedelta
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver     # ① thêm import (đặt lên đầu file)


# ========== 1. TOOLS (định nghĩa TẤT CẢ tool trước) ==========
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

tools = [cong, nhan, gio_hien_tai]      # ⭐ tạo list NGAY SAU các tool

# ========== 2. LLM (giờ mới dùng tools) ==========
llm = ChatOllama(model="qwen3:1.7b", temperature=0, reasoning=True)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = SystemMessage(
    content="Bạn có các tool: cong, nhan, gio_hien_tai. "
            "KHÔNG được tự tính toán hay tự đoán ngày giờ — PHẢI gọi tool. "
            "Hãy nhớ thông tin người dùng kể trong cuộc trò chuyện. "      # ← thêm
            "Trả lời ngắn gọn bằng tiếng Việt."
)

# ========== 3. NODE ==========
def chatbot(state: MessagesState):
    response = llm_with_tools.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": [response]}

# ========== 4. ROUTER ==========
def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if last.tool_calls:
        return "tools"
    return "__end__"


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", should_continue)
builder.add_edge("tools", "chatbot")

graph = builder.compile(checkpointer=InMemorySaver())  


thread_id = input("Nhập tên của bạn: ")
config = {"configurable": {"thread_id": thread_id}}       # ③ chọn "trang sổ"

print("Gõ 'exit' để thoát, 'doi' để đổi người")
while True:
    text = input(f"\n[{thread_id}] Bạn: ").strip()

    if text.lower() == "exit":
        break

    if text.lower() == "doi":                              # đổi sang người khác
        thread_id = input("Tên mới: ")
        config = {"configurable": {"thread_id": thread_id}}
        continue

    # ③ chỉ gửi TIN MỚI + config. Lịch sử do checkpointer lo
    result = graph.invoke({"messages": [("user", text)]}, config)

    # in tool đã gọi trong lượt này
    for m in result["messages"][-4:]:
        if isinstance(m, AIMessage) and m.tool_calls:
            for tc in m.tool_calls:
                print(f"   🔧 {tc['name']}({tc['args']})")

    print("Bot:", result["messages"][-1].content.strip())
    print(f"   ({len(result['messages'])} tin nhắn trong bộ nhớ)")