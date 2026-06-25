import psycopg

def conectar():
    return psycopg.connect(
        host="localhost",
        dbname="objetos_perdidos",
        user="postgres",
        password="6211",
        port="5432"
    )