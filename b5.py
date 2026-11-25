from langchain_core.tools import tool

@tool
def cong(a: int, b: int) -> int:
    """Cộng hai số nguyên a và b."""
    return a + b

@tool
def nhan(a: int, b: int) -> int:
    """Nhân hai số nguyên a và b."""
    return a * b

tools = [cong, nhan]

# Thử tool như hàm thường
print(cong.invoke({"a": 2, "b": 3}))   # → 5
print(cong.name, "|", cong.description, "|", cong.args)


