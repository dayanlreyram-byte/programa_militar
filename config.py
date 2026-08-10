"""
Configuración global de la aplicación.
Centraliza rutas y constantes usadas por las distintas capas.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carpeta donde se guardan la base de datos y la clave de encriptación
DATA_DIR = os.path.join(BASE_DIR, "almacenamiento")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "acceso_militar.db")
KEY_PATH = os.path.join(DATA_DIR, "secret.key")

# Roles del sistema
ROL_ADMIN = "admin"
ROL_OPERADOR = "operador"

# Estados de un ingreso (Apartado 1/2): solo el admin puede autorizar/rechazar
ESTADO_PENDIENTE = "pendiente"
ESTADO_AUTORIZADO = "autorizado"
ESTADO_RECHAZADO = "rechazado"

# Parámetros de hashing (PBKDF2-HMAC-SHA256)
HASH_ITERACIONES = 100_000
SALT_BYTES = 16

# Longitud por defecto de claves/códigos generados
LONGITUD_CLAVE_RECUPERACION = 12
LONGITUD_CODIGO_UNICO = 8

APP_TITLE = "Sistema de Control de Acceso — Dirección General del Ejército"
