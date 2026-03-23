"""
Agente de consola con autenticacion y ejecucion de comandos.
Taller Semana 1
Julián Morales
hector.morales@sofka.com.co
Notas:
- Se agregan comentarios a funciones con estilo Google
- Se crea diccionario de comandos para facilitar la lectura del código y su mantenibilidad
- Le ejecución de cada comandos retorna su respuesta para se guarde a excepción de Salir
"""

# Importa todo el módulo sys
import sys

# Impota del módulo datetime solo la clase datetime
from datetime import datetime


def comando_ping():
    """Responde con un mensaje simple."""
    respuesta = "pong!"
    print(respuesta)
    return respuesta


def comando_contar():
    """Cuenta vocales y consonantes en una frase."""
    frase = input("Ingresa una frase: ")
    vocales = 0
    consonantes = 0
    # For se puede utilizar con una variable tipo str ya que este tipo es iterable
    for caracter in frase.lower():
        # Se utiliza isalpha() para evaluar si cada caracter de la cadena es una letra
        if not caracter.isalpha():
            continue

        if caracter in "aeiou":
            vocales += 1
        else:
            consonantes += 1

    respuesta = f"Frase: {frase}\nVocales: {vocales}\nConsonantes: {consonantes}"
    print(respuesta)
    return respuesta


def comando_fecha_hoy(usuario):
    """Muestra la fecha actual si el usuario es administrador.

    Args:
        usuario (str): Usuario autenticado.
    """
    # Comando recibe usuario logueado, si no es admin no puede continuar
    if usuario != "admin":
        respuesta = (
            "[Acceso Denegado] Este comando requiere privilegios de administrador."
        )
        return respuesta
    # Formatea la fecha con "%Y-%m-%d %H:%M:%S y la imprime
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    respuesta = f"Fecha y hora actual: {fecha_actual}"
    print(respuesta)
    return respuesta


def comando_validar_pass(usuario):
    """Valida una contrasena propuesta segun reglas basicas.

    Args:
        usuario (str): Usuario autenticado.
    """
    contrasena = input("Ingresa una contrasena propuesta: ")
    # Errores es de tipo lista, este tipo de variable es iterable
    errores = []

    if len(contrasena) < 8:
        # Append() agrega un elemento a a lista
        errores.append("Debe tener al menos 8 caracteres.")

    if contrasena == usuario:
        errores.append("No puede ser igual al nombre de usuario.")

    if errores:
        encabezado = "La contrasena no es valida por las siguientes razones:"
        detalle_errores = "\n".join(f"- {error}" for error in errores)
        respuesta = f"{encabezado}\n{detalle_errores}"
        print(respuesta)
        return respuesta

    respuesta = "La contrasena es valida."
    print(respuesta)
    return respuesta


def comando_calculadora():
    """Realiza una operacion matematica basica."""
    # Se usa float() para castear el texto ingresado a tipo float
    # Si el casteo falla se levanta una excepción de tipo ValueError
    # Así se asegura que el valor ingresado por el valor sea un número valido
    try:
        primer_numero = float(input("Ingresa el primer numero: "))
        operador = input("Ingresa el operador (+ - * /): ").strip()
        segundo_numero = float(input("Ingresa el segundo numero: "))
    except ValueError:
        respuesta = "Error: Debes ingresar numeros validos."
        print(respuesta)
        return respuesta

    if operador == "+":
        resultado = primer_numero + segundo_numero
    elif operador == "-":
        resultado = primer_numero - segundo_numero
    elif operador == "*":
        resultado = primer_numero * segundo_numero
    elif operador == "/":
        if segundo_numero == 0:
            respuesta = "Error: No se puede dividir entre cero."
            print(respuesta)
            return respuesta
        resultado = primer_numero / segundo_numero
    else:
        respuesta = "Error: Operador no valido."
        print(respuesta)
        return respuesta

    respuesta = (
        f"Operación: {primer_numero} {operador} {segundo_numero} Resultado: {resultado}"
    )
    print(respuesta)
    return respuesta


def comando_ayuda():
    """Muestra los comandos disponibles y su descripcion."""
    respuesta = mostrar_ayuda()
    print(respuesta)
    return respuesta


def comando_historial(historial_comandos, opcion):
    """Gestiona la visualizacion, limpieza y busqueda del historial.

    Args:
        historial_chat (list[dict]): Historial almacenado del pseudoagente.
        opcion (str): Subcomando opcional para operar sobre el historial.

    Returns:
        str: Respuesta del sistema.
    """
    opcion = opcion.strip().lower()

    if opcion == "all":
        if not historial_comandos:
            respuesta = "[Alerta] No hay historial almacenado."
            print(respuesta)
            return respuesta

        lineas = ["Historial completo:"]
        print(lineas[0])

        for registro in historial_comandos:
            linea = (
                f"{registro['timestamp']} | "
                f"Comando: {registro['comando']} | "
                f"Usuario: {registro['usuario']} | "
                f"Respuesta: {registro['respuesta']}"
            )
            print(linea)
            lineas.append(linea)
        #Si se retorna todo el contenido vuelve y se guarda un nuevo mensaje duplicando el historial
        return "".join(lineas)

    if opcion == "clear":
        historial_comandos.clear()
        respuesta = "[Alerta] Historial eliminado correctamente."
        print(respuesta)
        return respuesta

    palabra_clave = input("Ingresa la palabra clave a buscar: ").strip().lower()
    coincidencias = []
    if len(palabra_clave) == 0:
        respuesta = "[Alerta] No ingresó palabra clave a buscar"
        print(respuesta)
        return respuesta
    #Iterar en el histórico de comnados
    for registro in historial_comandos:
        #En cada respuesta de cada elemento de la historia se busca la cadena con el operador in
        #El operador in busca si un elemento está dentro de otro, en este caso un conjunto de caractares
        if palabra_clave in registro["respuesta"].lower():
            coincidencias.append(registro)

    if not coincidencias:
        respuesta = "[Alerta] No encontré registros que coincidan con esa palabra."
        print(respuesta)
        return respuesta

    encabezado = f"Buscando {palabra_clave} encontré {len(coincidencias)} registro(s) coincidente(s)."
    print(encabezado)
    lineas = [encabezado]

    for registro in coincidencias:
        fecha = registro["timestamp"]
        autor = registro["usuario"]
        comando = registro["comando"]
        mensaje = registro["respuesta"]
        detalle = f"Fecha: {fecha} Comando: {comando} Autor: {autor} | Mensaje: {mensaje}"
        print(detalle)
        lineas.append(detalle)

    return encabezado


def comando_salir():
    """Apaga el sistema y finaliza el programa."""
    print("Apagando sistema...")
    # Hace uso del módulo importado para salir del programa limpiamente
    sys.exit()


def autenticar_usuario(usuarios):
    """Solicita credenciales y autentica al usuario.

    Args:
        usuarios (dict[str, str]): Diccionario de usuarios y contrasenas.

    Returns:
        str | None: Nombre del usuario autenticado o `None` si falla.
    """
    intentos_maximos = 3

    # Solicita un usuario y contraseña, se eliminan espacios al inicio y al final de cada input
    for intento in range(intentos_maximos):
        usuario = input("Usuario: ").strip()
        contrasena = input("Contrasena: ").strip()
        # Si los inputs ingresados coinciden con algún elemento del diccionario se retorna el elemento
        if usuarios.get(usuario) == contrasena:
            print(f"Bienvenido, {usuario}.")
            return usuario

        intentos_restantes = intentos_maximos - intento - 1

        # Si usuario/contraseña no existe se valida si se puede volver a intentar
        if intentos_restantes > 0:
            print(f"Credenciales incorrectas. Intentos restantes: {intentos_restantes}")
    # Si se acaban los intentos no se devuelve usuario
    print("[Alerta] Usuario bloqueado. Cerrando sistema.")
    return None


def mostrar_ayuda():
    """Imprime la lista de comandos disponibles."""
    respuesta = "Comandos disponibles:\n"
    menu = []
    # Itere en cada item del diccionario, en este caso extrea el nombre del diccionario principal y descripción del diccionario anidado
    for nombre, datos in comandos.items():
        menu.append(f"- {nombre}: {datos['descripcion']}\n")
    respuesta = respuesta + "".join(menu)
    print(respuesta)
    return respuesta


def ejecutar_comando(comando_info, usuario, historial_comandos, argumento):
    """Ejecuta un comando y envia el usuario solo cuando es necesario.

    Args:
        comando_info (dict): Informacion del comando seleccionado.
        usuario (str): Usuario autenticado.
    """
    # Obtiene la referencia a la función asociada a cada comando
    funcion = comando_info["funcion"]
    # Si la función requiere el historial entonces envía los objetos necesarios
    # Luego ejecuta la función asociada al comando y termina la ejecución de esta función
    if comando_info.get("requiere_historial", False):
        return funcion(historial_comandos, argumento)
    # Si la función requiere el usuario entonces envía los objetos necesarios
    # Luego ejecuta la función asociada al comando y termina la ejecución de esta función
    if comando_info.get("requiere_usuario", False):
        return funcion(usuario)
    # Ejecuta la función que no requiere los datos del usuario
    return funcion()


def registrar_comando(historial, nombre_comando, usuario, respuesta):
    """Guarda la informacion de cada comando ejecutado.

    Args:
        historial (list[dict]): Historial de la sesion.
        nombre_comando (str): Nombre del comando ingresado.
        usuario (str): Usuario autenticado.
        respuesta (str): Respuesta del sistema.
    """
    historial.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comando": nombre_comando,
            "usuario": usuario,
            "respuesta": respuesta.replace("\n"," "),
        }
    )


# Define un diccionario con cada comando.
# A su vez cada elemento del diccionario tiene otro diccionario con los datos requeridos para definir cada comando
# funcion: Es una referencia a la función definida con la lógica de cada comando
# descripcion: un breve texto que describe el comando
# requiere_usuario: define si se requiere ejecutar alguna validación con los datos del usuario logueado
# requiere_historial: define si la función requiere el objeto con el historial de comando

comandos = {
    "ping": {
        "funcion": comando_ping,
        "descripcion": "Responde con un mensaje simple.",
    },
    "contar": {
        "funcion": comando_contar,
        "descripcion": "Cuenta vocales y consonantes de una frase.",
    },
    "fecha_hoy": {
        "funcion": comando_fecha_hoy,
        "descripcion": "Muestra la fecha y hora actual. Solo admin.",
        "requiere_usuario": True,
    },
    "validar_pass": {
        "funcion": comando_validar_pass,
        "descripcion": "Valida una contrasena segun reglas basicas.",
        "requiere_usuario": True,
    },
    "calculadora": {
        "funcion": comando_calculadora,
        "descripcion": "Realiza operaciones matematicas basicas.",
    },
    "historial": {
        "funcion": comando_historial,
        "descripcion": "Consulta, busca o limpia el historial del pseudoagente.",
        "requiere_historial": True,
    },
    "ayuda": {
        "funcion": comando_ayuda,
        "descripcion": "Muestra la ayuda del sistema.",
    },
    "salir": {
        "funcion": comando_salir,
        "descripcion": "Cierra el programa.",
    },
}


def main():
    """Ejecuta el flujo principal del agente de consola."""
    usuarios = {
        "admin": "admin123",
        "invitado": "invitado123",
    }

    historial_comandos = []

    usuario_autenticado = autenticar_usuario(usuarios)
    # Si no hay usuario autenticado se usa return para terminar la ejecución de la función principal y así terminar el programa
    if usuario_autenticado is None:
        return

    mostrar_ayuda()

    while True:
        # Se limpia cada input del usuario para validar si coincide con el nombre de un comando definido
        comando = input("\nIngresa un comando: ").strip().lower()
        if not comando:
            print("Debes ingresar un comando.")
            continue

        partes = comando.split(maxsplit=1)
        nombre_comando = partes[0]
        argumento = partes[1] if len(partes) > 1 else ""
        # Se busca en el diccionario haciendo uso de la llave, en este caso el nombre del comando
        comando_info = comandos.get(nombre_comando)

        # Si en el diccionario no se encuentra coincidencia se valida a None
        if comando_info is None:
            respuesta = "Comando no reconocido. Usa 'ayuda' para ver las opciones."
            print(respuesta)
            registrar_comando(
                historial_comandos,
                comando,
                usuario_autenticado,
                respuesta,
            )
            # Usado para saltar a la siguiente iteración del ciclo
            continue

        respuesta = ejecutar_comando(
            comando_info, usuario_autenticado, historial_comandos, argumento
        )
        registrar_comando(
            historial_comandos,
            comando,
            usuario_autenticado,
            respuesta,
        )


if __name__ == "__main__":
    main()
