from langchain_community.utilities import SQLDatabase
import os


def show_schema():
    db = SQLDatabase.from_uri(os.environ["POSTGRES_URI"])
    return db.get_table_info()
