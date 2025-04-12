import os
import matplotlib.pyplot as plt
import pandas as pd


def create_dashboard(state, save_path="output/dashboard.png"):
    # Debugging: print the state to ensure it's passed correctly
    print("DEBUG: Checking 'state' content before visualization:")
    print(state)  # Print state content to inspect it

    # Ensure that 'df' exists in state
    if "df" not in state:
        print("❌ Error: No DataFrame found in state.")
        return {"result": "No DataFrame found in state."}

    # Ensure 'chart_type' is in state
    chart_type = state.get("chart_type", "none")
    print("DEBUG: Chart Type:", chart_type)  # Print chart type

    # If DataFrame is empty or chart type is 'none', return early
    df = state["df"]
    if df.empty or chart_type == "none":
        return {"result": "No data to visualize."}

    # Check if df is a valid pandas DataFrame
    if not isinstance(df, pd.DataFrame):
        print("❌ Error: 'df' is not a valid DataFrame.")
        return {"result": "'df' is not a valid DataFrame."}

    # Ensure there are at least two columns
    if df.shape[1] < 2:
        return {"result": "Insufficient columns for charting. Need at least 2 columns."}

    # Create the plot based on chart_type
    plt.figure(figsize=(8, 6))
    title = f"{chart_type.capitalize()} Chart"

    try:
        if chart_type == "bar":
            df.iloc[:, :2].plot(kind="bar", x=df.columns[0], y=df.columns[1])
        elif chart_type == "line":
            df.iloc[:, :2].plot(kind="line", x=df.columns[0], y=df.columns[1])
        elif chart_type == "pie":
            df.iloc[:, 1].plot(
                kind="pie", labels=df.iloc[:, 0], autopct="%1.1f%%")
        elif chart_type == "scatter":
            df.plot(kind="scatter", x=df.columns[0], y=df.columns[1])
        else:
            df.plot()

        plt.title(title)
        plt.tight_layout()

        # Ensure output directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the plot as a PNG image
        plt.savefig(save_path)
        print(f"✅ Dashboard saved to {save_path}")
        return {"result": f"Dashboard saved to {save_path}"}

    except Exception as e:
        print("❌ Visualization failed:", e)
        return {"result": f"Visualization error: {e}"}
