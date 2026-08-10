"""
CAPA DE DATOS — Repositorio de ingresos (apartados de verificación
1: identidad/código único, y 2: propósito/área de visita), más el
flujo de autorización: todo ingreso nace en estado 'pendiente' y
solo el admin puede pasarlo a 'autorizado' o 'rechazado'.
"""
from datetime import datetime
from capas.datos.conexion_bd import obtener_conexion
from config import ESTADO_PENDIENTE


def insertar_ingreso(personal_id, area_visita_enc, proposito_enc, codigo_unico_enc, registrado_por):
    conn = obtener_conexion()
    conn.execute(
        """INSERT INTO ingresos
           (personal_id, area_visita, proposito, codigo_unico, fecha_hora,
            registrado_por, estado)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (personal_id, area_visita_enc, proposito_enc, codigo_unico_enc,
         datetime.now().isoformat(timespec="seconds"), registrado_por, ESTADO_PENDIENTE),
    )
    conn.commit()
    conn.close()


def listar_ingresos():
    conn = obtener_conexion()
    filas = conn.execute("""
        SELECT ingresos.*, personal_militar.nombres AS nombres_personal,
               personal_militar.apellidos AS apellidos_personal
        FROM ingresos
        JOIN personal_militar ON personal_militar.id = ingresos.personal_id
        ORDER BY ingresos.id DESC
    """).fetchall()
    conn.close()
    return [dict(f) for f in filas]


def obtener_ingreso(ingreso_id):
    conn = obtener_conexion()
    fila = conn.execute("SELECT * FROM ingresos WHERE id = ?", (ingreso_id,)).fetchone()
    conn.close()
    return dict(fila) if fila else None


def actualizar_estado(ingreso_id, nuevo_estado, autorizado_por):
    conn = obtener_conexion()
    conn.execute(
        """UPDATE ingresos SET estado = ?, autorizado_por = ?, fecha_autorizacion = ?
           WHERE id = ?""",
        (nuevo_estado, autorizado_por, datetime.now().isoformat(timespec="seconds"), ingreso_id),
    )
    conn.commit()
    conn.close()
