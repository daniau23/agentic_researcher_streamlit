"""
Article Graph

Workflow:
  writer -> critic -> [ACCEPTED -> END, REJECTED -> writer]
"""

from langgraph.graph import StateGraph, END
from shared import ResearchState
from .writer import writer_node
from .critic import critic_node

builder = StateGraph(ResearchState)

builder.add_node("writer", writer_node)
builder.add_node("critic", critic_node)

def should_accept(state):
    return state.critique == "ACCEPTED"

builder.set_entry_point("writer")
builder.add_edge("writer", "critic")
builder.add_conditional_edges("critic", should_accept, {
    True: END,
    False: "writer"
})

article_graph = builder.compile()