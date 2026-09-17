import sqlite3


def get_db_connection(db_path):
    conn = sqlite3.connect(db_path, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")

        # Tabla platos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS platos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT    NOT NULL,
                descripcion TEXT    NOT NULL,
                precio      REAL    NOT NULL,
                imagen      TEXT    NOT NULL,
                disponible  INTEGER DEFAULT 1
            )
        ''')

        cols_platos = [col[1] for col in cursor.execute("PRAGMA table_info(platos)").fetchall()]
        if "disponible" not in cols_platos:
            cursor.execute("ALTER TABLE platos ADD COLUMN disponible INTEGER DEFAULT 1")

        # Tabla pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa            INTEGER NOT NULL,
                detalle         TEXT,
                total           REAL    NOT NULL,
                estado          TEXT    NOT NULL DEFAULT 'Pendiente de Pago',
                metodo_pago     TEXT,
                fecha           TEXT,
                fecha_entregado TEXT
            )
        ''')

        cols_pedidos = [col[1] for col in cursor.execute("PRAGMA table_info(pedidos)").fetchall()]
        for col in ["metodo_pago", "detalle", "fecha", "fecha_entregado"]:
            if col not in cols_pedidos:
                cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {col} TEXT")

        # Tabla configuracion
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')
        cursor.execute(
            "INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('modo_pago', 'pagar_primero')"
        )

        # Datos de ejemplo si el menú está vacío
        if cursor.execute("SELECT COUNT(*) FROM platos").fetchone()[0] == 0:
            platos_iniciales = [
                (
                    "Hamburguesa Bacon Double",
                    "Doble carne Smash, queso cheddar, tocino crocante y salsa especial.",
                    32000,
                    "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500",
                    1,
                ),
                (
                    "Pizza Pepperoni Artesanal",
                    "Masa madre de fermentación lenta, queso mozzarella y pepperoni.",
                    38000,
                    "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=500",
                    1,
                ),
                (
                    "Tacos al Pastor (3 uds)",
                    "Carne de cerdo marinada, piña asada, cilantro y cebolla fina.",
                    25000,
                    "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=500",
                    1,
                ),
                (
                    "Limonada de Coco",
                    "Refrescante bebida natural batida con leche de coco y hielo.",
                    12000,
                    "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500",
                    1,
                ),
            ]
            cursor.executemany(
                "INSERT INTO platos (nombre, descripcion, precio, imagen, disponible) VALUES (?, ?, ?, ?, ?)",
                platos_iniciales,
            )

        conn.commit()
