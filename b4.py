from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "qwen3:1.7b",
    temperature=0.7,
    reasoning=False
)

response = llm.invoke(["user", "Gioi thieu ve Ha Noi"])
print(type(response))
print(response)
print("--------------------")
print(response.content)