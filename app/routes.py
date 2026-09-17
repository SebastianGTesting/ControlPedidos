from datetime import datetime
from flask import current_app, render_template, request, jsonify
from .database import get_db_connection


def register_routes(app):

    # ------------------------------------------------------------------ #
    #  CLIENTE                                                             #
    # ------------------------------------------------------------------ #

    @app.route("/")
    def vista_cliente():
        mesa = request.args.get("mesa", default=1, type=int)
        db = current_app.config["DATABASE"]
        with get_db_connection(db) as conn:
            platos = conn.execute("SELECT * FROM platos WHERE disponible = 1").fetchall()
            modo_row = conn.execute(
                "SELECT valor FROM configuracion WHERE clave = 'modo_pago'"
            ).fetchone()
            modo_pago = modo_row["valor"] if modo_row else "pagar_primero"
        return render_template("cliente.html", platos=platos, mesa=mesa, modo_pago=modo_pago)

    # ------------------------------------------------------------------ #
    #  API PEDIDOS                                                         #
    # ------------------------------------------------------------------ #

    @app.route("/api/pedido", methods=["POST"])
    def recibir_pedido():
        data = request.json
        mesa = data.get("mesa")
        carrito = data.get("carrito", {})

        detalle_lineas = []
        total = 0
        for item in carrito.values():
            subtotal = item["precio"] * item["cantidad"]
            total += subtotal
            detalle_lineas.append(f"{item['cantidad']}x {item['nombre']} ($ {subtotal:,.0f})")

        detalle_str = "\n".join(detalle_lineas)
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = current_app.config["DATABASE"]

        with get_db_connection(db) as conn:
            modo_row = conn.execute(
                "SELECT valor FROM configuracion WHERE clave = 'modo_pago'"
            ).fetchone()
            modo = modo_row["valor"] if modo_row else "pagar_primero"

            estado_inicial = (
                "Pendiente de Pago" if modo == "pagar_primero" else "Pasado a cocina"
            )
            mensaje = (
                "¡Pedido registrado! Por favor pasa a la caja para realizar el pago e iniciar la preparación."
                if modo == "pagar_primero"
                else "¡Pedido enviado directamente a cocina! Muchas gracias."
            )

            conn.execute(
                "INSERT INTO pedidos (mesa, detalle, total, estado, fecha) VALUES (?, ?, ?, ?, ?)",
                (mesa, detalle_str, total, estado_inicial, fecha_actual),
            )
            conn.commit()

        return jsonify({"status": "ok", "mensaje": mensaje})

    @app.route("/api/pedidos")
    def obtener_pedidos_json():
        db = current_app.config["DATABASE"]
        with get_db_connection(db) as conn:
            pedidos = conn.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchall()

        pedidos_activos = []
        historial_completo = []
        ahora = datetime.now()

        for p in pedidos:
            dict_p = dict(p)
            historial_completo.append(dict_p)

            if dict_p["estado"] == "Entregado" and dict_p["fecha_entregado"]:
                try:
                    dt_entregado = datetime.strptime(
                        dict_p["fecha_entregado"], "%Y-%m-%d %H:%M:%S"
                    )
                    if (ahora - dt_entregado).total_seconds() > 300:
                        continue
                except Exception:
                    pass
            pedidos_activos.append(dict_p)

        return jsonify({"activos": pedidos_activos, "historial": historial_completo})

    # ------------------------------------------------------------------ #
    #  ADMIN                                                               #
    # ------------------------------------------------------------------ #

    @app.route("/admin")
    def vista_admin():
        db = current_app.config["DATABASE"]
        with get_db_connection(db) as conn:
            platos = conn.execute("SELECT * FROM platos").fetchall()
            modo_row = conn.execute(
                "SELECT valor FROM configuracion WHERE clave = 'modo_pago'"
            ).fetchone()
            modo_pago = modo_row["valor"] if modo_row else "pagar_primero"
        return render_template("admin.html", platos=platos, modo_pago=modo_pago)

    @app.route("/admin/agregar_plato", methods=["POST"])
    def agregar_plato():
        nombre = request.form["nombre"]
        precio = float(request.form["precio"])
        imagen = request.form["imagen"]
        descripcion = request.form["descripcion"]
        db = current_app.config["DATABASE"]
        with get_db_connection(db) as conn:
            conn.execute(
                "INSERT INTO platos (nombre, descripcion, precio, imagen, disponible) VALUES (?, ?, ?, ?, 1)",
                (nombre, descripcion, precio, imagen),
            )
            conn.commit()
        return '<script>window.location.href="/admin";</script>'

    @app.route("/admin/eliminar_plato/<int:plato_id>")
    def eliminar_plato(plato_id):
        db = current_app.config["DATABASE"]
        with get_db_connection(db) as conn:
            conn.execute("DELETE FROM platos WHERE id = ?", (plato_id,))
            conn.commit()
        return '<script>window.location.href="/admin";</script>'

    @app.route("/admin/cambiar_estado", methods=["POST"])
    def cambiar_estado():
        pedido_id = request.form.get("pedido_id")
        nuevo_estado = request.form.get("nuevo_estado")
        metodo_pago = request.form.get("metodo_pago")
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = current_app.config["DATABASE"]

        with get_db_connection(db) as conn:
            if nuevo_estado and metodo_pago:
                conn.execute(
                    "UPDATE pedidos SET estado = ?, metodo_pago = ? WHERE id = ?",
                    (nuevo_estado, metodo_pago, pedido_id),
                )
            elif nuevo_estado == "Entregado":
                conn.execute(
                    "UPDATE pedidos SET estado = ?, fecha_entregado = ? WHERE id = ?",
                    (nuevo_estado, fecha_actual, pedido_id),
                )
            elif nuevo_estado:
                conn.execute(
                    "UPDATE pedidos SET estado = ? WHERE id = ?",
                    (nuevo_estado, pedido_id),
                )
            elif metodo_pago:
                conn.execute(
                    "UPDATE pedidos SET metodo_pago = ? WHERE id = ?",
                    (metodo_pago, pedido_id),
                )
            conn.commit()

        return jsonify({"status": "ok"})

    @app.route("/admin/configurar_modo", methods=["POST"])
    def configurar_modo():
        modo = request.form.get("modo")
        db = current_app.config["DATABASE"]
        with get_db_connection(db) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO configuracion (clave, valor) VALUES ('modo_pago', ?)",
                (modo,),
            )
            conn.commit()
        return jsonify({"status": "ok"})
