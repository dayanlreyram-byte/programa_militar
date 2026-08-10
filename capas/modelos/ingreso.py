"""Entidad de dominio: registro de ingreso (apartados 1 y 2 verificados),
con su flujo de autorización por parte del admin."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Ingreso:
    id: int
    personal_id: int
    area_visita: str
    proposito: str
    codigo_unico: str
    fecha_hora: str
    registrado_por: str
    estado: str
    autorizado_por: Optional[str] = None
    fecha_autorizacion: Optional[str] = None
    nombre_completo_personal: str = ""
