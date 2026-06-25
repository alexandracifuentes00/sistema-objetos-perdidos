import os
import psycopg
from psycopg.rows import dict_row

def get_db_connection():
    # Render inyectará la URL de Neon en esta variable automáticamente
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn