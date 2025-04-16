# app_ui.py
import streamlit as st
import pandas as pd
import requests
import os

# Function to upload CSV to FaaS
def upload_csv_to_faas(file):
    url = "https://your-actual-api-gateway-url/upload"  # Replace with your actual API Gateway URL
    files = {'file': file}
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading file: {e}")
        return None

# Function to run SQL query
def run_sql_query(query):
    url = "https://your-api-gateway-url/query"  # Replace with your API Gateway URL
    response = requests.post(url, json={"query": query})
    return response.json()

# Streamlit UI
st.title("Smart AI Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Display the uploaded CSV file
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df)

    # Upload CSV to FaaS
    if st.button("Upload to Database"):
        result = upload_csv_to_faas(uploaded_file)
        st.success(result.get("body", "CSV uploaded successfully!"))

    # Query input
    query = st.text_input("Enter your SQL query:")

    if st.button("Run Query"):
        if query:
            result = run_sql_query(query)
            st.write("Query Result:")
            st.dataframe(pd.DataFrame(result.get("data", [])))
        else:
            st.warning("Please enter a query.")

# Display any observations or messages
if 'observation' in locals():
    st.write("Observation:")
    st.write(observation)
    