"""Entidad de dominio: Usuario del sistema."""
from dataclasses import dataclass


@dataclass
class Usuario:
    username: str
    rol: str
    fecha_registro: str = ""

    @property
    def es_admin(self):
        return self.rol == "admin"
