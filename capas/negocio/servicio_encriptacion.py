"""
CAPA DE NEGOCIO — Encriptación simétrica AES de datos sensibles.

Usa cryptography.fernet.Fernet, que implementa AES-128 en modo CBC con
autenticación HMAC (evita tanto la lectura como la manipulación de los
datos cifrados). La clave se genera una sola vez y se guarda en
secret.key; toda la app reutiliza esa misma clave para poder
desencriptar lo ya guardado.
"""
import os
from cryptography.fernet import Fernet, InvalidToken
from config import KEY_PATH


def _obtener_clave():
    if not os.path.exists(KEY_PATH):
        clave = Fernet.generate_key()
        with open(KEY_PATH, "wb") as archivo_clave:
            archivo_clave.write(clave)
    with open(KEY_PATH, "rb") as archivo_clave:
        return archivo_clave.read()


_cipher_suite = Fernet(_obtener_clave())


def encriptar(texto_plano: str) -> str:
    """Encripta un string y devuelve el token cifrado como texto (para SQLite)."""
    if texto_plano is None:
        texto_plano = ""
    token = _cipher_suite.encrypt(texto_plano.encode("utf-8"))
    return token.decode("utf-8")


def desencriptar(token_texto: str) -> str:
    """Desencripta un token guardado en BD y devuelve el texto original."""
    try:
        datos = _cipher_suite.decrypt(token_texto.encode("utf-8"))
        return datos.decode("utf-8")
    except InvalidToken:
        return "[DATO CORRUPTO O CLAVE INVÁLIDA]"
