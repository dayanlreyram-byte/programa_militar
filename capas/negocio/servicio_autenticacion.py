"""
CAPA DE NEGOCIO — Autenticación y registro de usuarios.
Aplica las reglas del negocio y delega la persistencia al repositorio
de la capa de datos.
"""
import re
from capas.datos import repositorio_usuarios as repo
from capas.negocio import servicio_hashing as hashing
from capas.negocio import generador_claves
from config import ROL_ADMIN, ROL_OPERADOR


class ErrorAutenticacion(Exception):
    pass


# Requisitos de una contraseña segura (se muestran también en el login/registro)
REQUISITOS_PASSWORD = [
    "Mínimo 8 caracteres",
    "Al menos una letra mayúscula (A-Z)",
    "Al menos una letra minúscula (a-z)",
    "Al menos un número (0-9)",
    "Al menos un símbolo (!@#$%&*-_+=...)",
]


def validar_fortaleza_password(password: str):
    """Devuelve la lista de requisitos que la contraseña NO cumple."""
    faltantes = []
    if len(password) < 8:
        faltantes.append(REQUISITOS_PASSWORD[0])
    if not re.search(r"[A-ZÁÉÍÓÚÑ]", password):
        faltantes.append(REQUISITOS_PASSWORD[1])
    if not re.search(r"[a-záéíóúñ]", password):
        faltantes.append(REQUISITOS_PASSWORD[2])
    if not re.search(r"[0-9]", password):
        faltantes.append(REQUISITOS_PASSWORD[3])
    if not re.search(r"[!@#$%&*\-_+=.,;:¿?¡!()\[\]{}]", password):
        faltantes.append(REQUISITOS_PASSWORD[4])
    return faltantes


def registrar_usuario(username: str, password: str):
    """
    Registra un nuevo usuario. El primer usuario del sistema queda como
    admin automáticamente; los siguientes como operador.
    Devuelve la clave de recuperación generada (mostrarla UNA sola vez).
    """
    username = username.strip()
    if not username or not password:
        raise ErrorAutenticacion("Usuario y contraseña son obligatorios.")

    faltantes = validar_fortaleza_password(password)
    if faltantes:
        raise ErrorAutenticacion("La contraseña no es lo bastante segura. Falta: "
                                  + "; ".join(faltantes) + ".")
    if repo.existe_usuario(username):
        raise ErrorAutenticacion("Ese nombre de usuario ya existe.")

    rol = ROL_ADMIN if repo.contar_usuarios() == 0 else ROL_OPERADOR

    salt = hashing.generar_salt()
    password_hash = hashing.hash_password(password, salt)

    clave_recuperacion = generador_claves.generar_clave_segura()
    salt_clave = hashing.generar_salt()
    clave_recuperacion_hash = hashing.hash_password(clave_recuperacion, salt_clave)

    repo.insertar_usuario(username, password_hash, salt, clave_recuperacion_hash,
                           salt_clave, rol)

    return rol, clave_recuperacion


def iniciar_sesion(username: str, password: str):
    """Valida credenciales, deja registro en la bitácora de accesos
    (éxito o fallo) y devuelve el rol si son correctas."""
    from capas.datos import repositorio_bitacora as bitacora  # import local: evita ciclos

    username_limpio = username.strip()
    usuario = repo.obtener_usuario(username_limpio)

    if usuario is None or not hashing.verificar_password(
            password, usuario["password_hash"], usuario["salt"]):
        bitacora.registrar_acceso(username_limpio, exitoso=False,
                                   rol=usuario["rol"] if usuario else "desconocido")
        raise ErrorAutenticacion("Usuario o contraseña incorrectos.")

    bitacora.registrar_acceso(username_limpio, exitoso=True, rol=usuario["rol"])
    return usuario["rol"]


def listar_usuarios():
    return repo.listar_usuarios()


def listar_bitacora_accesos():
    from capas.datos import repositorio_bitacora as bitacora
    return bitacora.listar_accesos()


def cambiar_rol(username: str, nuevo_rol: str):
    if nuevo_rol not in (ROL_ADMIN, ROL_OPERADOR):
        raise ErrorAutenticacion("Rol inválido.")
    repo.actualizar_rol(username, nuevo_rol)


def recuperar_password(username: str, clave_recuperacion: str, nueva_password: str):
    """Permite definir una nueva contraseña si la clave de recuperación
    coincide con la que se generó (y se guardó hasheada) al registrarse."""
    username = username.strip()
    usuario = repo.obtener_usuario(username)
    if usuario is None:
        raise ErrorAutenticacion("Ese usuario no existe.")

    if not hashing.verificar_password(clave_recuperacion.strip(),
                                       usuario["clave_recuperacion_hash"],
                                       usuario["clave_recuperacion_salt"]):
        raise ErrorAutenticacion("La clave de recuperación no es correcta.")

    if len(nueva_password) < 6:
        raise ErrorAutenticacion("La nueva contraseña debe tener al menos 6 caracteres.")

    faltantes = validar_fortaleza_password(nueva_password)
    if faltantes:
        raise ErrorAutenticacion("La nueva contraseña no es lo bastante segura. Falta: "
                                  + "; ".join(faltantes) + ".")

    nuevo_salt = hashing.generar_salt()
    nuevo_hash = hashing.hash_password(nueva_password, nuevo_salt)
    repo.actualizar_password(username, nuevo_hash, nuevo_salt)
