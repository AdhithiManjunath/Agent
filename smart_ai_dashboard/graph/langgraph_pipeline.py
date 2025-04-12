from langgraph.graph import StateGraph, END
from agents.sql_agent import run_sql_query
from agents.observability_agent import analyze_data
from agents.dashboard_agent import create_dashboard
from typing import TypedDict, List, Any
import pandas as pd


# ✅ Define the shape of the state using TypedDict
class AgentState(TypedDict):
    input: str
    task: str
    result: str
    data: List[dict]
    columns: List[str]
    df: pd.DataFrame
    chart_type: str
    observation: str


def build_graph():
    # ✅ Define graph and state schema
    builder = StateGraph(AgentState)

    # ✅ Register nodes
    builder.add_node("sql_agent_node", run_sql_query)
    builder.add_node("observability_node", analyze_data)
    builder.add_node("dashboard_node", create_dashboard)

    # ✅ Define flow
    builder.set_entry_point("sql_agent_node")
    builder.add_edge("sql_agent_node", "observability_node")
    builder.add_edge("observability_node", "dashboard_node")
    builder.add_edge("dashboard_node", END)

    # ✅ Compile graph
    graph = builder.compile()
    return graph
