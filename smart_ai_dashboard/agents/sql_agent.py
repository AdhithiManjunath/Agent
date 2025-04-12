import os
import pandas as pd
from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from config.env import load_env

# Load environment variables
load_env()

db = SQLDatabase.from_uri(os.environ["POSTGRES_URI"])
llm = ChatGroq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_agent = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)


def run_sql_query(state):
    user_input = state.get("input", "")

    if not user_input:
        return {**state, "result": "No input provided", "data": [], "columns": [], "df": pd.DataFrame()}

    print("\n🟡 Incoming user query:", user_input)
    schema = db.get_table_info()

    prompt = (
        f"You are an AI SQL assistant. Here is the database schema:\n{schema}\n\n"
        f"Convert the following natural language request into a valid SQL query:\n{user_input}\n"
        f"Only return the SQL code. Don't wrap it in triple backticks."
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    sql_query = response.content.strip()

    print("🧠 Cleaned SQL:", sql_query)

    try:
        # ✅ Use raw connection for reliable access to column names
        raw_conn = db._engine.raw_connection()
        cursor = raw_conn.cursor()
        cursor.execute(sql_query)

        # ✅ Extract column names
        columns = [desc[0] for desc in cursor.description]

        # ✅ Fetch all rows
        rows = cursor.fetchall()

        # ✅ Safely close
        cursor.close()
        raw_conn.close()

        # ✅ Build DataFrame
        df = pd.DataFrame(rows, columns=columns)

        print("\n📑 Tabular Data:")
        print(df)

        return {
            **state,
            "result": sql_query,
            "data": df.to_dict(orient="records"),
            "columns": columns,
            "df": df
        }

    except Exception as e:
        print("❌ Error executing query:", e)
        return {**state, "result": f"SQL error: {e}", "data": [], "columns": [], "df": pd.DataFrame()}
