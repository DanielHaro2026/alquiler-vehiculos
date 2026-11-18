import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE = Path(
    os.environ.get(
        "DATABASE_PATH",
        str(BASE_DIR / "instance" / "alquiler.db")
    )
)


def get_db():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_db():
    conn = get_db()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            placa TEXT NOT NULL UNIQUE,
            precio_dia REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Disponible'
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            dni TEXT NOT NULL UNIQUE,
            telefono TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS alquileres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            vehiculo_id INTEGER NOT NULL,
            fecha_alquiler TEXT NOT NULL,
            fecha_devolucion TEXT NOT NULL,
            total REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Activo',
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)
        );
    """)

    conn.commit()
    conn.close()
