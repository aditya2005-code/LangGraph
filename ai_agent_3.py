from typing import TypedDict, List, Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tools
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode

load_dotenv()

class AgentState(TypedDict):
  messages : Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a:int,b:int):
  return a+b

tools = [add]

llm = ChatOpenAI(model = "gpt-4o").bind_tools(tools)


def process(state:AgentState) ->AgentState:
  system_prompt = SystemMessage(content="SystemMessage")
  res = llm.invoke([system_prompt] + state["messages"])
  return {"messages": [res]}

def shouldContinue(state:AgentState) :
  messages=state["messages"]
  last_message = messages[-1]
  if not last_message.tool_calls:
    return "end"
  else:
    return "continue"


graph = StateGraph(AgentState)
graph.add_node("our_agent",process)
tool_node = ToolNode(tools=tools)
graph.add_node("tools",tool_node)
graph.add_entry_point("our_agent")
graph.add_conditional_edges(
    "our_agent",
    shouldContinue,
    {
        "continue":tools,
        "end": END,
    },
)

graph.add_edge("tools","our_agent")
agent = graph.compile()

def print_stream(stream):
  for s in stream:
    message = s["messages"][-1]
    if isinstance(message,tuple):
      print(message)
    else:
      message.pretty_print()

inputs = {"messages" : [("user","add 3 + 4")]}
print_stream(app.stream(inputs,stream_mode="values"))

