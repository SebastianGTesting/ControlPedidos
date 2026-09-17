# 🍽️ ControlPedidos — Menú Digital para Restaurante

Sistema web liviano para gestión de pedidos en restaurantes. Los clientes hacen su pedido desde el móvil escaneando un QR y el panel de caja recibe las comandas en tiempo real.

---

## 📁 Estructura del Proyecto

```
ControlPedidos/
├── app/
│   ├── __init__.py          # Factory de la app Flask
│   ├── database.py          # Conexión SQLite e inicialización de tablas
│   ├── routes.py            # Todas las rutas (cliente, admin, APIs)
│   ├── templates/
│   │   ├── cliente.html     # Vista del menú para clientes (móvil)
│   │   └── admin.html       # Panel de caja y administración
│   └── static/
│       ├── css/
│       │   ├── cliente.css
│       │   └── admin.css
│       └── js/
│           ├── cliente.js   # Lógica del carrito
│           └── admin.js     # Polling de comandas y arqueo de caja
├── instance/                # Base de datos SQLite (generada automáticamente, en .gitignore)
├── run.py                   # Punto de entrada
├── requirements.txt
└── .gitignore
```

---

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias

```bash
pip3 install -r requirements.txt
```

### 2. Ejecutar el servidor

```bash
python3 run.py
```

Se abrirá automáticamente el panel admin en el navegador.

---

## 🌐 URLs

| Vista | URL |
|---|---|
| Panel Admin (caja) | `http://localhost:5001/admin` |
| Menú Cliente Mesa 1 | `http://<tu-ip>:5001/?mesa=1` |
| Menú Cliente Mesa 2 | `http://<tu-ip>:5001/?mesa=2` |

> La IP local se imprime en la terminal al iniciar el servidor. Úsala para acceder desde los móviles de los clientes en la misma red WiFi.

---

## ✨ Funcionalidades

- **Menú digital** — Los clientes ven el menú, agregan productos al carrito y confirman el pedido desde su móvil.
- **Panel de caja en tiempo real** — Las comandas aparecen automáticamente cada 4 segundos sin recargar la página.
- **Notificación sonora** — Alerta de audio al llegar un nuevo pedido.
- **Flujo de pago configurable** — Dos modos: pagar antes de cocina o pagar al final.
- **Métodos de pago** — Efectivo, Nequi, Daviplata o Bre-B.
- **Arqueo de caja** — Totales del día divididos por método de pago.
- **Gestión del menú** — Añadir y eliminar platos desde el panel admin.

---

## 🛠️ Tecnologías

- **Backend:** Python 3 + Flask + SQLite
- **Frontend:** Bootstrap 5 + Font Awesome 6 + JavaScript Vanilla

---

## 📋 Requisitos

- Python 3.9+
- Flask 3.x
- Puerto `5001` libre (en macOS el 5000 lo usa AirPlay Receiver)
