from config.env import load_env
from graph.langgraph_pipeline import build_graph
import pandas as pd

load_env()
graph = build_graph()

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
