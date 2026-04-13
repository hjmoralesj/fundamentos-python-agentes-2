# -----------------------------------------------------------#
# Semana 5 - Sesion 2: Servidor FastAPI para Agentes
# -----------------------------------------------------------#
# En la sesion anterior le dimos memoria permanente a nuestros
# agentes con SQLite. Pero solo nosotros podiamos hablar con
# ellos ejecutando scripts de Python.
#
# Hoy vamos a ABRIR UNA PUERTA AL MUNDO: un servidor web.
# Cualquier programa, navegador o aplicacion podra comunicarse
# con nuestros agentes a traves de HTTP (el mismo protocolo
# que usa tu navegador para cargar paginas web).
#
# Usaremos FastAPI: un framework moderno de Python que convierte
# funciones normales en endpoints HTTP con documentacion
# automatica.
#
# Instrucciones:
# 1. Instala las dependencias (solo la primera vez):
#       pip install fastapi uvicorn
# 2. Ejecuta el servidor desde la carpeta S5/:
#       uvicorn S5_sesion_2:app --reload
# 3. Abre http://localhost:8000/docs en tu navegador
# 4. Descomenta capitulo por capitulo, guarda, y observa
#    como aparecen nuevos endpoints en /docs automaticamente
# -----------------------------------------------------------#

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from S5_sesion_1 import (
    crear_tablas,
    registrar_agente,
    despertar_agente,
    enviar_mensaje,
    leer_mensajes,
    listar_agentes,
)

# -----------------------------------------------------------#
# Creamos las tablas al iniciar el servidor.
# Asi garantizamos que la base de datos existe antes de
# recibir cualquier peticion.
# -----------------------------------------------------------#
crear_tablas()

# -----------------------------------------------------------#
# Modelos Pydantic: definen la FORMA de los datos que el
# servidor acepta. FastAPI usa estos modelos para:
# - Validar automaticamente los datos de entrada
# - Generar documentacion en Swagger UI
# - Convertir JSON del cliente a objetos de Python
# -----------------------------------------------------------#


class AgenteRequest(BaseModel):
    nombre: str
    rol: str
    energia: int


class MensajeRequest(BaseModel):
    remitente: str
    destinatario: str
    contenido: str


# -----------------------------------------------------------#
# La aplicacion FastAPI: este objeto ES nuestro servidor.
# El titulo y la descripcion aparecen en la pagina de /docs.
# -----------------------------------------------------------#
app = FastAPI(
    title="Sistema de Agentes",
    description="API para gestionar agentes y mensajes",
)


# ======================================================
# CAPITULO 1: La analogia del restaurante (5 min)
# ======================================================
# Imagina un restaurante:
#   - TU eres el CLIENTE (estas en la mesa, tienes hambre)
#   - La COCINA es el SERVIDOR (tiene los ingredientes y sabe cocinar)
#   - El MESERO es HTTP (lleva tu pedido a la cocina y trae la comida)
#   - El MENU es la API (te dice que puedes pedir y como pedirlo)
#
# Cuando visitas una pagina web, tu navegador (cliente) envia una
# PETICION HTTP al servidor. El servidor procesa la peticion y
# retorna una RESPUESTA. Eso es todo. Asi funciona internet.
#
# Codigos de respuesta del mesero:
#   200 = "Aqui esta tu plato" (todo bien)
#   404 = "Ese plato no existe" (recurso no encontrado)
#   422 = "No entendi tu pedido" (datos invalidos)
#   500 = "Se incendio la cocina" (error del servidor)
# ======================================================


# ======================================================
# CAPITULO 2: Instalacion y verificacion (5 min)
# ======================================================
# FastAPI necesita dos paquetes adicionales:
#   pip install fastapi uvicorn
#
# - fastapi: el framework que convierte funciones en endpoints
# - uvicorn: el servidor web que ejecuta nuestra aplicacion
#
# Para ejecutar el servidor:
#   cd S5
#   uvicorn S5_sesion_2:app --reload
#
# El flag --reload hace que el servidor se reinicie automaticamente
# cada vez que guardas cambios en el archivo. Muy util para desarrollo.
#
# PRUEBA: Ejecuta en tu terminal: pip install fastapi uvicorn
#         Luego verifica: python -c "import fastapi; print(fastapi.__version__)"
# ======================================================


# ======================================================
# CAPITULO 3: Mi primer endpoint (10 min)
# ======================================================
# Un ENDPOINT es una URL que responde a peticiones HTTP.
# @app.get("/") es un DECORADOR: le dice a FastAPI que
# cuando alguien visite la ruta "/" con el metodo GET,
# ejecute la funcion de abajo.
#
# Lo que la funcion retorna (un diccionario) se convierte
# automaticamente en JSON. Asi de simple.
# ======================================================


@app.get("/")
def inicio():
    return {"status": "online", "mensaje": "Bienvenido al sistema de agentes con FastAPI"}


# PRUEBA: Abre http://localhost:8000/docs en tu navegador. Esa es Swagger UI.
#         Swagger UI es documentacion INTERACTIVA generada automaticamente
#         por FastAPI a partir de tu codigo. Puedes probar endpoints ahi mismo.
# PRUEBA: Cambia el mensaje de arriba, guarda el archivo, y recarga /docs.
#         uvicorn --reload detecta el cambio y reinicia el servidor solo.
# CONCLUSION:
# Al cambiar cualquier parte del archivo, como el mensaje, 
# se recarga la aplicación y se observa inmediatamente el efecto.



# ======================================================
# CAPITULO 4: GET con parametros (10 min)
# ======================================================
# A veces necesitamos que el cliente nos diga QUE quiere.
# Por ejemplo: "dame los datos del agente Atlas".
#
# En FastAPI, {nombre} en la ruta es un PATH PARAMETER.
# FastAPI extrae el valor de la URL y lo pasa como argumento
# a la funcion. El type hint (nombre: str) le dice a FastAPI
# que debe ser un string.
#
# Si el agente no existe, no queremos retornar un dict vacio.
# Queremos retornar un ERROR HTTP con codigo 404 (Not Found).
# Para eso usamos HTTPException.

# --- Descomenta el siguiente bloque, ejecuta y observa ---
@app.get("/agente/{nombre}")
def obtener_agente(nombre: str):
    agente = despertar_agente(nombre)
    if agente is None:
        raise HTTPException(status_code=404, detail=f"Agente '{nombre}' no encontrado")
    return agente


@app.get("/agentes/")
def obtener_todos_los_agentes():
    return listar_agentes()

# PRUEBA: Prueba en Swagger UI: busca un agente que exista y uno que no.
#         ¿Que respuesta recibes? ¿Que codigo HTTP retorna cada caso?
# - En el caso del agente que existe se retorna una código HTTP 200
# indicando que el endpoint se ejecutó de forma exitosa(sin errores)
# y el agente fue encontrado.
# - En el caso del agente que no existe se retorna una código HTTP 404 
# indicanddo que el endpoint se ejecutó de forma exitosa(sin errores) y el agente no fue encontrado.
#
# CONCLUSION:
# - FastAPI genera facilmente la documentación y expone una función simple como un endpoint.
#

# ======================================================
# CAPITULO 5: POST endpoints (10 min)
# ======================================================
# GET es para LEER datos. POST es para ENVIAR datos nuevos.
#
# Cuando un cliente hace POST, envia datos en el BODY de la
# peticion (no en la URL). FastAPI usa los modelos Pydantic
# que definimos arriba para:
# 1. Leer el JSON del body
# 2. Validar que tiene los campos correctos con los tipos correctos
# 3. Convertirlo a un objeto Python (agente.nombre, agente.rol, etc.)
#
# Si el cliente envia datos invalidos (por ejemplo, energia="hola"
# en vez de un numero), FastAPI retorna automaticamente un error 422
# con detalles de que salio mal. No necesitas escribir validacion manual.

# --- Descomenta el siguiente bloque, ejecuta y observa ---
@app.post("/agentes/")
def crear_agente(agente: AgenteRequest):
    resultado = registrar_agente(agente.nombre, agente.rol, agente.energia)
    return {"mensaje": resultado}


@app.post("/mensajes/")
def crear_mensaje(mensaje: MensajeRequest):
    resultado = enviar_mensaje(mensaje.remitente, mensaje.destinatario, mensaje.contenido)
    return {"mensaje": resultado}


@app.get("/mensajes/{nombre}")
def obtener_mensajes(nombre: str):
    return leer_mensajes(nombre)

# PRUEBA: En Swagger UI: crea un agente nuevo via POST /agentes/.
#         Luego consultalo via GET /agente/{nombre}. ¿Aparece?
# Si, se registra y el endpoint devuelve un código 200 indicando que fue exitoso.
# PRUEBA: Envia un mensaje via POST /mensajes/.
#         Luego consulta la bandeja via GET /mensajes/{nombre}.
# El mensaje se registra correctamente, tal como si se hubiera llamado la función.
# PRUEBA: Intenta enviar un POST con energia="hola" en vez de un numero.
#         ¿Que error recibes? Esa es la validacion automatica de Pydantic.
# La aplicación retorna un mensaje HTTP 422 Error: Unprocessable Content. En el detalle de la respuesta se indica que el valor enviado a la variable energía debe ser entero.
# CONCLUSION:
# Con FastAPI logramos exponer endpoints no solo de GET sino POST de forma rápida, ademas utilizando Pydantic para validar la correcta estructura y tipado del JSON entrante.

# -----------------------------------------------------------#
# Felicidades! Ya tienes un servidor web que expone tus agentes
# al mundo. Cualquier programa puede crear agentes, enviar
# mensajes y consultar datos a traves de HTTP.
#
# Resumen de lo aprendido:
# - GET: leer datos (navegador, curl, fetch)
# - POST: enviar datos nuevos (body en JSON)
# - Path parameters: {nombre} en la URL
# - Pydantic: validacion automatica de datos
# - HTTPException: errores HTTP con codigos estandar
# - Swagger UI: documentacion interactiva gratuita
# -----------------------------------------------------------#
