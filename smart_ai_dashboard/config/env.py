import os
from dotenv import load_dotenv


def load_env():
    load_dotenv()
    if not os.getenv("POSTGRES_URI") or not os.getenv("GROQ_API_KEY"):
        raise EnvironmentError("Missing POSTGRES_URI or GROQ_API_KEY in .env")
