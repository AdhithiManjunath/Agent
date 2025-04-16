from config.env import load_env
from graph.langgraph_pipeline import build_graph
import pandas as pd
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_env()
graph = build_graph()

# Initialize LLM with API key from environment
llm = ChatGroq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])

while True:
    query = input("\n💬 Ask a question about your data (or type 'exit'): ")
    if query.lower() in ["exit", "quit"]:
        print("\n👋 Exiting. See you next time!")
        break

    # Prepare initial state
    state = {
        "input": query,
        "task": "dashboard",
        "result": "",
        "data": [],
        "columns": [],
        "df": pd.DataFrame(),  # Ensure it's always a valid DataFrame
        "chart_type": "",
        "observation": ""
    }

    try:
        final_state = graph.invoke(state)

        if not final_state:
            print("❌ Error: final_state is None.")
            continue

        print("\n✅ Final SQL Query:\n", final_state.get(
            "result", "No SQL query returned."))
        print("\n📊 Suggested Chart Type:\n", final_state.get(
            "chart_type", "No chart type detected."))
        print("\n🧠 LLM Observation:\n", final_state.get(
            "observation", "No observation generated."))

        dashboard_result = final_state.get("result", "")
        if "dashboard.png" in dashboard_result:
            print("\n📈 Dashboard saved to 'output/dashboard.png'")
        else:
            print("\n⚠️ Visualization Result:\n", dashboard_result)

    except Exception as e:
        print("❌ Exception during pipeline execution:", e)

def analyze_data(state):
    # Check if DataFrame is present in the state
    if "df" in state:
        df = state["df"]
    else:
        print("❌ Error: No DataFrame found in state.")
        return state

    # If DataFrame is empty, return early with appropriate message
    if df.empty:
        return {**state, "chart_type": "none", "observation": "No data to visualize."}

    # Convert the first 5 rows of the DataFrame to markdown format
    sample = df.head(5).to_markdown()

    # Prepare the prompt for the LLM
    prompt = (
        f"You are a data analysis expert. Here's a sample of a dataframe:\n\n{sample}\n\n"
        "Based on this, suggest the most suitable chart type (bar, line, pie, scatter, etc.). "
        "Also, provide a brief explanation for why that chart type would be suitable."
    )

    # Get LLM response
    response = llm.invoke([HumanMessage(content=prompt)])
    output = response.content.strip()

    # Extract chart type from the LLM response
    chart_type = "bar"  # Default fallback chart type
    explanation = "The LLM didn't provide an explanation."

    # Look for chart type and explanation in the response
    lines = output.splitlines()
    for line in lines:
        # Look for chart-related keywords (case-insensitive)
        if "bar" in line.lower():
            chart_type = "bar"
        elif "line" in line.lower():
            chart_type = "line"
        elif "pie" in line.lower():
            chart_type = "pie"
        elif "scatter" in line.lower():
            chart_type = "scatter"

        # Capture the explanation
        if "explanation" in line.lower() or "reason" in line.lower():
            explanation = line.strip()

    # Check if an observation was generated
    if explanation == "The LLM didn't provide an explanation.":
        observation = "No observation generated. Please check the data or the query."
    else:
        observation = explanation

    return {**state, "chart_type": chart_type, "observation": observation}
