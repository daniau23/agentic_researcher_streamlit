from langgraph.graph import StateGraph, END
from shared import ResearchState
from .search import search_node
from .loader import load_node
from .summarizer import summarize_node

builder = StateGraph(ResearchState)
builder.add_node("search", search_node)
builder.add_node("load", load_node)
builder.add_node("summarize", summarize_node)

builder.set_entry_point("search")
builder.add_edge("search", "load")
builder.add_edge("load", "summarize")
builder.add_edge("summarize", END)

web_graph = builder.compile()