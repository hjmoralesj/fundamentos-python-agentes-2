"""Funciones de acceso a la base de datos SQLite."""

from datetime import datetime, timezone
import sqlite3
from contextlib import closing
from typing import Any

# Notas del reto
# - Se utiliza closing para asegurar cierre de la conexión a SQLite
#  en vez de usar estructura try, finally.
# - Cada función recibe la ruta al archivo de la base de datos. Esto desacopla este archivo de
# la gestión de la configuración. Facilita pruebas sin cambiar db.py
# - Como practica recomendada se retornan las filas actualizadas o insertadas luego de la ejecución
# de la sentencia en la base de datos.
# - El cálculo de fechas y estados de la misión es controlado por la lógica de la base de datos y
# no de los endpoints asegurando la validez de los datos en este punto.
# - Se decide que cuando un agente es eliminado si tiene misiones asignadas que no hayan sido
# terminadas ("fallida", "completada") entonces se actualizan a "fallida".
# - Al abrir la conexión se configura el objeto para que los datos de las filas puedan leerse
# por nombre de columna y no por posición haciendo mas legible el código.


def now_iso() -> str:
    """Devuelve la fecha y hora actual en formato ISO 8601 UTC.

    Returns:
        str: Fecha actual serializada en UTC.
    """
    return datetime.now(timezone.utc).isoformat()


def get_connection(db_path: str) -> sqlite3.Connection:
    """Crea una conexion SQLite.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.

    Returns:
        sqlite3.Connection: Conexion lista para trabajar con la base de datos.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def crear_tablas(db_path: str) -> None:
    """Crea las tablas necesarias para agentes, mensajes y misiones.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
    """
    with closing(get_connection(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agentes (
                nombre TEXT PRIMARY KEY,
                rol TEXT,
                energia INTEGER
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remitente TEXT,
                destinatario TEXT,
                contenido TEXT,
                timestamp TEXT
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS misiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                agente_asignado TEXT,
                estado TEXT,
                energia_requerida INTEGER,
                prioridad TEXT,
                deadline_at TEXT,
                created_at TEXT,
                completed_at TEXT,
                updated_at TEXT,
                result TEXT
            );
            """
        )
        conn.commit()


def inicializar_bd(db_path: str) -> None:
    """Crea tablas y registra datos semilla para una base recien creada.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
    """
    crear_tablas(db_path)

    registrar_agente(db_path, "Niobe", "capitana", 95)
    registrar_agente(db_path, "Link", "operativo", 85)
    registrar_agente(db_path, "Ghost", "analista", 90)

    registrar_mensaje(
        db_path,
        "Niobe",
        "Link",
        "Confirma la ventana segura para el acceso al objetivo.",
    )
    registrar_mensaje(
        db_path,
        "Link",
        "Niobe",
        "Ruta despejada por el corredor sur durante ocho minutos.",
    )
    registrar_mensaje(
        db_path,
        "Ghost",
        "Niobe",
        "Necesito tu evaluacion del trafico antes del despliegue.",
    )
    registrar_mensaje(
        db_path,
        "Niobe",
        "Ghost",
        "Patron de vigilancia estable, sin refuerzos visibles.",
    )
    registrar_mensaje(
        db_path,
        "Link",
        "Ghost",
        "Equipo de campo listo para iniciar la extraccion.",
    )

    crear_mision(
        db_path,
        "Mapear sensores perimetrales",
        "Construir un mapa de puntos ciegos alrededor del complejo.",
        "Ghost",
        12,
        "media",
        None,
    )
    mision_en_curso = crear_mision(
        db_path,
        "Asegurar acceso secundario",
        "Mantener abierta una ruta alterna para evacuacion.",
        "Link",
        18,
        "alta",
        None,
    )
    mision_completada = crear_mision(
        db_path,
        "Coordinar ventana de salida",
        "Sincronizar al equipo con el transporte de extraccion.",
        "Niobe",
        10,
        "baja",
        None,
    )

    actualizar_estado_mision(
        db_path,
        int(mision_en_curso["id"]),
        "en_curso",
    )
    actualizar_estado_mision(
        db_path,
        int(mision_completada["id"]),
        "completada",
        "La extraccion fue coordinada dentro del tiempo previsto.",
    )


def registrar_agente(
    db_path: str,
    nombre: str,
    rol: str,
    energia: int,
) -> dict[str, Any]:
    """Inserta un agente y devuelve la fila creada.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        nombre: Nombre del agente.
        rol: Rol asociado al agente.
        energia: Energia inicial del agente.

    Returns:
        dict[str, Any]: Registro persistido del agente.
    """
    with closing(get_connection(db_path)) as conn:
        conn.execute(
            "INSERT INTO agentes (nombre, rol, energia) VALUES (?, ?, ?)",
            (nombre, rol, energia),
        )
        conn.commit()
    return consultar_agente_por_nombre(db_path, nombre)


def consultar_agente_por_nombre(
    db_path: str,
    nombre: str,
) -> dict[str, Any] | None:
    """Busca un agente por su nombre.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        nombre: Nombre del agente a consultar.

    Returns:
        dict[str, Any] | None: Registro del agente o `None`.
    """
    with closing(get_connection(db_path)) as conn:
        fila = conn.execute(
            "SELECT nombre, rol, energia FROM agentes WHERE nombre = ?",
            (nombre,),
        ).fetchone()
    return dict(fila) if fila else None


def consultar_agentes(db_path: str) -> list[dict[str, Any]]:
    """Devuelve todos los agentes registrados.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.

    Returns:
        list[dict[str, Any]]: Lista de agentes almacenados.
    """
    with closing(get_connection(db_path)) as conn:
        filas = conn.execute(
            "SELECT nombre, rol, energia FROM agentes ORDER BY nombre"
        ).fetchall()
    return [dict(fila) for fila in filas]


def actualizar_energia_agente(
    db_path: str,
    nombre: str,
    energia: int,
) -> None:
    """Actualiza la energia persistida de un agente.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        nombre: Nombre del agente a actualizar.
        energia: Nuevo valor de energia.
    """
    with closing(get_connection(db_path)) as conn:
        conn.execute(
            "UPDATE agentes SET energia = ? WHERE nombre = ?",
            (energia, nombre),
        )
        conn.commit()


def actualizar_agente(
    db_path: str,
    nombre: str,
    rol: str,
    energia: int,
) -> dict[str, Any] | None:
    """Actualiza el rol y la energia de un agente.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        nombre: Nombre del agente a actualizar.
        rol: Nuevo rol del agente.
        energia: Nuevo valor de energia.

    Returns:
        dict[str, Any] | None: Registro actualizado del agente o `None`.
    """
    with closing(get_connection(db_path)) as conn:
        conn.execute(
            "UPDATE agentes SET rol = ?, energia = ? WHERE nombre = ?",
            (rol, energia, nombre),
        )
        conn.commit()
    return consultar_agente_por_nombre(db_path, nombre)


def eliminar_agente(
    db_path: str,
    nombre: str,
) -> None:
    """Elimina un agente de la base de datos.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        nombre: Nombre del agente a eliminar.
    """
    with closing(get_connection(db_path)) as conn:
        conn.execute(
            "DELETE FROM agentes WHERE nombre = ?",
            (nombre,),
        )
        conn.commit()


def registrar_mensaje(
    db_path: str,
    remitente: str,
    destinatario: str,
    contenido: str,
) -> dict[str, Any]:
    """Guarda un mensaje y devuelve la fila insertada.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        remitente: Nombre del agente que envia el mensaje.
        destinatario: Nombre del agente que recibe el mensaje.
        contenido: Contenido del mensaje.

    Returns:
        dict[str, Any]: Registro persistido del mensaje.
    """
    timestamp = now_iso()
    with closing(get_connection(db_path)) as conn:
        cursor = conn.execute(
            """
            INSERT INTO mensajes (remitente, destinatario, contenido, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (remitente, destinatario, contenido, timestamp),
        )
        mensaje_id = cursor.lastrowid
        conn.commit()
        fila = conn.execute(
            """
            SELECT id, remitente, destinatario, contenido, timestamp
            FROM mensajes
            WHERE id = ?
            """,
            (mensaje_id,),
        ).fetchone()
    return dict(fila)


def consultar_mensajes_por_destinatario(
    db_path: str,
    destinatario: str,
) -> list[dict[str, Any]]:
    """Lista los mensajes recibidos por un destinatario.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        destinatario: Nombre del agente destinatario.

    Returns:
        list[dict[str, Any]]: Mensajes ordenados por timestamp.
    """
    with closing(get_connection(db_path)) as conn:
        filas = conn.execute(
            """
            SELECT id, remitente, destinatario, contenido, timestamp
            FROM mensajes
            WHERE destinatario = ?
            ORDER BY timestamp
            """,
            (destinatario,),
        ).fetchall()
    return [dict(fila) for fila in filas]


def crear_mision(
    db_path: str,
    titulo: str,
    descripcion: str | None,
    agente_asignado: str,
    energia_requerida: int,
    prioridad: str,
    deadline_at: str | None,
) -> dict[str, Any]:
    """Crea una mision y devuelve su registro persistido.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        titulo: Titulo de la mision.
        descripcion: Descripcion opcional de la mision.
        agente_asignado: Nombre del agente asignado.
        energia_requerida: Energia necesaria para completarla.
        prioridad: Prioridad operativa de la mision.
        deadline_at: Fecha limite en formato ISO 8601.

    Returns:
        dict[str, Any]: Registro persistido de la mision.
    """
    marca_tiempo = now_iso()
    with closing(get_connection(db_path)) as conn:
        cursor = conn.execute(
            """
            INSERT INTO misiones (
                titulo, descripcion, agente_asignado, estado, energia_requerida,
                prioridad, deadline_at, created_at, completed_at, updated_at, result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                titulo,
                descripcion,
                agente_asignado,
                "pendiente",
                energia_requerida,
                prioridad,
                deadline_at,
                marca_tiempo,
                None,
                marca_tiempo,
                None,
            ),
        )
        mision_id = cursor.lastrowid
        conn.commit()
    return consultar_mision_por_id(db_path, int(mision_id))


def consultar_mision_por_id(
    db_path: str,
    mision_id: int,
) -> dict[str, Any] | None:
    """Busca una mision por su identificador.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        mision_id: Identificador numerico de la mision.

    Returns:
        dict[str, Any] | None: Registro de la mision o `None`.
    """
    with closing(get_connection(db_path)) as conn:
        fila = conn.execute(
            """
            SELECT id, titulo, descripcion, agente_asignado, estado, energia_requerida,
                   prioridad, deadline_at, created_at, completed_at, updated_at, result
            FROM misiones
            WHERE id = ?
            """,
            (mision_id,),
        ).fetchone()
    return dict(fila) if fila else None


def consultar_misiones_por_agente(
    db_path: str,
    agente_asignado: str,
) -> list[dict[str, Any]]:
    """Obtiene las misiones asignadas a un agente.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        agente_asignado: Nombre del agente asignado.

    Returns:
        list[dict[str, Any]]: Misiones del agente.
    """
    with closing(get_connection(db_path)) as conn:
        filas = conn.execute(
            """
            SELECT id, titulo, descripcion, agente_asignado, estado, energia_requerida,
                   prioridad, deadline_at, created_at, completed_at, updated_at, result
            FROM misiones
            WHERE agente_asignado = ?
            ORDER BY id
            """,
            (agente_asignado,),
        ).fetchall()
    return [dict(fila) for fila in filas]


def actualizar_estado_mision(
    db_path: str,
    mision_id: int,
    estado: str,
    result: str | None = None,
) -> dict[str, Any] | None:
    """Actualiza el estado de una mision y ajusta sus marcas temporales.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        mision_id: Identificador numerico de la mision.
        estado: Nuevo estado de la mision.
        result: Resultado o motivo asociado al cambio de estado.

    Returns:
        dict[str, Any] | None: Registro actualizado de la mision o `None`.
    """
    marca_tiempo = now_iso()
    completed_at = marca_tiempo if estado in ("completada", "fallida") else None
    with closing(get_connection(db_path)) as conn:
        conn.execute(
            """
            UPDATE misiones
            SET estado = ?, completed_at = ?, updated_at = ?, result = ?
            WHERE id = ?
            """,
            (estado, completed_at, marca_tiempo, result, mision_id),
        )
        conn.commit()
    return consultar_mision_por_id(db_path, mision_id)


def fallar_misiones_activas_por_agente(
    db_path: str,
    agente_asignado: str,
    result: str,
) -> list[dict[str, Any]]:
    """Marca como fallidas las misiones activas de un agente.

    Args:
        db_path: Ruta del archivo de base de datos SQLite.
        agente_asignado: Nombre del agente cuyas misiones deben fallar.
        result: Motivo por el que la mision fue fallida.

    Returns:
        list[dict[str, Any]]: Misiones afectadas luego de la actualizacion.
    """
    ids: list[int] = []
    with closing(get_connection(db_path)) as conn:
        filas = conn.execute(
            """
            SELECT id
            FROM misiones
            WHERE agente_asignado = ?
              AND estado IN (?, ?)
            ORDER BY id
            """,
            (agente_asignado, "pendiente", "en_curso"),
        ).fetchall()

        ids = [int(fila["id"]) for fila in filas]

    misiones_actualizadas = []
    for mision_id in ids:
        mision = actualizar_estado_mision(
            db_path,
            mision_id,
            "fallida",
            result,
        )
        if mision is not None:
            misiones_actualizadas.append(mision)
    return misiones_actualizadas
