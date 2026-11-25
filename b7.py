from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command            # ⭐ 2 thứ mới

class State(TypedDict):
    ten_file: str
    ket_qua: str

def chuan_bi(state: State):
    print(f"[chuan_bi] Chuẩn bị xoá file: {state['ten_file']}")
    return {}                                             # không cập nhật gì

def xin_phep(state: State):
    print("[xin_phep] Bắt đầu chạy node xin_phep")
    tra_loi = interrupt(f"Bạn có chắc muốn xoá '{state['ten_file']}'? (y/n)")   # ⭐ DỪNG
    print(f"[xin_phep] Người dùng trả lời: {tra_loi}")
    if tra_loi == "y":
        return {"ket_qua": f"Đã xoá {state['ten_file']} 🗑️"}
    return {"ket_qua": "Đã huỷ, không xoá gì cả ✋"}

builder = StateGraph(State)
builder.add_node("chuan_bi", chuan_bi)
builder.add_node("xin_phep", xin_phep)
builder.add_edge(START, "chuan_bi")
builder.add_edge("chuan_bi", "xin_phep")
builder.add_edge("xin_phep", END)
graph = builder.compile(checkpointer=InMemorySaver())    # ⭐ bắt buộc

config = {"configurable": {"thread_id": "1"}}

print("===== LẦN 1: chạy graph =====")
result = graph.invoke({"ten_file": "baocao.docx"}, config)
print("result:", result)
print("Graph đang dừng ở node:", graph.get_state(config).next)

print("\n===== LẦN 2: chạy tiếp với câu trả lời =====")
result = graph.invoke(Command(resume="y"), config)       # ⭐ CHẠY TIẾP
print("result:", result)