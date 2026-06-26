import os
import psycopg
from psycopg.rows import dict_row

def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    print("DATABASE_URL:", database_url)

    if not database_url:
        raise Exception("No se encontró la variable DATABASE_URL")

    return psycopg.connect(
        database_url,
        row_factory=dict_row
    )