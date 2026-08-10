"""
CAPA DE NEGOCIO — Hashing de contraseñas.

Usa PBKDF2-HMAC-SHA256 con salt aleatorio (equivalente al "SHA-256 + salt"
solicitado en el planteamiento), tal como recomienda la documentación
oficial de Python para almacenar contraseñas de forma irreversible.
Nunca se guarda ni se puede recuperar la contraseña original: solo se
compara el hash calculado contra el hash almacenado.
"""
import hashlib
import hmac
import os
from config import HASH_ITERACIONES, SALT_BYTES


def generar_salt():
    return os.urandom(SALT_BYTES).hex()


def hash_password(password: str, salt_hex: str) -> str:
    """Deriva un hash irreversible de la contraseña usando el salt dado."""
    salt = bytes.fromhex(salt_hex)
    derivado = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, HASH_ITERACIONES
    )
    return derivado.hex()


def verificar_password(password: str, password_hash: str, salt_hex: str) -> bool:
    """Recalcula el hash con el mismo salt y compara de forma segura."""
    hash_calculado = hash_password(password, salt_hex)
    return hmac.compare_digest(hash_calculado, password_hash)
