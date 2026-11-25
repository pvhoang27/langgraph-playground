from typing import Literal
from datetime import datetime, timezone, timedelta
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

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
            "Sau khi có kết quả từ tool, trả lời ngắn gọn bằng tiếng Việt."
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

# ========== 5. GRAPH (chỉ 2 node: chatbot + tools) ==========
builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", should_continue)
builder.add_edge("tools", "chatbot")

graph = builder.compile()
# ========== 6. CHẠY THỬ ==========
from langchain_core.messages import AIMessage, ToolMessage

def in_ket_qua(q: str, messages: list):
    print("\n" + "─" * 50)
    print(f"❓ {q}")
    for m in messages[1:]:                      # bỏ qua câu hỏi của user
        if isinstance(m, AIMessage) and m.tool_calls:
            for tc in m.tool_calls:
                args = ", ".join(f"{k}={v}" for k, v in tc["args"].items())
                print(f"   🔧 gọi {tc['name']}({args})")
        elif isinstance(m, ToolMessage):
            print(f"   ↳ kết quả: {m.content}")
    print(f"💬 {messages[-1].content.strip()}")

cau_hoi = [
    "Tính (3 + 5) nhân 4",              # cần 2 tool
    "mấy giờ",                         # không cần tool
]

for q in cau_hoi:
    result = graph.invoke({"messages": [("user", q)]})
    in_ket_qua(q, result["messages"])


for step in graph.stream({"messages": [("user", q)]}):
    for node_name in step:
        print("→ đã chạy node:", node_name)