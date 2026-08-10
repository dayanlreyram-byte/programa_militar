"""
CAPA DE NEGOCIO — Apartados de verificación cifrados:
  Apartado 1: identidad del soldado (id militar + código único).
  Apartado 2: propósito del ingreso (área de visita + motivo).

Además, el flujo de autorización: todo ingreso se registra en estado
'pendiente' y solo el rol admin puede autorizarlo o rechazarlo — el
operador puede capturar el ingreso pero no decidir si se permite.
"""
from capas.datos import repositorio_ingresos as repo
from capas.negocio import servicio_encriptacion as cripto
from capas.negocio import servicio_permisos as permisos
from capas.negocio import generador_claves
from capas.negocio.servicio_personal import obtener_personal_desencriptado, ErrorPersonal
from capas.modelos.ingreso import Ingreso
from config import ESTADO_AUTORIZADO, ESTADO_RECHAZADO

PROPOSITOS_VALIDOS = ["Misión", "Reunión", "Asignación", "Visita", "Otro"]


class ErrorVerificacion(Exception):
    pass


def registrar_ingreso(personal_id: int, area_visita: str, proposito: str, usuario_actual: str):
    """
    Genera el Apartado 1 (código único de identidad) y guarda el
    Apartado 2 (propósito/área) encriptados, ligados al personal_id.
    El ingreso queda en estado 'pendiente' hasta que un admin lo
    autorice o rechace. Devuelve el código único en claro (comprobante).
    """
    if not area_visita.strip():
        raise ErrorVerificacion("El área de visita es obligatoria.")
    if proposito not in PROPOSITOS_VALIDOS:
        raise ErrorVerificacion("Selecciona un propósito de ingreso válido.")

    try:
        obtener_personal_desencriptado(personal_id)
    except ErrorPersonal as error:
        raise ErrorVerificacion(str(error))

    codigo_unico = generador_claves.generar_codigo_unico()

    repo.insertar_ingreso(
        personal_id=personal_id,
        area_visita_enc=cripto.encriptar(area_visita.strip()),
        proposito_enc=cripto.encriptar(proposito),
        codigo_unico_enc=cripto.encriptar(codigo_unico),
        registrado_por=usuario_actual,
    )
    return codigo_unico


def _desencriptar_fila(fila: dict) -> Ingreso:
    return Ingreso(
        id=fila["id"],
        personal_id=fila["personal_id"],
        area_visita=cripto.desencriptar(fila["area_visita"]),
        proposito=cripto.desencriptar(fila["proposito"]),
        codigo_unico=cripto.desencriptar(fila["codigo_unico"]),
        fecha_hora=fila["fecha_hora"],
        registrado_por=fila["registrado_por"],
        estado=fila["estado"],
        autorizado_por=fila["autorizado_por"],
        fecha_autorizacion=fila["fecha_autorizacion"],
        nombre_completo_personal=f'{fila["nombres_personal"]} {fila["apellidos_personal"]}',
    )


def listar_ingresos(rol: str):
    filas = repo.listar_ingresos()
    resultado = []
    for fila in filas:
        ingreso = _desencriptar_fila(fila)
        if not permisos.puede_ver_datos_desencriptados(rol):
            ingreso.codigo_unico = permisos.enmascarar(ingreso.codigo_unico)
            ingreso.proposito = permisos.enmascarar(ingreso.proposito)
        resultado.append(ingreso)
    return resultado


def verificar_identidad(personal_id: int, codigo_ingresado: str, rol: str) -> bool:
    """Compara el código único ingresado contra los registrados para esa
    persona (Apartado 1 de verificación de identidad)."""
    if not permisos.puede_ver_datos_desencriptados(rol):
        raise ErrorVerificacion("No tienes permisos para verificar identidad.")
    filas = [f for f in repo.listar_ingresos() if f["personal_id"] == personal_id]
    for fila in filas:
        if cripto.desencriptar(fila["codigo_unico"]) == codigo_ingresado.strip():
            return True
    return False


def autorizar_ingreso(ingreso_id: int, usuario_actual: str, rol: str):
    """Solo el admin puede autorizar un ingreso pendiente."""
    if not permisos.puede_autorizar_ingresos(rol):
        raise ErrorVerificacion("No tienes permisos para autorizar ingresos.")
    if repo.obtener_ingreso(ingreso_id) is None:
        raise ErrorVerificacion("No se encontró ese registro de ingreso.")
    repo.actualizar_estado(ingreso_id, ESTADO_AUTORIZADO, usuario_actual)


def rechazar_ingreso(ingreso_id: int, usuario_actual: str, rol: str):
    """Solo el admin puede rechazar un ingreso pendiente."""
    if not permisos.puede_autorizar_ingresos(rol):
        raise ErrorVerificacion("No tienes permisos para rechazar ingresos.")
    if repo.obtener_ingreso(ingreso_id) is None:
        raise ErrorVerificacion("No se encontró ese registro de ingreso.")
    repo.actualizar_estado(ingreso_id, ESTADO_RECHAZADO, usuario_actual)
