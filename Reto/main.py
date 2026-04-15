"""API FastAPI para gestionar agentes, mensajes, misiones y briefings."""

import logging
import os
import sqlite3
from datetime import datetime, timezone

import requests
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from agente import reconstruir_agente_desde_fila
from config import Settings, get_settings
from db import (
    actualizar_agente,
    actualizar_energia_agente,
    actualizar_estado_mision,
    consultar_agente_por_nombre,
    consultar_mensajes_por_destinatario,
    consultar_mision_por_id,
    consultar_misiones_por_agente,
    consultar_agentes,
    inicializar_bd,
    crear_mision,
    eliminar_agente,
    fallar_misiones_activas_por_agente,
    registrar_agente,
    registrar_mensaje,
)
from schemas import (
    AgentCreate,
    AgentDeleteResponse,
    AgentResponse,
    AgentUpdate,
    BriefingResponse,
    HealthResponse,
    MessageCreate,
    MessageResponse,
    MissionComplete,
    MissionCreate,
    MissionResponse,
)

# Notas del reto
# - Configuación de logging: INFO deja trazabilidad operativa sin ruido; WARNING marca degradaciones
# recuperables; ERROR y exception se reservan para fallos reales del servidor.
# - Se crea handler manejar_excepcion_no_controlada para manejar cualquier
# excepción no controlada que suceda en cualquier endpoint.
# - En todos los endpoints se define un response_model que corresponde a un esquema de Pydantic.
# - Usando dependencies me aseguro de ejecutar funciones requeridas por cada endpoint antes del
# inicio de la ejecución del resto de lógica de cada función asociada al endpoint.
# - Se usa model_validate para comprobar que la entrada del usuario corresponda al esquema de
# Pydantic definido para los endpoints que requieran validar entradas del usuario.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def consultar_agente(
    settings: Settings,
    nombre: str,
    detalle: str = "Agente no encontrado",
    contexto_log: str = "Consulta de agente inexistente",
) -> dict[str, object]:
    """Recupera un agente o lanza un error 404 si no existe.

    Args:
        settings: Configuracion activa de la aplicacion.
        nombre: Nombre del agente a recuperar.
        detalle: Mensaje a devolver en la respuesta HTTP.
        contexto_log: Prefijo del mensaje de auditoria.

    Returns:
        dict[str, object]: Registro del agente encontrado.

    Raises:
        HTTPException: Si el agente no existe.
    """
    agente = consultar_agente_por_nombre(settings.database_path, nombre)
    if agente is None:
        logger.warning("%s: %s", contexto_log, nombre)
        raise HTTPException(status_code=404, detail=detalle)
    return agente


def consultar_mision(
    settings: Settings,
    mision_id: int,
    detalle: str = "Mision no encontrada",
    contexto_log: str = "Consulta de mision inexistente",
) -> dict[str, object]:
    """Recupera una mision o lanza un error 404 si no existe.

    Args:
        settings: Configuracion activa de la aplicacion.
        mision_id: Identificador numerico de la mision.
        detalle: Mensaje a devolver en la respuesta HTTP.
        contexto_log: Prefijo del mensaje de auditoria.

    Returns:
        dict[str, object]: Registro de la mision encontrada.

    Raises:
        HTTPException: Si la mision no existe.
    """
    mision = consultar_mision_por_id(settings.database_path, mision_id)
    if mision is None:
        logger.warning("%s: %s", contexto_log, mision_id)
        raise HTTPException(status_code=404, detail=detalle)
    return mision


def require_api_key(
    x_api_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    """Valida la API key enviada en el header de la solicitud.

    Args:
        x_api_key: API key recibida desde el header `X-API-KEY`.
        settings: Configuracion activa de la aplicacion.

    Raises:
        HTTPException: Si la API key no coincide con la configurada.
    """
    if x_api_key != settings.agencia_api_key:
        logger.warning("Autenticacion fallida por API key invalida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key invalida",
        )


def obtener_consejo_externo(settings: Settings) -> str:
    """Consulta Advice Slip y resuelve un fallback si la fuente externa falla.

    Args:
        settings: Configuracion activa de la aplicacion.

    Returns:
        str: Consejo obtenido desde la API externa o un mensaje alterno
            cuando la integracion no responde o llega con formato invalido.
    """
    try:
        response = requests.get(
            settings.external_api_url,
            timeout=settings.external_api_timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["slip"]["advice"]
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Fallback de briefing activado por fallo externo: %s", exc)
        return "La fuente externa no respondio; se entrega briefing con datos locales."
    except (KeyError, TypeError) as exc:
        logger.warning(
            "Advice Slip respondio con formato inesperado: %s",
            exc,
        )
        return "La fuente externa respondio sin un consejo interpretable."


app = FastAPI(
    title="Agencia de Misiones",
    version="1.0.0",
)

def inicializar_datos() -> None:
    """Inicializa la base y los datos semilla solo en la primera ejecucion."""
    settings = get_settings()

    try:
        archivo_bd_existe = os.path.exists(settings.database_path)
        if not archivo_bd_existe:
            inicializar_bd(settings.database_path)
            logger.info(
                "Base de datos creada con datos iniciales en %s",
                settings.database_path,
            )
    except sqlite3.Error:
        logger.exception("Error al inicializar la base de datos")
        raise


inicializar_datos()


@app.exception_handler(Exception)
async def manejar_excepcion_no_controlada(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Registra excepciones no controladas y responde con error generico.

    Args:
        request: Solicitud HTTP que disparo la excepcion.
        exc: Excepcion no controlada.

    Returns:
        JSONResponse: Respuesta generica de error interno.
    """
    logger.exception(
        "Fallo inesperado en %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )


@app.get("/", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    """Verifica que la API este disponible.

    Returns:
        HealthResponse: Estado de salud del servicio.
    """
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc))


@app.get(
    "/agentes/{nombre}",
    response_model=AgentResponse,
    dependencies=[Depends(require_api_key)],
)
def obtener_agente(nombre: str, settings: Settings = Depends(get_settings)) -> AgentResponse:
    """Devuelve el detalle de un agente por nombre.

    Args:
        nombre: Nombre del agente a consultar.
        settings: Configuracion activa de la aplicacion.

    Returns:
        AgentResponse: Agente encontrado.

    Raises:
        HTTPException: Si el agente no existe.
    """
    agente = consultar_agente(settings, nombre)
    return AgentResponse.model_validate(agente)


@app.get(
    "/agentes/",
    response_model=list[AgentResponse],
    dependencies=[Depends(require_api_key)],
)
def listar_agentes(settings: Settings = Depends(get_settings)) -> list[AgentResponse]:
    """Lista todos los agentes registrados en el sistema.

    Args:
        settings: Configuracion activa de la aplicacion.

    Returns:
        list[AgentResponse]: Lista de agentes disponibles.
    """
    return [
        AgentResponse.model_validate(agente)
        for agente in consultar_agentes(settings.database_path)
    ]


@app.post(
    "/agentes/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def crear_agente(
    payload: AgentCreate,
    settings: Settings = Depends(get_settings),
) -> AgentResponse:
    """Crea un nuevo agente en la base de datos.

    Args:
        payload: Datos validados del agente a crear.
        settings: Configuracion activa de la aplicacion.

    Returns:
        AgentResponse: Agente creado.

    Raises:
        HTTPException: Si ya existe un agente con el mismo nombre.
    """
    try:
        agente = registrar_agente(
            settings.database_path,
            nombre=payload.nombre,
            rol=payload.rol,
            energia=payload.energia,
        )
    except sqlite3.IntegrityError as exc:
        logger.warning("Intento de crear agente duplicado: %s", payload.nombre)
        raise HTTPException(
            status_code=409,
            detail="Ya existe un agente con ese nombre",
        ) from exc
    except sqlite3.Error:
        logger.exception("Fallo SQL al crear agente %s", payload.nombre)
        raise
    logger.info("Agente creado: %s con rol %s", payload.nombre, payload.rol)
    return AgentResponse.model_validate(agente)


@app.put(
    "/agentes/{nombre}",
    response_model=AgentResponse,
    dependencies=[Depends(require_api_key)],
)
def actualizar_agente_por_nombre(
    nombre: str,
    payload: AgentUpdate,
    settings: Settings = Depends(get_settings),
) -> AgentResponse:
    """Actualiza el rol y la energia de un agente existente.

    Args:
        nombre: Nombre del agente a actualizar.
        payload: Datos validados de actualizacion.
        settings: Configuracion activa de la aplicacion.

    Returns:
        AgentResponse: Agente actualizado.

    Raises:
        HTTPException: Si el agente no existe.
    """
    consultar_agente(
        settings,
        nombre,
        contexto_log="Intento de actualizar agente inexistente",
    )

    try:
        actualizado = actualizar_agente(
            settings.database_path,
            nombre=nombre,
            rol=payload.rol,
            energia=payload.energia,
        )
    except sqlite3.Error:
        logger.exception("Fallo SQL al actualizar agente %s", nombre)
        raise

    logger.info(
        "Agente actualizado: %s con rol %s y energia %s",
        nombre,
        payload.rol,
        payload.energia,
    )
    return AgentResponse.model_validate(actualizado)


@app.delete(
    "/agentes/{nombre}",
    response_model=AgentDeleteResponse,
    dependencies=[Depends(require_api_key)],
)
def eliminar_agente_por_nombre(
    nombre: str,
    settings: Settings = Depends(get_settings),
) -> AgentDeleteResponse:
    """Elimina un agente y marca como fallidas sus misiones activas.

    Args:
        nombre: Nombre del agente a eliminar.
        settings: Configuracion activa de la aplicacion.

    Returns:
        AgentDeleteResponse: Resumen de la eliminacion.

    Raises:
        HTTPException: Si el agente no existe.
    """
    consultar_agente(
        settings,
        nombre,
        contexto_log="Intento de eliminar agente inexistente",
    )

    motivo = "Mision marcada como fallida porque el agente asignado fue eliminado del sistema."

    try:
        misiones_fallidas = fallar_misiones_activas_por_agente(
            settings.database_path,
            agente_asignado=nombre,
            result=motivo,
        )
        eliminar_agente(settings.database_path, nombre)
    except sqlite3.Error:
        logger.exception("Fallo SQL al eliminar agente %s", nombre)
        raise

    logger.info(
        "Agente eliminado: %s; misiones activas marcadas como fallidas: %s",
        nombre,
        len(misiones_fallidas),
    )
    return AgentDeleteResponse(
        mensaje=f"Agente {nombre} eliminado correctamente",
        misiones_fallidas=[
            MissionResponse.model_validate(mision)
            for mision in misiones_fallidas
        ],
    )


@app.post(
    "/mensajes",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def crear_mensaje(
    payload: MessageCreate,
    settings: Settings = Depends(get_settings),
) -> MessageResponse:
    """Registra un mensaje entre dos agentes existentes.

    Args:
        payload: Datos validados del mensaje.
        settings: Configuracion activa de la aplicacion.

    Returns:
        MessageResponse: Mensaje persistido.

    Raises:
        HTTPException: Si remitente o destinatario no existen.
    """
    consultar_agente(
        settings,
        payload.remitente,
        detalle="El remitente no existe",
        contexto_log="Mensaje rechazado por remitente inexistente",
    )
    consultar_agente(
        settings,
        payload.destinatario,
        detalle="El destinatario no existe",
        contexto_log="Mensaje rechazado por destinatario inexistente",
    )

    try:
        mensaje = registrar_mensaje(
            settings.database_path,
            remitente=payload.remitente,
            destinatario=payload.destinatario,
            contenido=payload.contenido,
        )
    except sqlite3.Error:
        logger.exception(
            "Fallo SQL al registrar mensaje de %s para %s",
            payload.remitente,
            payload.destinatario,
        )
        raise
    logger.info(
        "Mensaje registrado de %s para %s",
        payload.remitente,
        payload.destinatario,
    )
    return MessageResponse.model_validate(mensaje)


@app.get(
    "/mensajes/{nombre}",
    response_model=list[MessageResponse],
    dependencies=[Depends(require_api_key)],
)
def obtener_mensajes(
    nombre: str,
    settings: Settings = Depends(get_settings),
) -> list[MessageResponse]:
    """Devuelve la bandeja de entrada de un destinatario.

    Args:
        nombre: Nombre del destinatario.
        settings: Configuracion activa de la aplicacion.

    Returns:
        list[MessageResponse]: Mensajes recibidos por el agente.
    """
    return [
        MessageResponse.model_validate(mensaje)
        for mensaje in consultar_mensajes_por_destinatario(
            settings.database_path,
            nombre,
        )
    ]


@app.post(
    "/misiones/",
    response_model=MissionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def crear_mision_para_agente(
    payload: MissionCreate,
    settings: Settings = Depends(get_settings),
) -> MissionResponse:
    """Crea una mision para un agente existente.

    Args:
        payload: Datos validados de la mision.
        settings: Configuracion activa de la aplicacion.

    Returns:
        MissionResponse: Mision creada.

    Raises:
        HTTPException: Si el agente asignado no existe.
    """
    consultar_agente(
        settings,
        payload.agente_asignado,
        detalle="El agente asignado no existe",
        contexto_log="Creacion de mision rechazada por agente inexistente",
    )

    try:
        mision = crear_mision(
            settings.database_path,
            titulo=payload.titulo,
            descripcion=payload.descripcion,
            agente_asignado=payload.agente_asignado,
            energia_requerida=payload.energia_requerida,
            prioridad=payload.prioridad,
            deadline_at=payload.deadline_at.isoformat()
            if payload.deadline_at
            else None,
        )
    except sqlite3.Error:
        logger.exception("Fallo SQL al crear mision %s", payload.titulo)
        raise
    logger.info(
        "Mision creada: %s para %s",
        payload.titulo,
        payload.agente_asignado,
    )
    return MissionResponse.model_validate(mision)


@app.get(
    "/misiones/{mision_id}",
    response_model=MissionResponse,
    dependencies=[Depends(require_api_key)],
)
def obtener_mision(mision_id: int, settings: Settings = Depends(get_settings)) -> MissionResponse:
    """Consulta el detalle de una mision por identificador.

    Args:
        mision_id: Identificador numerico de la mision.
        settings: Configuracion activa de la aplicacion.

    Returns:
        MissionResponse: Mision encontrada.

    Raises:
        HTTPException: Si la mision no existe.
    """
    mision = consultar_mision(settings, mision_id)
    return MissionResponse.model_validate(mision)


@app.get(
    "/agentes/{nombre}/misiones",
    response_model=list[MissionResponse],
    dependencies=[Depends(require_api_key)],
)
def listar_misiones_por_agente(
    nombre: str,
    settings: Settings = Depends(get_settings),
) -> list[MissionResponse]:
    """Lista las misiones asignadas a un agente.

    Args:
        nombre: Nombre del agente asignado.
        settings: Configuracion activa de la aplicacion.

    Returns:
        list[MissionResponse]: Misiones asociadas al agente.
    """
    return [
        MissionResponse.model_validate(mision)
        for mision in consultar_misiones_por_agente(
            settings.database_path,
            nombre,
        )
    ]


@app.post(
    "/misiones/{mision_id}/completar",
    response_model=MissionResponse,
    dependencies=[Depends(require_api_key)],
)
def completar_mision_por_id(
    mision_id: int,
    payload: MissionComplete,
    settings: Settings = Depends(get_settings),
) -> MissionResponse:
    """Completa una mision usando la clase real del agente para consumir energia.

    Args:
        mision_id: Identificador numerico de la mision.
        payload: Resultado textual de la ejecucion.
        settings: Configuracion activa de la aplicacion.

    Returns:
        MissionResponse: Mision actualizada como completada.

    Raises:
        HTTPException: Si la mision o el agente no existen, si ya estaba
            completada o si no hay energia suficiente.
    """
    mision = consultar_mision(
        settings,
        mision_id,
        contexto_log="Intento de completar mision inexistente",
    )
    if mision["estado"] == "completada":
        logger.warning("Intento de recompletar mision %s", mision_id)
        raise HTTPException(
            status_code=400,
            detail="La mision ya estaba completada",
        )

    agente_fila = consultar_agente_por_nombre(
        settings.database_path,
        mision["agente_asignado"],
    )
    if agente_fila is None:
        logger.error(
            "Inconsistencia: la mision %s apunta a un agente inexistente %s",
            mision_id,
            mision["agente_asignado"],
        )
        raise HTTPException(
            status_code=404,
            detail="El agente asignado no existe",
        )

    agente = reconstruir_agente_desde_fila(agente_fila)
    if agente is None:
        logger.error("No fue posible reconstruir el agente de la mision %s", mision_id)
        raise HTTPException(
            status_code=500,
            detail="No fue posible reconstruir el agente",
        )

    try:
        agente.consumir_energia(int(mision["energia_requerida"]))
    except ValueError as exc:
        logger.warning("Mision %s no completada por energia insuficiente: %s", mision_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        actualizar_energia_agente(
            settings.database_path,
            agente.nombre,
            agente.energia,
        )
        actualizada = actualizar_estado_mision(
            settings.database_path,
            mision_id,
            "completada",
            result=payload.result,
        )
    except sqlite3.Error:
        logger.exception("Fallo SQL al completar la mision %s", mision_id)
        raise
    logger.info(
        "Mision completada: %s por %s; energia restante %s",
        mision_id,
        agente.nombre,
        agente.energia,
    )
    return MissionResponse.model_validate(actualizada)


@app.get(
    "/briefing/{nombre}",
    response_model=BriefingResponse,
    dependencies=[Depends(require_api_key)],
)
def obtener_briefing(
    nombre: str,
    settings: Settings = Depends(get_settings),
) -> BriefingResponse:
    """Construye un briefing con datos locales y una fuente publica externa.

    Args:
        nombre: Nombre del agente a consultar.
        settings: Configuracion activa de la aplicacion.

    Returns:
        BriefingResponse: Briefing consolidado del agente.

    Raises:
        HTTPException: Si el agente no existe.
    """
    agente = consultar_agente(
        settings,
        nombre,
        contexto_log="Briefing solicitado para agente inexistente",
    )

    fuente_externa = settings.external_api_url
    dato_externo = obtener_consejo_externo(settings)

    misiones = consultar_misiones_por_agente(settings.database_path, nombre)
    return BriefingResponse(
        agente=AgentResponse.model_validate(agente),
        misiones=[
            MissionResponse.model_validate(mision)
            for mision in misiones
        ],
        dato_externo=dato_externo,
        fuente_externa=fuente_externa,
    )
