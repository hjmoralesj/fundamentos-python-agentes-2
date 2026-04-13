# -----------------------------------------------------------#
# Semana 5 - Sesion 1: Persistencia con SQLite
# -----------------------------------------------------------#
# Hasta ahora, cada vez que cierras Python, todo desaparece.
# Los agentes, los mensajes, los datos... se pierden en la RAM.
# Hoy aprenderemos a darle MEMORIA PERMANENTE a nuestros agentes
# usando SQLite: una base de datos que vive en un solo archivo.
#
# Instrucciones:
# 1. Lee cada capitulo de arriba hacia abajo
# 2. Descomenta el bloque de codigo indicado
# 3. Ejecuta el script completo: python S5_sesion_1.py
# 4. Observa la salida, experimenta, y escribe tu CONCLUSION
# 5. Avanza al siguiente capitulo
# -----------------------------------------------------------#

import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agentes.db")

# -----------------------------------------------------------#
# SECCION A: Funciones del modulo (siempre disponibles)
# -----------------------------------------------------------#
# Estas funciones NO estan comentadas porque otros archivos
# las importan. No las modifiques a menos que se indique.
# -----------------------------------------------------------#


def crear_tablas() -> None:
    """Crea las tablas agentes y mensajes si no existen."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agentes (
            nombre TEXT PRIMARY KEY,
            rol TEXT,
            energia INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente TEXT,
            destinatario TEXT,
            contenido TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def registrar_agente(nombre: str, rol: str, energia: int) -> str:
    """Registra un agente en la base de datos. Retorna mensaje de exito o error."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO agentes (nombre, rol, energia) VALUES (?, ?, ?)",
            (nombre, rol, energia),
        )
        conn.commit()
        resultado = f"[DB] Agente '{nombre}' registrado con exito."
    except sqlite3.IntegrityError:
        resultado = f"[DB] Error: El agente '{nombre}' ya existe en la base de datos."
    finally:
        conn.close()
    return resultado


def despertar_agente(nombre: str) -> dict | None:
    """Busca un agente por nombre. Retorna dict o None si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, rol, energia FROM agentes WHERE nombre = ?", (nombre,))
    fila = cursor.fetchone()
    conn.close()
    if fila is None:
        return None
    return {"nombre": fila[0], "rol": fila[1], "energia": fila[2]}


def enviar_mensaje(remitente: str, destinatario: str, contenido: str) -> str:
    """Inserta un mensaje en la tabla mensajes con timestamp automatico."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO mensajes (remitente, destinatario, contenido, timestamp) VALUES (?, ?, ?, ?)",
        (remitente, destinatario, contenido, timestamp),
    )
    conn.commit()
    conn.close()
    return f"[DB] Mensaje de '{remitente}' a '{destinatario}' enviado a las {timestamp}."


def leer_mensajes(nombre_agente: str) -> list[dict]:
    """Lee todos los mensajes dirigidos a un agente, ordenados por timestamp."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT remitente, destinatario, contenido, timestamp FROM mensajes WHERE destinatario = ? ORDER BY timestamp",
        (nombre_agente,),
    )
    filas = cursor.fetchall()
    conn.close()
    return [
        {"remitente": f[0], "destinatario": f[1], "contenido": f[2], "timestamp": f[3]}
        for f in filas
    ]


def listar_agentes() -> list[dict]:
    """Retorna una lista con todos los agentes registrados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, rol, energia FROM agentes")
    filas = cursor.fetchall()
    conn.close()
    return [
        {"nombre": f[0], "rol": f[1], "energia": f[2]}
        for f in filas
    ]


# -----------------------------------------------------------#
# SECCION B: Ejercicios guiados (descomenta capitulo a capitulo)
# -----------------------------------------------------------#

if __name__ == "__main__":

    # ======================================================
    # CAPITULO 1: El problema de la amnesia (5 min)
    # ======================================================
    # Cada vez que ejecutas un script de Python, las variables
    # viven en la RAM. Cuando el script termina, la RAM se libera
    # y todo desaparece. Observa:

    agente = {"nombre": "Atlas", "rol": "explorador", "energia": 100}
    print(f"Agente creado: {agente}")
    print("Script terminado. ¿Donde quedo el agente Atlas? En ningun lado. La RAM se borro.")

    # PRUEBA: Vuelve a ejecutar el script. Atlas nace de cero cada vez. Eso es amnesia.
    # CONCLUSION: En este punto el script si bien genera una variable esta solo se imprime
    # y al terminar la ejecución se pierde.

    # ======================================================
    # CAPITULO 2: SQL en 5 minutos (10 min)
    # ======================================================
    # SQLite es una base de datos que vive en UN SOLO ARCHIVO.
    # No necesitas instalar nada: Python ya lo trae incluido.
    # CREATE TABLE IF NOT EXISTS crea la tabla solo si no existe.
    # Esto significa que puedes ejecutar este codigo muchas veces
    # sin que se rompa nada.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    crear_tablas()
    print(f"[Sistema] Tablas creadas. ¿Existe el archivo? {os.path.exists(DB_PATH)}")
    print(f"[Sistema] Archivo de base de datos: {DB_PATH}")

    # PRUEBA: Busca el archivo agentes.db en tu carpeta S5/. Abrelo con un editor de texto. ¿Que ves? (Nada legible, es binario.)
    # CONCLUSION:
    # - En este punto se utiliza la función crear_tablas() 
    # para crear dos tablas en la bd generada de SQLite.
    # - Se concluye que se está utilizando SQL similar al estandar.
    # - Si bien el archivo al abrirlo en un editor de texto tiene fragmentos
    # que se pueden leer también se observan simbolos que sugieren partes en binario.

    # ======================================================
    # CAPITULO 3: Registrar un agente (10 min)
    # ======================================================
    # INSERT INTO agentes ... inserta una fila nueva.
    # El ? es un PARAMETRO: SQLite reemplaza cada ? por el valor
    # correspondiente de la tupla. NUNCA uses f-strings en SQL
    # porque es vulnerable a inyeccion SQL.
    # Si el nombre ya existe (PRIMARY KEY), salta IntegrityError.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    print(registrar_agente("Atlas", "explorador", 100))
    print(registrar_agente("Nova", "cientifica", 150))
    print(registrar_agente("Titan", "guardian", 200))

    # PRUEBA: Intenta registrar 'Atlas' dos veces. ¿Que mensaje recibes? ¿Por que?
    print(registrar_agente("Atlas", "explorador", 100))

    # CONCLUSION:
    # Se concluye que como el archivo agentes.db ya genera persistencia.
    # Si se intenta insertar un registro con la misma llave (en este caso nombre)
    # entonces se levanta la excepción IntegrityError.
    # Esta excepción es controlada y se muestra el mensaje indicando
    # que ya existe un registro con dicho nombre.

    # ======================================================
    # CAPITULO 4: Despertar un agente (10 min)
    # ======================================================
    # SELECT busca datos en la tabla. fetchone() retorna UNA fila
    # como tupla, o None si no hay resultados.
    # Convertimos la tupla a dict para que sea mas facil de usar.
    # Lo importante: los datos PERSISTEN entre ejecuciones.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    datos_atlas = despertar_agente("Atlas")
    print(f"Agente encontrado: {datos_atlas}")
    print("Ahora cierra Python (Ctrl+C o cierra la terminal).")
    #print("Vuelve a abrir y ejecuta SOLO este capitulo. El agente sigue ahi.")

    datos_fantasma = despertar_agente("NoExisto")
    print(f"Agente inexistente: {datos_fantasma}")

    # PRUEBA: Cierra Python completamente. Vuelve a abrir. Ejecuta despertar_agente('Atlas'). ¿Sigue vivo?
    # Si, debido a que despertar_agente carga el archivo de base de datos generado
    # en los capítulos anteriores el cual ya contiene la fila del agente Atlas.

    # CONCLUSION:
    # La persistencia se confirma al ejecutar despertar_agente

    # ======================================================
    # CAPITULO 5: La tabla de mensajes (10 min)
    # ======================================================
    # La tabla mensajes tiene un id autoincrementable: cada mensaje
    # recibe un numero unico automaticamente. El timestamp se genera
    # con datetime.now().isoformat() al momento de enviar.
    # Esto permite tener un historial ordenado de comunicaciones.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    print(enviar_mensaje("Atlas", "Nova", "Encontre un artefacto en la cueva norte."))
    print(enviar_mensaje("Nova", "Atlas", "Excelente. Enviare un drone de analisis."))
    print(enviar_mensaje("Titan", "Nova", "Perimetro asegurado. Sin amenazas detectadas."))

    # PRUEBA: Envia un mensaje de Atlas a si mismo. ¿Funciona? ¿Deberia?
    print(enviar_mensaje("Atlas", "Atlas", "Mensaje a mi mismo"))
    # De acuerdo a la definición de la tabla y a la función enviar_mensaje
    # no hay restricción en el envio de un mensaje de un agente a el mismo
    #
    # CONCLUSION:
    # La función enviar_mensaje registra una nueva fila en la tabla mensajes,
    # SQLite genera un nuevo id por cada inserción de manera automática

    # ======================================================
    # CAPITULO 6: Bandeja de entrada (10 min)
    # ======================================================
    # SELECT ... WHERE destinatario = ? filtra los mensajes
    # dirigidos a un agente especifico. ORDER BY timestamp los
    # ordena cronologicamente. fetchall() retorna TODAS las filas.

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    mensajes_nova = leer_mensajes("Nova")
    print(f"\n--- Bandeja de entrada de Nova ({len(mensajes_nova)} mensajes) ---")
    for msg in mensajes_nova:
        print(f"  [{msg['timestamp']}] {msg['remitente']} -> {msg['contenido']}")

    # PRUEBA: Crea un tercer agente 'Hermes'.
    # Envia mensajes desde Atlas y Nova a Hermes. Lee la bandeja de Hermes.
    print(registrar_agente("Hermes", "Nuevo agente", 200))
    print(enviar_mensaje("Atlas", "Hermes", "Saludos Hermes!"))
    print(enviar_mensaje("Nova", "Hermes", "Bienvenido Hermes!"))

    mensajes_nova = leer_mensajes("Hermes")
    print(f"\n--- Bandeja de entrada de Hermes ({len(mensajes_nova)} mensajes) ---")
    for msg in mensajes_nova:
        print(f"  [{msg['timestamp']}] {msg['remitente']} -> {msg['contenido']}")

    # CONCLUSION:
    # - La función enviar_mensaje devuelve una variable iterable 
    # que puede navegarse por medio de un for
    # - El SELECT ejecutado es un selección básica de los datos
    # utilizando el filtro de destinatario sobre la tabla mensajes  

    # ======================================================
    # CAPITULO 7: Experimentacion libre (5 min)
    # ======================================================
    # Ahora que conoces las funciones, crea tu propio escenario.
    # Aqui tienes un mini-script de ejemplo que combina todo:

    # --- Descomenta el siguiente bloque, ejecuta y observa ---
    print(registrar_agente("Hades", "Elimina y limpia", 120))
    print(registrar_agente("Zeus", "Lider", 90))
    print(registrar_agente("Poseidon", "Carga de energía", 1000))

    print(enviar_mensaje("Zeus", "Hades", "Elimina a todos"))
    print(enviar_mensaje("Zeus", "Hades", "Limpia todo"))
    print(enviar_mensaje("Zeus", "Poseidon", "Dale mas energía a Hades"))

    print("\n--- Muestra todos los mensajes por agente ---")
    for agente in listar_agentes():
        print(f"\n---Agente: {agente['nombre']} | Rol: {agente['rol']} | Energia: {agente['energia']}---")
        print(f"\n--- Bandeja de {agente['nombre']} ---")
        for msg in leer_mensajes(agente['nombre']):
            print(f"  [{msg['timestamp']}] {msg['remitente']} -> {msg['contenido']}")

    # PRUEBA: Cierra Python. Vuelve a abrir. ¿Siguen los mensajes? ¿Y los agentes?
    # Si, la persistencia funciona correctamente. 
    # Sigue utilizandose el mismo archivo generado al inicio del script.

    # CONCLUSION:
    # Una vez definida un archivo de base de datos y las tablas se genera persistencia
    # siempre y cuando se cargue el mismo archivo en todas las funciones que utilizan dicha base de datos

    # -----------------------------------------------------------#
    # Felicidades! Ya sabes persistir datos con SQLite.
    # En la proxima sesion conectaremos estas funciones a una API
    # web con FastAPI para que otros programas puedan hablar con
    # nuestros agentes a traves de HTTP.
    # -----------------------------------------------------------#
