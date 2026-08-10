"""
CAPA DE DATOS — Repositorio de usuarios.
Solo hace SQL puro: no valida reglas de negocio ni encripta/hashea nada
(eso corresponde a la capa de negocio).
"""
from datetime import datetime
from capas.datos.conexion_bd import obtener_conexion


def existe_usuario(username):
    conn = obtener_conexion()
    fila = conn.execute(
        "SELECT 1 FROM usuarios WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return fila is not None


def contar_usuarios():
    conn = obtener_conexion()
    fila = conn.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()
    conn.close()
    return fila["total"]


def insertar_usuario(username, password_hash, salt, clave_recuperacion_hash,
                      clave_recuperacion_salt, rol):
    conn = obtener_conexion()
    conn.execute(
        """INSERT INTO usuarios
           (username, password_hash, salt, clave_recuperacion_hash,
            clave_recuperacion_salt, rol, fecha_registro)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (username, password_hash, salt, clave_recuperacion_hash, clave_recuperacion_salt,
         rol, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def actualizar_password(username, nuevo_password_hash, nuevo_salt):
    conn = obtener_conexion()
    conn.execute(
        "UPDATE usuarios SET password_hash = ?, salt = ? WHERE username = ?",
        (nuevo_password_hash, nuevo_salt, username),
    )
    conn.commit()
    conn.close()


def obtener_usuario(username):
    conn = obtener_conexion()
    fila = conn.execute(
        "SELECT * FROM usuarios WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return dict(fila) if fila else None


def listar_usuarios():
    conn = obtener_conexion()
    filas = conn.execute(
        "SELECT id, username, rol, fecha_registro FROM usuarios ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(f) for f in filas]


def actualizar_rol(username, nuevo_rol):
    conn = obtener_conexion()
    conn.execute("UPDATE usuarios SET rol = ? WHERE username = ?", (nuevo_rol, username))
    conn.commit()
    conn.close()
