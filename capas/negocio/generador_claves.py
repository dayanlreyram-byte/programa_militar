"""
CAPA DE NEGOCIO — Generador de claves y códigos seguros.

Usa el módulo `secrets` (criptográficamente seguro, a diferencia de
`random`) para producir claves de recuperación y códigos únicos de
verificación de identidad.
"""
import secrets
import string
from config import LONGITUD_CLAVE_RECUPERACION, LONGITUD_CODIGO_UNICO


def generar_clave_segura(longitud: int = LONGITUD_CLAVE_RECUPERACION) -> str:
    """Clave alfanumérica + símbolos, para recuperación de cuenta."""
    caracteres = string.ascii_letters + string.digits + "!@#$%&*-_+="
    return "".join(secrets.choice(caracteres) for _ in range(longitud))


def generar_codigo_unico(longitud: int = LONGITUD_CODIGO_UNICO) -> str:
    """Código único alfanumérico en mayúsculas para el Apartado 1
    (verificación de identidad), fácil de leer/transcribir."""
    caracteres = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(caracteres) for _ in range(longitud))
