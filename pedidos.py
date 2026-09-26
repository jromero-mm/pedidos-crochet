import os
import sqlite3
import sys
from pathlib import Path


def _directorio_datos():
    """Devuelve una carpeta estable para guardar la base de datos.

    Al ejecutar desde Python se mantiene la carpeta del proyecto. Al ejecutar
    desde un .exe generado con PyInstaller se usa la carpeta que contiene al
    ejecutable, para que los pedidos se guarden localmente y sobrevivan al
    cerrar y abrir nuevamente el programa.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


DIRECTORIO_DATOS = _directorio_datos()

try:
    DIRECTORIO_DATOS.mkdir(parents=True, exist_ok=True)
except OSError:
    # Si el ejecutable está en una carpeta de solo lectura, usamos una
    # ubicación local del usuario en Windows.
    if os.name == "nt":
        DIRECTORIO_DATOS = (
            Path(os.environ.get("APPDATA", str(Path.home())))
            / "Melicrochet"
        )
    else:
        DIRECTORIO_DATOS = Path.home() / ".melicrochet"
    DIRECTORIO_DATOS.mkdir(parents=True, exist_ok=True)

RUTA_BD = DIRECTORIO_DATOS / "pedidos.db"

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
def actualizar_pedido(
    pedido_id,
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
        UPDATE pedidos
        SET
            cliente = ?,
            telefono = ?,
            producto = ?,
            precio_total = ?,
            adelanto = ?,
            fecha_entrega = ?
        WHERE id = ?
        """,    
        
        (
            cliente,
            telefono,
            producto,
            precio_total,
            adelanto,
            fecha_entrega,
            pedido_id
        )
    )
    conexion.commit()
    conexion.close()        
def obtener_pedido(pedido_id):
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            id,
            cliente,
            telefono,
            producto,
            precio_total,
            adelanto,
            fecha_entrega,
            estado
        FROM pedidos
        WHERE id = ?
        """,
        (pedido_id,)
    )

    pedido = cursor.fetchone()

    conexion.close()

    return pedido
def eliminar_pedido(pedido_id):
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()

    cursor.execute(
        """
        DELETE FROM pedidos
        WHERE id = ?
        """,
        (pedido_id,)
    )

    conexion.commit()
    conexion.close()