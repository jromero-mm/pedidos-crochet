import sqlite3
from pathlib import Path

RUTA_BD = Path(__file__).resolve().parent / "pedidos.db"

def crear_base_datos():
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY,
            cliente TEXT NOT NULL,
            telefono TEXT,
            producto TEXT NOT NULL,
            precio_total REAL NOT NULL,
            adelanto REAL NOT NULL DEFAULT 0,
            fecha_entrega TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conexion.commit()
    conexion.close()
def insertar_pedido(
    cliente,
    telefono,
    producto,
    precio_total,
    adelanto,
    fecha_entrega
):
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO pedidos (
            cliente,
            telefono,
            producto,
            precio_total,
            adelanto,
            fecha_entrega
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            cliente,
            telefono,
            producto,
            precio_total,
            adelanto,
            fecha_entrega
        )
    )

    conexion.commit()

    pedido_id = cursor.lastrowid

    conexion.close()

    return pedido_id   
def obtener_pedidos():
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            cliente,
            producto,
            precio_total,
            adelanto,
            precio_total - adelanto AS saldo,
            fecha_entrega,
            estado
        FROM pedidos
        ORDER BY id DESC
    """)

    pedidos = cursor.fetchall()

    conexion.close()

    return pedidos
def actualizar_estado(pedido_id, estado):
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE pedidos
        SET estado = ?
        WHERE id = ?
        """,
        (estado, pedido_id)
    )

    conexion.commit()
    conexion.close()