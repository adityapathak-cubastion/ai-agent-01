from dotenv import load_dotenv
from typing import Annotated
from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearchResults(max_results = 2)
tools = [tool]
llm = ChatOllama(model = "llama3.2:3b", temperature = 0.2)
llm_with_tools = llm.bind_tools(tools)

system_prompt = {
    "role": "system",
    "content": "You are a helpful assistant that can perform searches and answer questions based on the provided tools. Please try to respond in a friendly and clear manner.\
        If the user greets you, respond with a greeting. If the user asks a question, try to answer it. If the user asks for help, offer to perform a search.",
}

def chatbot(state: State):
    state["messages"].insert(0, system_prompt)
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools = [tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    # process user input through langgraph
    for event in graph.stream({"messages": [("user", user_input)]}):
        print(event)
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)