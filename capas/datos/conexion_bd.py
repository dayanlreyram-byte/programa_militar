"""
CAPA DE DATOS
Maneja la conexión a SQLite y la creación del esquema.
Ninguna otra capa debe abrir sqlite3 directamente: todo pasa por aquí
o por los repositorios de esta misma capa.
"""
import sqlite3
from config import DB_PATH


def obtener_conexion():
    """Devuelve una conexión SQLite con claves foráneas habilitadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_esquema():
    """Crea las tablas si no existen. Se llama una vez al arrancar la app."""
    conn = obtener_conexion()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            clave_recuperacion_hash TEXT NOT NULL,
            clave_recuperacion_salt TEXT NOT NULL,
            rol TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS personal_militar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            id_militar TEXT NOT NULL,
            grado TEXT NOT NULL,
            unidad TEXT NOT NULL,
            cedula TEXT NOT NULL,
            telefono TEXT NOT NULL,
            ciudad TEXT NOT NULL,
            direccion TEXT NOT NULL,
            barrio TEXT NOT NULL,
            genero TEXT NOT NULL,
            edad TEXT NOT NULL,
            registrado_por TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personal_id INTEGER NOT NULL,
            area_visita TEXT NOT NULL,
            proposito TEXT NOT NULL,
            codigo_unico TEXT NOT NULL,
            fecha_hora TEXT NOT NULL,
            registrado_por TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            autorizado_por TEXT,
            fecha_autorizacion TEXT,
            FOREIGN KEY (personal_id) REFERENCES personal_militar(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bitacora_accesos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            rol TEXT NOT NULL,
            exitoso INTEGER NOT NULL,
            fecha_hora TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
