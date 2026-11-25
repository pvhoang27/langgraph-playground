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

ten = input("Tên file muốn xoá: ")
result = graph.invoke({"ten_file": ten}, config)

# Nếu graph đang dừng → hỏi người dùng
if "__interrupt__" in result:
    cau_hoi = result["__interrupt__"][0].value      # lấy câu hỏi trong interrupt
    tra_loi = input(f"🛑 {cau_hoi} ")
    result = graph.invoke(Command(resume=tra_loi), config)

print("✅", result["ket_qua"])