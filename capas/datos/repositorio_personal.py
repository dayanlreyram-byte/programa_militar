"""
CAPA DE DATOS — Repositorio de personal militar.
Guarda y lee exactamente lo que le pasan (ya encriptado por la capa de
negocio); no conoce la lógica de encriptación.
"""
from datetime import datetime
from capas.datos.conexion_bd import obtener_conexion


def insertar_personal(nombres_enc, apellidos_enc, id_militar_enc, grado_enc, unidad_enc,
                       cedula_enc, telefono_enc, ciudad_enc, direccion_enc, barrio_enc,
                       genero_enc, edad_enc, registrado_por):
    conn = obtener_conexion()
    cur = conn.execute(
        """INSERT INTO personal_militar
           (nombres, apellidos, id_militar, grado, unidad,
            cedula, telefono, ciudad, direccion, barrio, genero, edad,
            registrado_por, fecha_registro)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (nombres_enc, apellidos_enc, id_militar_enc, grado_enc, unidad_enc,
         cedula_enc, telefono_enc, ciudad_enc, direccion_enc, barrio_enc, genero_enc, edad_enc,
         registrado_por, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    nuevo_id = cur.lastrowid
    conn.close()
    return nuevo_id


def listar_personal():
    conn = obtener_conexion()
    filas = conn.execute("SELECT * FROM personal_militar ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(f) for f in filas]


def obtener_personal(personal_id):
    conn = obtener_conexion()
    fila = conn.execute(
        "SELECT * FROM personal_militar WHERE id = ?", (personal_id,)
    ).fetchone()
    conn.close()
    return dict(fila) if fila else None


def actualizar_hoja_vida(personal_id, cedula_enc, telefono_enc, ciudad_enc, direccion_enc,
                          barrio_enc, genero_enc, edad_enc):
    conn = obtener_conexion()
    conn.execute(
        """UPDATE personal_militar
           SET cedula = ?, telefono = ?, ciudad = ?, direccion = ?,
               barrio = ?, genero = ?, edad = ?
           WHERE id = ?""",
        (cedula_enc, telefono_enc, ciudad_enc, direccion_enc, barrio_enc, genero_enc,
         edad_enc, personal_id),
    )
    conn.commit()
    conn.close()
