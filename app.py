# No need for sqlite3 anymore
import logging
from typing import TypedDict
import os
from langchain.agents.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents import AgentExecutor
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
load_dotenv()


# Logging optional
logging.basicConfig(level=logging.INFO)

# ✅ Replace with your actual Neon PostgreSQL connection URI
postgres_uri = os.environ["POSTGRES_URI"]
# Step 1: Connect to Neon PostgreSQL
db = SQLDatabase.from_uri(postgres_uri)

# Step 2: Use Groq LLM
llm = ChatGroq(
    api_key=os.environ["GROQ_API_KEY"],
    model="llama3-70b-8192"
)

# Step 3: Create SQL Agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_agent: AgentExecutor = create_sql_agent(
    llm=llm, toolkit=toolkit, verbose=True)

# Step 4: Define LangGraph State


class AgentState(TypedDict):
    input: str
    result: str


def sql_node(state: AgentState) -> AgentState:
    query = state["input"]
    result_dict = sql_agent.invoke({"input": query})
    result = result_dict["output"]
    return {"input": query, "result": result}


# Step 5: Build LangGraph
builder = StateGraph(AgentState)
builder.add_node("sql_agent_node", sql_node)
builder.set_entry_point("sql_agent_node")
builder.add_edge("sql_agent_node", END)
graph = builder.compile()

# Step 6: Ask Questions via CLI
while True:
    user_input = input("\nAsk something about the database (or type 'exit'): ")
    if user_input.lower() in ["exit", "quit"]:
        break

    final_state = graph.invoke({"input": user_input})
    print("Answer:", final_state["result"])
