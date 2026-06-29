from flask import Flask, flash, render_template, request, redirect, url_for, session
from conexion import get_db_connection
import psycopg
from datetime import date
import os

app = Flask(__name__)
app.secret_key = "cft_tarapaca_2026"

# ==========================================
# RUTAS DE NAVEGACIÓN Y MENÚ
# ==========================================
@app.route('/')
def index():
    # OPTIMIZACIÓN: Redirigimos directamente al menú público para que el tótem 
    # no arroje error 404 si alguien ingresa a la URL base.
    return redirect(url_for("principal"))

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
        
        # Enviamos el mensaje de éxito antes de redirigir al menú público
        flash('¡El objeto se ha guardado correctamente en el sistema!', 'success')
        return redirect(url_for("principal"))
        
    return render_template("registrar.html")

@app.route("/buscar", methods=["GET", "POST"])
def buscar_objeto():
    if request.method == "POST":
        nombre = request.form.get("nombre")

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    nombre_objeto,
                    categoria,
                    descripcion,
                    fecha_encontrado,
                    lugar_encontrado,
                    ubicacion_actual,
                    estado
                FROM objetos_perdidos
                WHERE nombre_objeto ILIKE %s
            """, (f"%{nombre}%",))

            resultados = cur.fetchall()
        conn.close()

        if not resultados:
            return render_template(
                "sin_resultados.html",
                termino=nombre
            )

        return render_template(
            "resultado.html",
            resultados=resultados
        )

    return render_template("buscar.html")

# ==========================================
# DASHBOARD ADMINISTRATIVO
# ==========================================
@app.route("/dashboard")
def dashboard():
    if not session.get("admin_autenticado"):
        return redirect(url_for("login_admin"))
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM objetos_perdidos")
        cantidad = cur.fetchone()['total']
        
        cur.execute("""
            SELECT
                id,
                nombre_objeto,
                categoria,
                descripcion,
                fecha_encontrado,
                lugar_encontrado,
                ubicacion_actual,
                estado
            FROM objetos_perdidos
            ORDER BY id DESC
        """)
        objetos = cur.fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        objetos=objetos,
        cantidad=cantidad
    )

# ==========================================
# EDITAR Y ELIMINAR (CRUD)
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
                SET
                    nombre_objeto=%s,
                    categoria=%s,
                    descripcion=%s,
                    fecha_encontrado=%s,
                    lugar_encontrado=%s,
                    ubicacion_actual=%s,
                    estado=%s
                WHERE id=%s
            """, (
                request.form["nombre"],
                request.form["categoria"],
                request.form["descripcion"],
                request.form["fecha"],
                request.form["lugar"],
                request.form["ubicacion"],
                request.form["estado"],
                id
            ))
            conn.commit()
        conn.close()
        flash("Objeto actualizado correctamente.", "success")
        return redirect(url_for("dashboard"))
        
    with conn.cursor() as cur:
        cur.execute("""
            SELECT *
            FROM objetos_perdidos
            WHERE id=%s
        """, (id,))
        objeto = cur.fetchone()
    conn.close()
    if objeto is None:
        return "Objeto no encontrado", 404
    return render_template("editar.html", objeto=objeto)

@app.route("/eliminar/<int:id>")
def eliminar_objeto(id):
    if not session.get("admin_autenticado"):
        return redirect(url_for("login_admin"))
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM objetos_perdidos WHERE id=%s",
            (id,)
        )
        conn.commit()
    conn.close()
    flash("Objeto eliminado correctamente.", "success")
    return redirect(url_for("dashboard"))

# ==========================================
# LOGIN Y FEEDBACK
# ==========================================
@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        password = request.form.get("password")

        if password == "admin123":
            session["admin_autenticado"] = True
            return redirect(url_for("dashboard"))

        flash("Contraseña incorrecta", "danger")

    return render_template("login_admin.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.")
    return redirect(url_for("principal"))

@app.route("/enviar_feedback", methods=["POST"])
def enviar_feedback():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO feedback_alumnos (categoria, comentario, puntuacion) VALUES (%s,%s,%s)", 
                    (request.form["categoria"], request.form["comentario"], request.form["puntuacion"]))
        conn.commit()
    conn.close()
    return redirect(url_for("principal"))

@app.route("/sugerencias")
def sugerencias():
    return render_template("sugerencias.html")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)