from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langchain_core.messages import ToolMessage


@tool
def cong(a: int, b: int) -> int:
    """Cộng hai số nguyên a và b."""
    return a + b

@tool
def nhan(a: int, b: int) -> int:
    """Nhân hai số nguyên a và b."""
    return a * b
SYSTEM_PROMPT = SystemMessage(
    content="Bạn KHÔNG được tự tính toán. Với MỌI phép tính, bạn PHẢI gọi tool cong hoặc nhan và nhớ nêu kết quả cho tôi."
)
tools = [cong, nhan]

llm = ChatOllama(model="qwen3:1.7b", temperature=0, reasoning=False)
llm_with_tools = llm.bind_tools(tools)      # ⭐ gắn danh sách tool vào LLM

# Thử riêng (chưa dùng graph)
msg = llm_with_tools.invoke([SYSTEM_PROMPT,("user", "1234 nhân 5678 bằng bao nhiêu?")])
print("content:", msg.content)
print("tool_calls:", msg.tool_calls)


# ② Tự chạy tool theo yêu cầu của LLM
call = msg.tool_calls[0]
tool_map = {"cong": cong, "nhan": nhan}
ket_qua = tool_map[call["name"]].invoke(call["args"])
print("Kết quả tool:", ket_qua)

# ③ Gửi kết quả lại cho LLM (ToolMessage phải có tool_call_id khớp với yêu cầu)
tool_msg = ToolMessage(content=str(ket_qua), tool_call_id=call["id"])
final = llm_with_tools.invoke([
    SYSTEM_PROMPT,
    ("user", "1234 nhân 5678 bằng bao nhiêu?"),
    msg,          # tin AI chứa tool_calls
    tool_msg,     # kết quả tool
])
print("Trả lời cuối:", final.content)