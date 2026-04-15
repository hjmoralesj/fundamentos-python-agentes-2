"""Cliente HTTP de demostracion para probar el flujo end-to-end de la API."""

from pprint import pprint
import requests
from config import get_settings

# Notas del reto:
# - Se utiliza la librería pprint para mejorar la visualización en consola de los objetos que se
# imprimen como parte de la solución del reto.
# - Se crean funciones para reutilizar comportamientos que mejoran la lectura del código principal
# del demo del API.
# - El demo crea agentes, envia mensajes, elimina agente y ejecuta un briefing.

BASE_URL = "http://127.0.0.1:8000"


def imprimir_respuesta(
    label: str,
    response: requests.Response,
) -> dict | list:
    """Imprime y devuelve el contenido JSON de una respuesta HTTP exitosa.

    Args:
        label: Titulo corto para mostrar en consola.
        response: Respuesta HTTP recibida.

    Returns:
        dict | list: Cuerpo JSON parseado.
    """
    print(f"\n=== {label} ===")
    print(f"Status: {response.status_code}")
    response.raise_for_status()
    data = response.json()
    pprint(data)
    return data


def crear_o_recuperar_agente(
    headers: dict[str, str],
    payload: dict[str, object],
) -> dict:
    """Crea un agente o recupera el existente para permitir reejecutar el script.

    Args:
        headers: Headers HTTP requeridos por la API.
        payload: Datos del agente a crear.

    Returns:
        dict: Datos del agente creado o recuperado.
    """
    response = requests.post(
        f"{BASE_URL}/agentes/",
        headers=headers,
        json=payload,
        timeout=5,
    )
    print(f"\n=== Crear agente {payload['nombre']} ===")
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        return imprimir_respuesta(f"Crear agente {payload['nombre']}", response)

    if response.status_code == 409:
        existente = requests.get(
            f"{BASE_URL}/agentes/{payload['nombre']}",
            headers=headers,
            timeout=5,
        )
        return imprimir_respuesta(f"Recuperar agente {payload['nombre']}", existente)

    response.raise_for_status()
    return {}


def crear_mision_demo(
    headers: dict[str, str],
    payload: dict[str, object],
) -> dict:
    """Crea una mision y devuelve la respuesta parseada.

    Args:
        headers: Headers HTTP requeridos por la API.
        payload: Datos de la mision a crear.

    Returns:
        dict: Datos de la mision creada.
    """
    response = requests.post(
        f"{BASE_URL}/misiones/",
        headers=headers,
        json=payload,
        timeout=5,
    )
    return imprimir_respuesta(f"Crear mision {payload['titulo']}", response)


def main() -> None:
    """Ejecuta la demostracion completa del proyecto contra la API local."""
    settings = get_settings()
    headers = {"X-API-KEY": settings.agencia_api_key}

    health = requests.get(f"{BASE_URL}/", timeout=5)
    imprimir_respuesta("Healthcheck", health)

    neo = crear_o_recuperar_agente(
        headers, {"nombre": "Neo", "rol": "admin", "energia": 100}
    )
    trinity = crear_o_recuperar_agente(
        headers,
        {"nombre": "Trinity", "rol": "operativo", "energia": 80},
    )
    morpheus = crear_o_recuperar_agente(
        headers,
        {"nombre": "Morpheus", "rol": "estratega", "energia": 90},
    )
    cypher = crear_o_recuperar_agente(
        headers,
        {"nombre": "Cypher", "rol": "infiltrado", "energia": 70},
    )

    mision_neo = crear_mision_demo(
        headers,
        {
            "titulo": "Recuperar artefacto",
            "descripcion": "Infiltracion en zona controlada para extraer un paquete.",
            "agente_asignado": neo["nombre"],
            "energia_requerida": 25,
            "prioridad": "alta",
        },
    )
    crear_mision_demo(
        headers,
        {
            "titulo": "Cubrir extraccion",
            "descripcion": "Asegurar la zona perimetral mientras el equipo sale.",
            "agente_asignado": trinity["nombre"],
            "energia_requerida": 20,
            "prioridad": "media",
        },
    )
    crear_mision_demo(
        headers,
        {
            "titulo": "Analizar señal",
            "descripcion": "Revisar trafico y detectar interferencias.",
            "agente_asignado": morpheus["nombre"],
            "energia_requerida": 15,
            "prioridad": "media",
        },
    )
    crear_mision_demo(
        headers,
        {
            "titulo": "Desactivar alarma",
            "descripcion": "Ingresar al sistema y suspender la alerta principal.",
            "agente_asignado": cypher["nombre"],
            "energia_requerida": 18,
            "prioridad": "alta",
        },
    )
    crear_mision_demo(
        headers,
        {
            "titulo": "Abrir ruta secundaria",
            "descripcion": "Preparar una salida alterna en caso de contingencia.",
            "agente_asignado": cypher["nombre"],
            "energia_requerida": 12,
            "prioridad": "baja",
        },
    )

    completada = requests.post(
        f"{BASE_URL}/misiones/{mision_neo['id']}/completar",
        headers=headers,
        json={"result": "Artefacto asegurado y extraido sin bajas."},
        timeout=5,
    )
    imprimir_respuesta("Completar mision", completada)

    mensaje = requests.post(
        f"{BASE_URL}/mensajes",
        headers=headers,
        json={
            "remitente": neo["nombre"],
            "destinatario": trinity["nombre"],
            "contenido": "Mision completada. Preparar ruta de salida.",
        },
        timeout=5,
    )
    imprimir_respuesta("Enviar mensaje", mensaje)

    bandeja = requests.get(
        f"{BASE_URL}/mensajes/Trinity",
        headers=headers,
        timeout=5,
    )
    imprimir_respuesta("Leer bandeja de Trinity", bandeja)

    eliminar_cypher = requests.delete(
        f"{BASE_URL}/agentes/{cypher['nombre']}",
        headers=headers,
        timeout=5,
    )
    imprimir_respuesta("Eliminar agente Cypher", eliminar_cypher)

    misiones_cypher = requests.get(
        f"{BASE_URL}/agentes/{cypher['nombre']}/misiones",
        timeout=5,
    )
    imprimir_respuesta("Consultar misiones fallidas de Cypher", misiones_cypher)

    response = requests.get(
        f"{BASE_URL}/briefing/{morpheus['nombre']}",
        timeout=10,
    )
    imprimir_respuesta("Briefing de Morpheus", response)


if __name__ == "__main__":
    main()
