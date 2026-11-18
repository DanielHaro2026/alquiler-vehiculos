import os
import sqlite3
import re
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, get_db

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "clave-local-autorrent-cambiar-en-produccion"
)

init_db()


@app.route("/")
def index():
    conn = get_db()

    vehiculos = conn.execute(
        "SELECT COUNT(*) FROM vehiculos"
    ).fetchone()[0]

    clientes = conn.execute(
        "SELECT COUNT(*) FROM clientes"
    ).fetchone()[0]

    alquileres = conn.execute(
        "SELECT COUNT(*) FROM alquileres"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        vehiculos=vehiculos,
        clientes=clientes,
        alquileres=alquileres
    )


@app.route("/health")
def health():
    return {"status": "ok"}, 200


# ============================================
# MODULO DE VEHICULOS
# ============================================

@app.route("/vehiculos")
def listar_vehiculos():
    conn = get_db()
    vehiculos = conn.execute(
        "SELECT * FROM vehiculos ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "vehiculos/lista.html",
        vehiculos=vehiculos
    )


@app.route("/vehiculos/nuevo", methods=["GET", "POST"])
def nuevo_vehiculo():
    if request.method == "POST":
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        placa = request.form.get("placa", "").strip().upper()

        try:
            precio = float(request.form.get("precio_dia", 0))
        except (ValueError, TypeError):
            precio = 0

        if not marca or not modelo or not placa or precio <= 0:
            flash("Complete todos los campos correctamente.", "danger")
            return render_template("vehiculos/formulario.html", vehiculo=None)

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO vehiculos (marca, modelo, placa, precio_dia)
                VALUES (?, ?, ?, ?)
            """, (marca, modelo, placa, precio))
            conn.commit()
            flash("Vehiculo registrado correctamente.", "success")

        except sqlite3.IntegrityError:
            flash("La placa ya se encuentra registrada.", "danger")

        finally:
            conn.close()

        return redirect(url_for("listar_vehiculos"))

    return render_template("vehiculos/formulario.html", vehiculo=None)


@app.route("/vehiculos/editar/<int:id>", methods=["GET", "POST"])
def editar_vehiculo(id):
    conn = get_db()

    vehiculo = conn.execute(
        "SELECT * FROM vehiculos WHERE id = ?", (id,)
    ).fetchone()

    if not vehiculo:
        conn.close()
        flash("Vehiculo no encontrado.", "danger")
        return redirect(url_for("listar_vehiculos"))

    if request.method == "POST":
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        placa = request.form.get("placa", "").strip().upper()

        try:
            precio = float(request.form.get("precio_dia", 0))
        except (ValueError, TypeError):
            precio = 0

        if not marca or not modelo or not placa or precio <= 0:
            conn.close()
            flash("Complete todos los campos correctamente.", "danger")
            return render_template("vehiculos/formulario.html", vehiculo=vehiculo)

        try:
            conn.execute("""
                UPDATE vehiculos
                SET marca = ?, modelo = ?, placa = ?, precio_dia = ?
                WHERE id = ?
            """, (marca, modelo, placa, precio, id))

            conn.commit()
            flash("Vehiculo actualizado correctamente.", "success")

        except sqlite3.IntegrityError:
            flash("La placa ya pertenece a otro vehiculo.", "danger")

        finally:
            conn.close()

        return redirect(url_for("listar_vehiculos"))

    conn.close()
    return render_template("vehiculos/formulario.html", vehiculo=vehiculo)


@app.route("/vehiculos/eliminar/<int:id>", methods=["POST"])
def eliminar_vehiculo(id):
    conn = get_db()

    try:
        conn.execute("DELETE FROM vehiculos WHERE id = ?", (id,))
        conn.commit()
        flash("Vehiculo eliminado correctamente.", "success")

    except sqlite3.IntegrityError:
        flash("No se puede eliminar: tiene alquileres asociados.", "danger")

    finally:
        conn.close()

    return redirect(url_for("listar_vehiculos"))


# ============================================
# MODULO DE CLIENTES
# ============================================

@app.route("/clientes")
def listar_clientes():
    conn = get_db()

    clientes = conn.execute("""
        SELECT * FROM clientes
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "clientes/lista.html",
        clientes=clientes
    )


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    if request.method == "POST":

        nombres = request.form.get("nombres", "").strip()
        apellidos = request.form.get("apellidos", "").strip()
        dni = request.form.get("dni", "").strip()
        telefono = request.form.get("telefono", "").strip()

        if not nombres or not apellidos or not telefono:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("clientes/formulario.html", cliente=None)

        if not re.fullmatch(r"\d{8}", dni):
            flash("El DNI debe contener exactamente 8 digitos.", "danger")
            return render_template("clientes/formulario.html", cliente=None)

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO clientes (nombres, apellidos, dni, telefono)
                VALUES (?, ?, ?, ?)
            """, (nombres, apellidos, dni, telefono))

            conn.commit()
            flash("Cliente registrado correctamente.", "success")

        except sqlite3.IntegrityError:
            flash("El DNI ya se encuentra registrado.", "danger")

        finally:
            conn.close()

        return redirect(url_for("listar_clientes"))

    return render_template("clientes/formulario.html", cliente=None)


@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    conn = get_db()

    cliente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?", (id,)
    ).fetchone()

    if not cliente:
        conn.close()
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for("listar_clientes"))

    if request.method == "POST":

        nombres = request.form.get("nombres", "").strip()
        apellidos = request.form.get("apellidos", "").strip()
        dni = request.form.get("dni", "").strip()
        telefono = request.form.get("telefono", "").strip()

        if not nombres or not apellidos or not telefono:
            conn.close()
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("clientes/formulario.html", cliente=cliente)

        if not re.fullmatch(r"\d{8}", dni):
            conn.close()
            flash("El DNI debe contener exactamente 8 digitos.", "danger")
            return render_template("clientes/formulario.html", cliente=cliente)

        try:
            conn.execute("""
                UPDATE clientes
                SET nombres = ?, apellidos = ?, dni = ?, telefono = ?
                WHERE id = ?
            """, (nombres, apellidos, dni, telefono, id))

            conn.commit()
            flash("Cliente actualizado correctamente.", "success")

        except sqlite3.IntegrityError:
            flash("El DNI ya pertenece a otro cliente.", "danger")

        finally:
            conn.close()

        return redirect(url_for("listar_clientes"))

    conn.close()

    return render_template(
        "clientes/formulario.html",
        cliente=cliente
    )


@app.route("/clientes/eliminar/<int:id>", methods=["POST"])
def eliminar_cliente(id):
    conn = get_db()

    try:
        conn.execute("DELETE FROM clientes WHERE id = ?", (id,))
        conn.commit()
        flash("Cliente eliminado correctamente.", "success")

    except sqlite3.IntegrityError:
        flash("No se puede eliminar: el cliente tiene alquileres asociados.", "danger")

    finally:
        conn.close()

    return redirect(url_for("listar_clientes"))



# ============================================
# MODULO DE ALQUILERES
# ============================================

@app.route("/alquileres")
def listar_alquileres():

    conn = get_db()

    alquileres = conn.execute("""
        SELECT
            a.*,
            c.nombres,
            c.apellidos,
            c.dni,
            v.marca,
            v.modelo,
            v.placa,
            v.precio_dia
        FROM alquileres a
        INNER JOIN clientes c ON a.cliente_id = c.id
        INNER JOIN vehiculos v ON a.vehiculo_id = v.id
        ORDER BY a.id DESC
    """).fetchall()

    conn.close()

    registros = []

    for a in alquileres:
        registro = dict(a)
        inicio = date.fromisoformat(registro["fecha_alquiler"])
        fin = date.fromisoformat(registro["fecha_devolucion"])
        registro["dias"] = (fin - inicio).days
        registros.append(registro)

    return render_template(
        "alquileres/lista.html",
        alquileres=registros
    )


@app.route("/alquileres/nuevo", methods=["GET", "POST"])
def nuevo_alquiler():

    conn = get_db()

    if request.method == "POST":

        cliente_id = request.form.get("cliente_id", type=int)
        vehiculo_id = request.form.get("vehiculo_id", type=int)

        fecha_alquiler = request.form.get("fecha_alquiler", "")
        fecha_devolucion = request.form.get("fecha_devolucion", "")

        try:
            inicio = date.fromisoformat(fecha_alquiler)
            fin = date.fromisoformat(fecha_devolucion)

            if fin <= inicio:
                raise ValueError("Fecha de devolucion incorrecta")

        except (ValueError, TypeError):
            conn.close()
            flash("La fecha de devolucion debe ser posterior al alquiler.", "danger")
            return redirect(url_for("nuevo_alquiler"))

        if not cliente_id or not vehiculo_id:
            conn.close()
            flash("Seleccione un cliente y un vehiculo.", "danger")
            return redirect(url_for("nuevo_alquiler"))

        dias = (fin - inicio).days

        try:
            # Iniciar transaccion para evitar asignaciones simultaneas
            conn.execute("BEGIN IMMEDIATE")

            cliente = conn.execute(
                "SELECT id FROM clientes WHERE id = ?",
                (cliente_id,)
            ).fetchone()

            vehiculo = conn.execute("""
                SELECT id, precio_dia, estado
                FROM vehiculos
                WHERE id = ?
            """, (vehiculo_id,)).fetchone()

            if not cliente:
                raise ValueError("El cliente seleccionado no existe.")

            if not vehiculo:
                raise ValueError("El vehiculo seleccionado no existe.")

            if vehiculo["estado"] != "Disponible":
                raise ValueError("El vehiculo ya se encuentra alquilado.")

            total = dias * vehiculo["precio_dia"]

            conn.execute("""
                INSERT INTO alquileres (
                    cliente_id,
                    vehiculo_id,
                    fecha_alquiler,
                    fecha_devolucion,
                    total,
                    estado
                )
                VALUES (?, ?, ?, ?, ?, 'Activo')
            """, (
                cliente_id,
                vehiculo_id,
                fecha_alquiler,
                fecha_devolucion,
                total
            ))

            conn.execute("""
                UPDATE vehiculos
                SET estado = 'Alquilado'
                WHERE id = ?
            """, (vehiculo_id,))

            conn.commit()

            flash(
                f"Alquiler registrado. Total: S/ {total:.2f}",
                "success"
            )

        except ValueError as error:
            conn.rollback()
            flash(str(error), "danger")

        except sqlite3.IntegrityError:
            conn.rollback()
            flash("No se pudo registrar el alquiler.", "danger")

        finally:
            conn.close()

        return redirect(url_for("listar_alquileres"))

    clientes = conn.execute("""
        SELECT * FROM clientes ORDER BY nombres
    """).fetchall()

    vehiculos = conn.execute("""
        SELECT * FROM vehiculos
        WHERE estado = 'Disponible'
        ORDER BY marca
    """).fetchall()

    conn.close()

    return render_template(
        "alquileres/formulario.html",
        clientes=clientes,
        vehiculos=vehiculos
    )


@app.route("/alquileres/devolver/<int:id>", methods=["POST"])
def devolver_alquiler(id):

    conn = get_db()

    try:
        conn.execute("BEGIN IMMEDIATE")

        alquiler = conn.execute("""
            SELECT id, vehiculo_id, estado
            FROM alquileres
            WHERE id = ?
        """, (id,)).fetchone()

        if not alquiler:
            raise ValueError("Alquiler no encontrado.")

        if alquiler["estado"] != "Activo":
            raise ValueError("Este alquiler ya fue devuelto.")

        conn.execute("""
            UPDATE alquileres
            SET estado = 'Devuelto'
            WHERE id = ?
        """, (id,))

        # Comprobar que no existan otros alquileres activos
        otro_activo = conn.execute("""
            SELECT COUNT(*)
            FROM alquileres
            WHERE vehiculo_id = ?
            AND estado = 'Activo'
        """, (alquiler["vehiculo_id"],)).fetchone()[0]

        if otro_activo == 0:
            conn.execute("""
                UPDATE vehiculos
                SET estado = 'Disponible'
                WHERE id = ?
            """, (alquiler["vehiculo_id"],))

        conn.commit()
        flash("Devolucion registrada. Vehiculo actualizado.", "success")

    except ValueError as error:
        conn.rollback()
        flash(str(error), "danger")

    finally:
        conn.close()

    return redirect(url_for("listar_alquileres"))

if __name__ == "__main__":
    app.run(debug=True)

