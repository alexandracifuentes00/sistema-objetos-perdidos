from flask import Flask, flash, render_template, request, redirect, url_for, session
from conexion import get_db_connection
import psycopg
from datetime import date

app = Flask(__name__)
app.secret_key = "cft_tarapaca_2026"

# ==========================================
# PÁGINA INICIAL Y MENÚ
# ==========================================
# ==========================================
# PÁGINA INICIAL
# ==========================================
@app.route('/')
def index():
    conn = get_db_connection()
    with conn.cursor() as cur:
        # CAMBIADO: 'id' a 'id_objeto'
        cur.execute('SELECT id_objeto, nombre_objeto, categoria, descripcion, lugar_encontrado, estado FROM objetos_perdidos')
        objetos = cur.fetchall()
    conn.close()
    return render_template('index.html', objetos=objetos)

@app.route("/principal")
def principal():
    return render_template("menu_publico.html")

# ==========================================
# REGISTRAR OBJETO
# ==========================================
@app.route("/registrar", methods=["GET", "POST"])
def registrar_objeto():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        categoria = request.form.get("categoria")
        descripcion = request.form.get("descripcion")
        lugar = request.form.get("lugar")
        fecha = request.form.get("fecha")
        ubicacion = request.form.get("ubicacion")
        
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO objetos_perdidos 
                (nombre_objeto, categoria, descripcion, lugar_encontrado, fecha_encontrado, ubicacion_actual, estado)
                VALUES (%s, %s, %s, %s, %s, %s, 'Pendiente')
            """, (nombre, categoria, descripcion, lugar, fecha, ubicacion))
            conn.commit()
        conn.close()
        return redirect(url_for("principal"))
    return render_template("registrar.html")

# ==========================================
# BÚSQUEDA
# ==========================================
@app.route("/buscar_resultados")
def buscar_resultados():
    query = request.args.get("query")
    if not query: return redirect(url_for("principal"))

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, nombre_objeto, categoria, descripcion, lugar_encontrado, estado FROM objetos_perdidos WHERE LOWER(nombre_objeto) LIKE LOWER(%s)", (f"%{query}%",))
        fila = cur.fetchone()
    conn.close()

    if fila is None: return render_template("sin_resultados.html", termino=query)
    objeto = {"id": fila[0], "nombre": fila[1], "categoria": fila[2], "descripcion": fila[3], "lugar": fila[4], "estado": fila[5]}
    return render_template("resultado.html", objeto=objeto, termino=query)

# ==========================================
# DASHBOARD ADMINISTRATIVO (Editar/Eliminar)
# ==========================================
@app.route("/dashboard")
def dashboard():
    if not session.get("admin_autenticado"): return redirect(url_for("login_admin"))
    conn = get_db_connection()
    with conn.cursor() as cur:
        # CAMBIADO: 'id' a 'id_objeto'
        cur.execute("SELECT id_objeto, nombre_objeto, categoria, fecha_encontrado, lugar_encontrado, ubicacion_actual, estado FROM objetos_perdidos ORDER BY id_objeto DESC")
        filas = cur.fetchall()
        objetos = [{"id": f[0], "nombre": f[1], "categoria": f[2], "fecha": str(f[3]), "lugar": f[4], "ubicacion": f[5], "estado": f[6]} for f in filas]
    conn.close()
    return render_template("dashboard.html", objetos=objetos)

# ==========================================
# EDITAR OBJETO
# ==========================================
@app.route("/editar/<int:id_objeto>", methods=["GET", "POST"])
def editar_objeto(id_objeto):
    if not session.get("admin_autenticado"): return redirect(url_for("login_admin"))
    conn = get_db_connection()
    if request.method == "POST":
        with conn.cursor() as cur:
            # CORREGIDO: Usamos id_objeto en el WHERE
            cur.execute("""UPDATE objetos_perdidos SET nombre_objeto=%s, categoria=%s, fecha_encontrado=%s, lugar_encontrado=%s, ubicacion_actual=%s, estado=%s WHERE id_objeto=%s""", 
                        (request.form["nombre"], request.form["categoria"], request.form["fecha"], request.form["lugar"], request.form["ubicacion"], request.form["estado"], id_objeto))
            conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    
    with conn.cursor() as cur:
        cur.execute("SELECT id_objeto, nombre_objeto, categoria, fecha_encontrado, lugar_encontrado, ubicacion_actual, estado FROM objetos_perdidos WHERE id_objeto=%s", (id_objeto,))
        fila = cur.fetchone()
    conn.close()
    
    # Manejo de error si no existe el objeto
    if not fila: return "Objeto no encontrado", 404
    
    objeto = {"id": fila[0], "nombre": fila[1], "categoria": fila[2], "fecha": str(fila[3]), "lugar": fila[4], "ubicacion": fila[5], "estado": fila[6]}
    return render_template("editar.html", objeto=objeto)

@app.route("/eliminar/<int:id_objeto>")
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
        if request.form.get("password") == "admin123":
            session["admin_autenticado"] = True
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
    
    # --- AÑADE ESTAS RUTAS PARA CORREGIR EL BUILDERROR ---
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