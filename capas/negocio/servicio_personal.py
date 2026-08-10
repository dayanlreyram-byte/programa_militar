"""
CAPA DE NEGOCIO — Registro y consulta del personal militar.

Se maneja en DOS PASOS independientes (cada uno con su propia
ventana en la capa de presentación):
  1) Registro militar (nombres, apellidos, ID militar, grado, unidad).
  2) Hoja de vida (cédula, teléfono, ciudad, dirección, barrio,
     género, edad) — se completa después, para una persona que ya
     exista en el paso 1.

Ambos pasos validan y encriptan los datos antes de guardarlos, y se
desencriptan al leerlos (respetando permisos por rol).
"""
import re
from capas.datos import repositorio_personal as repo
from capas.negocio import servicio_encriptacion as cripto
from capas.negocio import servicio_permisos as permisos
from capas.modelos.personal_militar import PersonalMilitar


class ErrorPersonal(Exception):
    pass


CAMPOS_MILITARES = ["nombres", "apellidos", "id_militar", "grado", "unidad"]
CAMPOS_HOJA_VIDA = ["cedula", "telefono", "ciudad", "direccion", "barrio", "genero", "edad"]

# Patrón y mensaje de error por campo. La capa de presentación usa
# estos mismos patrones para restringir lo que se puede teclear; aquí
# se vuelven a validar como última barrera (nunca hay que confiar
# solo en la validación de la interfaz).
REGLAS_CAMPOS = {
    "nombres":    (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ ]{2,40}$", "solo letras y espacios (2 a 40 caracteres)"),
    "apellidos":  (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ ]{2,40}$", "solo letras y espacios (2 a 40 caracteres)"),
    "id_militar": (r"^[A-Za-z0-9\-]{4,15}$", "letras, números y guiones (4 a 15 caracteres)"),
    "unidad":     (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ0-9 ]{2,40}$", "letras, números y espacios (2 a 40 caracteres)"),
    "cedula":     (r"^[0-9]{6,10}$", "solo números (6 a 10 dígitos)"),
    "telefono":   (r"^[0-9]{7,10}$", "solo números (7 a 10 dígitos)"),
    "ciudad":     (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ ]{2,30}$", "solo letras y espacios (2 a 30 caracteres)"),
    "direccion":  (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ0-9#\-.,° ]{5,60}$",
                   "letras, números y # - . , ° (5 a 60 caracteres)"),
    "barrio":     (r"^[A-Za-zÁÉÍÓÚÑáéíóúñ0-9 ]{2,30}$", "letras, números y espacios (2 a 30 caracteres)"),
    "edad":       (r"^[0-9]{1,3}$", "solo números"),
}

EDAD_MINIMA = 18
EDAD_MAXIMA = 70


def _validar_campos(datos: dict, campos: list):
    for campo in campos:
        valor = datos.get(campo, "").strip()
        if not valor:
            raise ErrorPersonal(f"El campo '{campo}' es obligatorio.")
        patron, descripcion = REGLAS_CAMPOS.get(campo, (None, None))
        if patron and not re.match(patron, valor):
            raise ErrorPersonal(f"El campo '{campo}' debe contener {descripcion}.")


# ----------------------------------------------------------------------
# Paso 1: registro militar
# ----------------------------------------------------------------------
def registrar_personal(datos: dict, usuario_actual: str) -> int:
    """Registra los datos militares de una persona. La hoja de vida
    queda vacía (pendiente) hasta que se complete en su propia
    ventana con `actualizar_hoja_vida`."""
    _validar_campos(datos, CAMPOS_MILITARES)

    nuevo_id = repo.insertar_personal(
        nombres_enc=cripto.encriptar(datos["nombres"].strip()),
        apellidos_enc=cripto.encriptar(datos["apellidos"].strip()),
        id_militar_enc=cripto.encriptar(datos["id_militar"].strip()),
        grado_enc=cripto.encriptar(datos["grado"].strip()),
        unidad_enc=cripto.encriptar(datos["unidad"].strip()),
        cedula_enc=cripto.encriptar(""),
        telefono_enc=cripto.encriptar(""),
        ciudad_enc=cripto.encriptar(""),
        direccion_enc=cripto.encriptar(""),
        barrio_enc=cripto.encriptar(""),
        genero_enc=cripto.encriptar(""),
        edad_enc=cripto.encriptar(""),
        registrado_por=usuario_actual,
    )
    return nuevo_id


# ----------------------------------------------------------------------
# Paso 2: hoja de vida (ventana aparte)
# ----------------------------------------------------------------------
def actualizar_hoja_vida(personal_id: int, datos: dict, usuario_actual: str):
    """Completa/actualiza la hoja de vida de una persona ya registrada
    en el paso militar. Todos los campos de hoja de vida son
    obligatorios en este paso."""
    if repo.obtener_personal(personal_id) is None:
        raise ErrorPersonal("Primero debes registrar a la persona en 'Personal Militar'.")

    _validar_campos(datos, CAMPOS_HOJA_VIDA)

    edad = int(datos["edad"].strip())
    if not (EDAD_MINIMA <= edad <= EDAD_MAXIMA):
        raise ErrorPersonal(f"La edad debe estar entre {EDAD_MINIMA} y {EDAD_MAXIMA} años.")

    repo.actualizar_hoja_vida(
        personal_id=personal_id,
        cedula_enc=cripto.encriptar(datos["cedula"].strip()),
        telefono_enc=cripto.encriptar(datos["telefono"].strip()),
        ciudad_enc=cripto.encriptar(datos["ciudad"].strip()),
        direccion_enc=cripto.encriptar(datos["direccion"].strip()),
        barrio_enc=cripto.encriptar(datos["barrio"].strip()),
        genero_enc=cripto.encriptar(datos["genero"].strip()),
        edad_enc=cripto.encriptar(datos["edad"].strip()),
    )


def _desencriptar_fila(fila: dict) -> PersonalMilitar:
    return PersonalMilitar(
        id=fila["id"],
        nombres=cripto.desencriptar(fila["nombres"]),
        apellidos=cripto.desencriptar(fila["apellidos"]),
        id_militar=cripto.desencriptar(fila["id_militar"]),
        grado=cripto.desencriptar(fila["grado"]),
        unidad=cripto.desencriptar(fila["unidad"]),
        cedula=cripto.desencriptar(fila["cedula"]),
        telefono=cripto.desencriptar(fila["telefono"]),
        ciudad=cripto.desencriptar(fila["ciudad"]),
        direccion=cripto.desencriptar(fila["direccion"]),
        barrio=cripto.desencriptar(fila["barrio"]),
        genero=cripto.desencriptar(fila["genero"]),
        edad=cripto.desencriptar(fila["edad"]),
        registrado_por=fila["registrado_por"],
        fecha_registro=fila["fecha_registro"],
    )


def listar_personal(rol: str):
    """Devuelve la lista de personal. Si el rol no tiene permiso de ver
    datos desencriptados, los campos sensibles vienen enmascarados."""
    filas = repo.listar_personal()
    resultado = []
    for fila in filas:
        persona = _desencriptar_fila(fila)
        if not permisos.puede_ver_datos_desencriptados(rol):
            persona.nombres = permisos.enmascarar(persona.nombres)
            persona.apellidos = permisos.enmascarar(persona.apellidos)
            persona.id_militar = permisos.enmascarar(persona.id_militar)
            if persona.hoja_vida_completa:
                persona.cedula = permisos.enmascarar(persona.cedula)
                persona.telefono = permisos.enmascarar(persona.telefono)
                persona.direccion = permisos.enmascarar(persona.direccion)
                persona.barrio = permisos.enmascarar(persona.barrio)
        resultado.append(persona)
    return resultado


def obtener_personal_desencriptado(personal_id: int) -> PersonalMilitar:
    """Uso interno (p. ej. para generar el Apartado 1); ignora permisos
    de visualización porque no expone el resultado directamente al operador."""
    fila = repo.obtener_personal(personal_id)
    if fila is None:
        raise ErrorPersonal("No se encontró el registro de personal.")
    return _desencriptar_fila(fila)


def listar_opciones_para_combo(solo_pendientes_hoja_vida: bool = False):
    """(id, 'Nombre Apellido — ID militar') para poblar un combobox.
    Si `solo_pendientes_hoja_vida` es True, solo incluye personas cuya
    hoja de vida todavía no se ha completado."""
    filas = repo.listar_personal()
    opciones = []
    for fila in filas:
        persona = _desencriptar_fila(fila)
        if solo_pendientes_hoja_vida and persona.hoja_vida_completa:
            continue
        etiqueta = f"{persona.id} — {persona.nombre_completo} ({persona.grado})"
        opciones.append((persona.id, etiqueta))
    return opciones
