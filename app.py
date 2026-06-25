from flask import Flask, flash, render_template, request, redirect, url_for, session
from conexion import get_db_connection
import psycopg
from datetime import date

app = Flask(__name__)
app.secret_key = "cft_tarapaca_2026"

# ==========================================
# RUTAS DE NAVEGACIÓN Y MENÚ
# ==========================================
@app.route('/')
def index():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT id, nombre_objeto, categoria, descripcion, lugar_encontrado, estado FROM objetos_perdidos')
        objetos = cur.fetchall()
    conn.close()
    return render_template('index.html', objetos=objetos)

@app.route("/principal")
def principal():
    return render_template("menu_publico.html")

# ==========================================
# GESTIÓN DE OBJETOS (Registrar, Buscar)
# ==========================================
@app.route("/registrar", methods=["GET", "POST"])
def registrar_objeto():
    if request.method == "POST":
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO objetos_perdidos 
                (nombre_objeto, categoria, descripcion, lugar_encontrado, fecha_encontrado, ubicacion_actual, estado)
                VALUES (%s, %s, %s, %s, %s, %s, 'Pendiente')
            """, (request.form.get("nombre"), request.form.get("categoria"), request.form.get("descripcion"), 
                    request.form.get("lugar"), request.form.get("fecha"), request.form.get("ubicacion")))
            conn.commit()
        conn.close()
        return redirect(url_for("principal"))
    return render_template("registrar.html")

@app.route("/buscar", methods=["GET", "POST"])
def buscar_objeto():
    if request.method == "POST":
        query = request.form.get("query")
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre_objeto, categoria, descripcion, lugar_encontrado, estado FROM objetos_perdidos WHERE nombre_objeto ILIKE %s", (f"%{query}%",))
            resultados = cur.fetchall()
        conn.close()
        return render_template("resultados.html", resultados=resultados)
    return render_template("resultado.html", resultados=resultados)

# ==========================================
# DASHBOARD ADMINISTRATIVO
# ==========================================
@app.route("/dashboard")
def dashboard():
    if not session.get("admin_autenticado"): 
        return redirect(url_for("login_admin"))
    
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Obtenemos la cantidad de otra forma para evitar errores
        cur.execute("SELECT count(*) FROM objetos_perdidos")
        # Usamos fetchone() que devuelve una tupla
        row = cur.fetchone()
        cantidad = row[0] if row else 0
        
        # Obtenemos los objetos
        cur.execute("SELECT id, nombre_objeto, categoria, fecha_encontrado, lugar_encontrado, ubicacion_actual, estado FROM objetos_perdidos ORDER BY id DESC")
        filas = cur.fetchall()
        
        # Procesamos los datos
        objetos = []
        for f in filas:
            objetos.append({
                "id": f[0], 
                "nombre": f[1], 
                "categoria": f[2], 
                "fecha": str(f[3]), 
                "lugar": f[4], 
                "ubicacion": f[5], 
                "estado": f[6]
            })
    conn.close()
    return render_template("dashboard.html", objetos=objetos, cantidad=cantidad)
# ==========================================
# EDITAR Y ELIMINAR (CRUD)
# ==========================================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_objeto(id):
    if not session.get("admin_autenticado"): return redirect(url_for("login_admin"))
    conn = get_db_connection()
    if request.method == "POST":
        with conn.cursor() as cur:
            cur.execute("""UPDATE objetos_perdidos SET nombre_objeto=%s, categoria=%s, fecha_encontrado=%s, 
                            lugar_encontrado=%s, ubicacion_actual=%s, estado=%s WHERE id=%s""", 
                        (request.form["nombre"], request.form["categoria"], request.form["fecha"], 
                            request.form["lugar"], request.form["ubicacion"], request.form["estado"], id))
            conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    
    with conn.cursor() as cur:
        cur.execute("SELECT id, nombre_objeto, categoria, fecha_encontrado, lugar_encontrado, ubicacion_actual, estado FROM objetos_perdidos WHERE id=%s", (id,))
        fila = cur.fetchone()
    conn.close()
    if not fila: return "Objeto no encontrado", 404
    objeto = {"id": fila[0], "nombre": fila[1], "categoria": fila[2], "fecha": str(fila[3]), "lugar": fila[4], "ubicacion": fila[5], "estado": fila[6]}
    return render_template("editar.html", objeto=objeto)

@app.route("/eliminar/<int:id>")
def eliminar_objeto(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM objetos_perdidos WHERE id = %s", (id,))
        conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

# ==========================================
# LOGIN Y FEEDBACK
# ==========================================
@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        password = request.form.get("password")
        print(f"Intento de login con: {password}") # Mira esto en los Logs de Render
        if password == "admin123":
            session["admin_autenticado"] = True
            print("Login exitoso, redirigiendo al dashboard...")
            return redirect(url_for("dashboard"))
    return render_template("login_admin.html")

@app.route("/enviar_feedback", methods=["POST"])
def enviar_feedback():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO feedback_alumnos (categoria, comentario, puntuacion) VALUES (%s,%s,%s)", 
                    (request.form["categoria"], request.form["comentario"], request.form["puntuacion"]))
        conn.commit()
    conn.close()
    return redirect(url_for("principal"))

@app.route("/activar_pc")
def activar_pc():
    session["modo_pc"] = True
    return redirect(request.referrer or url_for("principal"))

@app.route("/activar_totem")
def activar_totem():
    session["modo_pc"] = False
    return redirect(request.referrer or url_for("principal"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)