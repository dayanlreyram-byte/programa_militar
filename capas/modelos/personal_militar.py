"""Entidad de dominio: datos del personal militar (ya desencriptados)."""
from dataclasses import dataclass


@dataclass
class PersonalMilitar:
    id: int
    nombres: str
    apellidos: str
    id_militar: str
    grado: str
    unidad: str
    # --- Datos de Hoja de Vida ---
    cedula: str
    telefono: str
    ciudad: str
    direccion: str
    barrio: str
    genero: str
    edad: str
    registrado_por: str
    fecha_registro: str

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def hoja_vida_completa(self):
        """La hoja de vida se completa en una ventana aparte; mientras
        la cédula esté vacía, se considera pendiente."""
        return bool(self.cedula.strip())
