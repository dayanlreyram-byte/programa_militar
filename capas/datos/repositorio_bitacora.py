"""
CAPA DE DATOS — Bitácora de inicios de sesión (auditoría).
Registra cada intento de login, exitoso o fallido, para trazabilidad.
"""
from datetime import datetime
from capas.datos.conexion_bd import obtener_conexion


def registrar_acceso(username: str, exitoso: bool, rol: str):
    conn = obtener_conexion()
    conn.execute(
        """INSERT INTO bitacora_accesos (username, rol, exitoso, fecha_hora)
           VALUES (?, ?, ?, ?)""",
        (username, rol, 1 if exitoso else 0, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def listar_accesos(limite: int = 200):
    conn = obtener_conexion()
    filas = conn.execute(
        "SELECT * FROM bitacora_accesos ORDER BY id DESC LIMIT ?", (limite,)
    ).fetchall()
    conn.close()
    return [dict(f) for f in filas]
