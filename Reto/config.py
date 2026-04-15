"""Carga y expone la configuracion del proyecto basada en variables de entorno."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Notas del reto
# - Decido utilizar config.py para cargar las variables de entorno de una manera ordenada
# y separada de main.py
# - Uso la libreria dotenv que facilita la lectura del archivo .env, el archivo .env
# debe tener definido cada configuración como CLAVE=valor
# - Defina un dataclass con cada item de la configuracion para facilitar su uso
# - Dataclass(frozen=True) se implementa para que una vez se instancia un objeto este no se puede
# modificar. Aplica para la configuración que se carga una sola vez y no se puede modificar.

@dataclass(frozen=True)
class Settings:
    """Agrupa los valores de configuracion requeridos por la aplicacion.

    Attributes:
        agencia_api_key: Clave usada para autenticar peticiones protegidas.
        external_api_url: URL de la API publica usada por el briefing.
        database_path: Ruta del archivo SQLite.
        external_api_timeout: Tiempo maximo de espera para la API externa.
    """

    agencia_api_key: str
    external_api_url: str
    database_path: str
    external_api_timeout: float


def get_settings() -> Settings:
    """Carga el archivo .env y devuelve la configuracion activa.

    Returns:
        Settings: Configuracion de la aplicacion.
    """
    load_dotenv()
    return Settings(
        agencia_api_key=os.getenv("AGENCIA_API_KEY"),
        external_api_url=os.getenv("EXTERNAL_API_URL", "https://api.adviceslip.com/advice"),
        database_path=os.getenv("DATABASE_PATH", "agencia.db"),
        external_api_timeout=float(os.getenv("EXTERNAL_API_TIMEOUT", "5")),
    )
