import os
import socket
from flask import Flask


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["DATABASE"] = os.path.join(
        os.path.dirname(__file__), "..", "instance", "restaurante.db"
    )

    from .database import init_db
    init_db(app.config["DATABASE"])

    from .routes import register_routes
    register_routes(app)

    return app


def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip
