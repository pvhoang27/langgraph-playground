from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END

llm = ChatOllama(
    model = "qwen3:1.7b",
    temperature=0.7,
    reasoning=False
)

#Prompt
SYSTEM_PROMPT = SystemMessage(content="Ban la tro ly than thien, tra loi bang tieng viet, ngan gon")

#Node
def chatbot(state: MessagesState):
    response = llm.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": [response]}

#Graph
builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile()

#Chat
history =[]
print("Chat voi bot:")
while True:
    text = input("\nBan:")
    if text.strip().lower() == "exit":
        break
    history.append(("user", text))
    result = graph.invoke({"messages": history})
    history = result["messages"]
    print("Bot:", history[-1].content)