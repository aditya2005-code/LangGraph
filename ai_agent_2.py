from typing import TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
  messages : List[Union[HumanMessage,AIMessage]]

llm = ChatOpenAI(model = "gpt-4o")


def process(state:AgentState) ->AgentState:
  res = llm.invoke(state["messages"])
  state["messages"].append(AIMessage(content=res.content))
  print(f"AI : {res.content}")
  return state


graph = StateGraph(AgentState)
graph.add_node("process",process)
graph.add_edge(START,"process")
graph.add_edge("process",END)
app = graph.compile()

conversation_history = []

user_input = input("Enter : ")
while user_input != "exit":
  conversation_history.append(HumanMessage(content=user_input))
  ans = app.invoke({"messages" : [HumanMessage(content=user_input)]})
  conversation_history = ans["messages"]
  user_input = input("Enter : ")