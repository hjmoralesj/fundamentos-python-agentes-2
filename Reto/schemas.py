"""Modelos Pydantic usados por la API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Notas del reto
# - Se definan esquemas utilizando Pydantic para aprovechar las capacidad de validación automática
# de tipos y funciones adicionales para validar longitud y valores de los datos de entrada al API.
# - Según mi investigación es más limpio y sencillo utilizar Field, Literal que
# @field_validator para las validaciones requeridas en el contexto de este proyecto.
# - Los esquemas definidos son tanto para las entradas al API como las respuestas.
# - Algunas de los esquemas pueden anidar otros esquemas para completar el objeto que se responde
# en alguna API. ej: BriefingResponse

class AgentCreate(BaseModel):
    """Payload de entrada para crear un agente."""

    nombre: str = Field(min_length=1)
    rol: str = Field(min_length=1)
    energia: int = Field(ge=0)


class AgentResponse(BaseModel):
    """Representa la respuesta publica de un agente."""

    nombre: str
    rol: str
    energia: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)


class AgentUpdate(BaseModel):
    """Payload de entrada para actualizar un agente."""

    rol: str = Field(min_length=1)
    energia: int = Field(ge=0)


class MessageCreate(BaseModel):
    """Payload de entrada para registrar un mensaje."""

    remitente: str = Field(min_length=1)
    destinatario: str = Field(min_length=1)
    contenido: str = Field(min_length=1)


class MessageResponse(BaseModel):
    """Representa un mensaje almacenado en la API."""

    id: int
    remitente: str
    destinatario: str
    contenido: str
    timestamp: datetime


class MissionCreate(BaseModel):
    """Payload de entrada para crear una mision."""

    titulo: str = Field(min_length=1)
    descripcion: str | None = None
    agente_asignado: str = Field(min_length=1)
    energia_requerida: int = Field(gt=0)
    prioridad: Literal["baja", "media", "alta"] = "media"
    deadline_at: datetime | None = None


class MissionComplete(BaseModel):
    """Payload usado para completar una mision."""

    result: str = Field(min_length=1)


class MissionResponse(BaseModel):
    """Representa la respuesta publica de una mision."""

    id: int
    titulo: str
    descripcion: str | None = None
    agente_asignado: str
    estado: Literal["pendiente", "en_curso", "completada", "fallida"]
    energia_requerida: int = Field(ge=0)
    prioridad: Literal["baja", "media", "alta"]
    deadline_at: datetime | None = None
    created_at: datetime
    completed_at: datetime | None = None
    updated_at: datetime
    result: str | None = None


class AgentDeleteResponse(BaseModel):
    """Representa el resultado del borrado de un agente."""

    mensaje: str
    misiones_fallidas: list[MissionResponse]


class HealthResponse(BaseModel):
    """Respuesta simple para verificar el estado del servicio."""

    status: str
    timestamp: datetime


class BriefingResponse(BaseModel):
    """Estructura del briefing combinado local y externo."""

    agente: AgentResponse
    misiones: list[MissionResponse]
    dato_externo: str
    fuente_externa: str
