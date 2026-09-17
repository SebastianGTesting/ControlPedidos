import webbrowser
from app import create_app, obtener_ip_local

app = create_app()

if __name__ == "__main__":
    ip_local = obtener_ip_local()
    port = 5001

    print("--------------------------------------------------")
    print(" Gourmet Express — Servidor Iniciado")
    print("--------------------------------------------------")
    print(f" Admin  (PC):    http://localhost:{port}/admin")
    print(f" Cliente (móvil): http://{ip_local}:{port}/?mesa=1")
    print("--------------------------------------------------")

    webbrowser.open(f"http://localhost:{port}/admin")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
