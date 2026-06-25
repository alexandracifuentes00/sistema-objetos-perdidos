from flask import Flask, flash, render_template, request, redirect, url_for, session
from conexion import get_db_connection
import psycopg
from datetime import date

app = Flask(__name__)
app.secret_key = "cft_tarapaca_2026"


# ==========================================
# PÁGINA INICIAL (PORTADA DE BIENVENIDA)
# ==========================================
@app.route('/')
def index():
    conn = get_db_connection() # Usas el nombre nuevo
    objetos = conn.execute('SELECT * FROM objetos_perdidos').fetchall()
    conn.close()
    return render_template('index.html', objetos=objetos)

# ==========================================
# MENÚ PÚBLICO (CENTRAL DE BOTONES)
# ==========================================
@app.route("/principal")
def principal():
    return render_template("menu_publico.html")

# ==========================================
# REGISTRAR OBJETO
# ==========================================
# Ejemplo corregido para la función de registro
@app.route("/registrar", methods=["POST"])
def registrar_objeto():
    # 1. Primero capturamos del formulario
    nombre = request.form.get("nombre") 
    categoria = request.form.get("categoria")
    descripcion = request.form.get("descripcion")
    lugar = request.form.get("lugar")
    estado = "Pendiente" # Valor por defecto
    fecha = date.today()
    ubicacion = "Biblioteca - Mostrador"

    # 2. Luego usamos las variables en el INSERT
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO objetos_perdidos 
            (nombre_objeto, categoria, descripcion, fecha_encontrado, lugar_encontrado, ubicacion_actual, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, categoria, descripcion, fecha, lugar, ubicacion, estado))
        conn.commit()
    conn.close()
    return redirect(url_for("principal"))

# ==========================================
# CONTROL DE BÚSQUEDA DE OBJETOS
# ==========================================
@app.route('/buscar', methods=["GET", "POST"])
def buscar_objeto():
    if request.method == "POST":
        nombre_buscar = request.form.get("nombre", "").strip()
        conn = get_db_connection()
        with conn.cursor() as cur:
            # CORRECCIÓN: Usar SELECT para buscar, no INSERT
            cur.execute("SELECT id_objeto, nombre_objeto, categoria, descripcion, fecha_encontrado, lugar_encontrado, ubicacion_actual, estado FROM objetos_perdidos WHERE nombre_objeto = %s", (nombre_buscar,))
            fila = cur.fetchone()
        conn.close()
        
        if fila is None:
            return render_template("sin_resultados.html", termino=nombre_buscar)
        
        objeto = {
            "id": fila[0], "nombre": fila[1], "categoria": fila[2], "descripcion": fila[3],
            "fecha": str(fila[4]), "lugar": fila[5], "ubicacion": fila[6], "estado": fila[7]
        }
        return render_template("resultado.html", objeto=objeto)
        
    return render_template("buscar.html")

# ==========================================
# DETALLE DE RESULTADO INDIVIDUAL
# ==========================================
@app.route("/buscar_resultados")
def buscar_resultados():
    query = request.args.get("query")
    if not query:
        return redirect(url_for("buscar_objeto"))

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id_objeto, nombre_objeto, categoria, descripcion, fecha_encontrado, lugar_encontrado, ubicacion_actual, estado
            FROM objetos_perdidos
            WHERE LOWER(nombre_objeto) LIKE LOWER(%s)
        """, (f"%{query}%",))
        fila = cur.fetchone()
    conn.close()

    if fila is None:
        return render_template("sin_resultados.html", termino=query)

    objeto = {
        "id": fila[0],
        "nombre": fila[1],
        "categoria": fila[2],
        "descripcion": fila[3],
        "fecha": str(fila[4]),
        "lugar": fila[5],
        "ubicacion": fila[6],
        "estado": fila[7]
    }
    return render_template("resultado.html", objeto=objeto, termino=query)

# ==========================================
# DASHBOARD ADMINISTRATIVO
# ==========================================
@app.route("/dashboard")
def dashboard():
    if not session.get("admin_autenticado"):
        return redirect(url_for("login_admin"))
    accion = request.args.get("accion", "actualizar")
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id_objeto, nombre_objeto, categoria, fecha_encontrado, lugar_encontrado, ubicacion_actual, estado
            FROM objetos_perdidos
            ORDER BY id_objeto DESC
        """)
        filas = cur.fetchall()

        objetos = []
        for fila in filas:
            objetos.append({
                "id": fila[0],
                "nombre": fila[1],
                "categoria": fila[2],
                "fecha": str(fila[3]),
                "lugar": fila[4],
                "ubicacion": fila[5],
                "estado": fila[6]
            })
        comentarios = []
        if accion == "feedback":
            cur.execute("""
                SELECT id_feedback, categoria, comentario, puntuacion, fecha_envio
                FROM feedback_alumnos
                ORDER BY id_feedback DESC
            """)
            filas_fb = cur.fetchall()
            for fila in filas_fb:
                comentarios.append({
                    "id": fila[0],
                    "categoria": fila[1],
                    "comentario": fila[2],
                    "puntuacion": fila[3],
                    "fecha": str(fila[4])[:10]
                })

    conn.close()
    return render_template("dashboard.html", objetos=objetos, comentarios=comentarios, vista_actual=accion)

# ==========================================
# LOGIN / LOGOUT
# ==========================================
@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    if session.get("admin_autenticado"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        password = request.form.get("password")
        if password == "admin123":
            session["admin_autenticado"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Contraseña incorrecta. Inténtalo de nuevo.")
            return redirect(url_for("login_admin"))
    return render_template("login_admin.html")

@app.route("/logout")
def logout():
    session.pop("admin_autenticado", None)
    return redirect(url_for("principal"))

# ==========================================
# EDITAR OBJETO
# ==========================================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_objeto(id):
    if not session.get("admin_autenticado"):
        return redirect(url_for("login_admin"))
        conn = get_db_connection()
        if request.method == "POST":
            with conn.cursor() as cur:
                cur.execute("""
                UPDATE objetos_perdidos
                SET nombre_objeto=%s, categoria=%s, fecha_encontrado=%s, lugar_encontrado=%s, ubicacion_actual=%s, estado=%s
                WHERE id_objeto=%s
            """, (
                request.form["nombre"],
                request.form["categoria"],
                request.form["fecha"],
                request.form["lugar"],
                request.form["ubicacion"],
                request.form["estado"],
                id
            ))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

        with conn.cursor() as cur:
            cur.execute("""
            SELECT id_objeto, nombre_objeto, categoria, fecha_encontrado, lugar_encontrado, ubicacion_actual, estado
            FROM objetos_perdidos WHERE id_objeto=%s
        """, (id,))
        fila = cur.fetchone()

        conn.close()

        objeto = {
        "id": fila[0],
        "nombre": fila[1],
        "categoria": fila[2],
        "fecha": str(fila[3]),
        "lugar": fila[4],
        "ubicacion": fila[5],
        "estado": fila[6]
    }
        return render_template("editar.html", objeto=objeto)

# ==========================================
# ELIMINAR OBJETO
# ==========================================
@app.route("/eliminar/<int:id>")
def eliminar_objeto(id):
    if not session.get("admin_autenticado"):
        return redirect(url_for("login_admin"))
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM objetos_perdidos WHERE id_objeto = %s", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    except Exception as e:
        return f"Error al eliminar el objeto: {e}"

# ==========================================
# SUGERENCIAS Y FEEDBACK
# ==========================================
@app.route("/sugerencias")
def sugerencias():
    return render_template("sugerencias.html")

@app.route("/enviar_feedback", methods=["POST"])
def enviar_feedback():
    categoria = request.form["categoria"]
    comentario = request.form["comentario"]
    puntuacion = request.form["puntuacion"]

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO feedback_alumnos (categoria, comentario, puntuacion)
            VALUES (%s,%s,%s)
        """, (categoria, comentario, puntuacion))
    conn.commit()
    conn.close()
    return redirect(url_for("principal"))

# ==========================================
# CAMBIO DINÁMICO DE PANTALLA
# ==========================================
@app.route("/activar_pc")
def activar_pc():
    session["modo_pc"] = True
    return redirect(request.referrer or url_for("principal"))

@app.route("/activar_totem")
def activar_totem():
    session["modo_pc"] = False
    return redirect(request.referrer or url_for("principal"))

@app.context_processor
def injectar_modo():
    return {
        "modo_pc": session.get("modo_pc", False)
    }

if __name__ == '__main__':
    # El host '0.0.0.0' permite que otros dispositivos en tu red (celulares, otros PCs)
    # puedan acceder a tu app usando tu dirección IP local.
    app.run(host='0.0.0.0', port=5000, debug=True) 

