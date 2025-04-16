from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Connect to Neon DB
def get_db_connection():
    conn = psycopg2.connect(os.environ["NEON_DB_URL"])  # Use your Neon DB connection string
    return conn

@app.route('/upload', methods=['POST'])
def upload_csv():
    # Handle CSV upload logic here
    # Save the CSV data to Neon DB
    return jsonify({"message": "CSV uploaded successfully!"})

@app.route('/query', methods=['POST'])
def run_query():
    query = request.json.get('query')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"data": results})

if __name__ == '__main__':
    app.run(debug=True)
