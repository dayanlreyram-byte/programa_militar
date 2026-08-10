"""
CAPA DE NEGOCIO — Control de permisos por rol.

- admin: puede ver los datos desencriptados, administrar usuarios y
  consultar el historial completo de ingresos.
- operador: solo puede capturar personal e ingresos; ve los campos
  sensibles enmascarados.
"""
from config import ROL_ADMIN, ROL_OPERADOR


def puede_ver_datos_desencriptados(rol: str) -> bool:
    return rol == ROL_ADMIN


def puede_administrar_usuarios(rol: str) -> bool:
    return rol == ROL_ADMIN


def puede_autorizar_ingresos(rol: str) -> bool:
    """Solo el admin decide si un ingreso queda autorizado o rechazado;
    el operador únicamente puede capturarlo (queda 'pendiente')."""
    return rol == ROL_ADMIN


def enmascarar(_texto: str) -> str:
    return "••••••••"
