"""
Agente de consola con autenticacion y ejecucion de comandos.
Taller Semana 3
Julian Morales
hector.morales@sofka.com.co
Notas:
- Se agregan comentarios a funciones con estilo Google
- Se crea diccionario de comandos para facilitar la lectura del codigo y su mantenibilidad
- Cada comando se encarga de devolver su respuesta, no imprimen en consola
- Cada respuesta es guardada en el historial por main
"""

# Imports
import sys
from datetime import datetime
from typing import Any, NoReturn

# Tipos
RegistroHistorial = dict[str, str]
HistorialComandos = list[RegistroHistorial]


# Funciones auxiliares
def autenticar_usuario(usuarios: dict[str, str]) -> str | None:
    """Solicita credenciales y autentica al usuario.

    Args:
        usuarios (dict[str, str]): Diccionario de usuarios y contrasenas.

    Returns:
        str | None: Nombre del usuario autenticado o `None` si falla.
    """
    intentos_maximos = 3

    print("=" * 40)
    print("   Bienvenido al PseudoAgente de Consola")
    print("=" * 40)
    print("\nInicia sesion para continuar.")
    print(f"Tienes hasta {intentos_maximos} intentos disponibles.\n")

    # Solicita un usuario y contrasena, se eliminan espacios al inicio y al final de cada input
    for intento in range(intentos_maximos):
        usuario = input("Ingresa tu usuario: ").strip()
        contrasena = input("Ingresa tu contrasena: ").strip()
        # Si los inputs ingresados coinciden con algun elemento del diccionario
        # se retorna el elemento
        if usuarios.get(usuario) == contrasena:
            print(f"\nInicio de sesion exitoso. Bienvenido, {usuario}.")
            return usuario

        intentos_restantes = intentos_maximos - intento - 1

        # Si usuario/contrasena no existe se valida si se puede volver a intentar
        if intentos_restantes > 0:
            print(
                "[Error] Usuario o contrasena incorrectos. "
                f"Intentos restantes: {intentos_restantes}."
            )
    # Si se acaban los intentos no se devuelve usuario
    print("[Alerta] Usuario bloqueado. Cerrando el sistema.")
    print("Gracias por usar el pseudoagente.")
    return None


def mostrar_ayuda() -> str:
    """Construye la lista de comandos disponibles.

    Returns:
        str: Menu de ayuda en formato de texto con comandos disponibles.
    """
    menu: list[str] = []
    # Itera en cada item del diccionario, en este caso extrae el nombre del diccionario principal
    # y descripcion del diccionario anidado
    for nombre, datos in comandos.items():
        menu.append(f"- {nombre}: {datos['descripcion']}\n")
    respuesta = "".join(menu)
    return respuesta


def ejecutar_comando(
    comando_info: dict[str, Any],
    usuario: str,
    historial_comandos: HistorialComandos,
    argumento: str,
) -> str:
    """Ejecuta un comando y envia el usuario o el historial_comandos solo cuando es necesario.

    Args:
        comando_info (dict[str, Any]): Informacion del comando seleccionado.
        usuario (str): Usuario autenticado.
        historial_comandos (HistorialComandos): Historial de comandos.
        argumento (str): Argumento adicional del comando.

    Returns:
        str: Respuesta generada por el comando.
    """
    # Obtiene la referencia a la funcion asociada a cada comando
    funcion = comando_info["funcion"]
    # Si la funcion requiere el historial entonces envia los objetos necesarios
    # Luego ejecuta la funcion asociada al comando y termina la ejecucion de esta funcion
    if comando_info.get("requiere_historial", False):
        return funcion(historial_comandos, argumento)
    # Si la funcion requiere el usuario entonces envia los objetos necesarios
    # Luego ejecuta la funcion asociada al comando y termina la ejecucion de esta funcion
    if comando_info.get("requiere_usuario", False):
        return funcion(usuario)
    # Ejecuta la funcion que no requiere los datos del usuario
    return funcion()


def registrar_comando(
    historial: HistorialComandos,
    nombre_comando: str,
    usuario: str,
    respuesta: str,
) -> None:
    """Guarda la respuesta de cada comando ejecutado.

    Args:
        historial (HistorialComandos): Historial de la sesion.
        nombre_comando (str): Nombre del comando ingresado.
        usuario (str): Usuario autenticado.
        respuesta (str): Respuesta del comando.
    """
    registro: RegistroHistorial = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "comando": nombre_comando,
        "usuario": usuario,
        "respuesta": respuesta.replace("\n", " "),
    }
    historial.append(registro)


# Funciones de comandos
def comando_ping() -> str:
    """Responde con un mensaje de respuesta a ping.

    Returns:
        str: Respuesta del comando.
    """
    return "pong!"


def comando_contar() -> str:
    """Cuenta vocales y consonantes en una frase ingresada por consola.

    Solicita una frase al usuario y recorre cada caracter para contar
    unicamente letras alfabeticas. Los demas caracteres se ignoran.

    Returns:
        str: Respuesta del comando con la frase original y la cantidad de
            vocales y consonantes encontradas.
    """
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
    return respuesta


def comando_fecha_hoy(usuario: str) -> str:
    """Muestra la fecha actual si el usuario es administrador.

    Args:
        usuario (str): Usuario autenticado.

    Returns:
        str: Respuesta del comando, fecha y hora actual.

    Raises:
        PermissionError: Si el usuario no tiene privilegios suficientes.
    """
    # Si no es admin no puede continuar
    if usuario != "admin":
        raise PermissionError("Privilegios insuficientes")
    # Formatea la fecha con "%Y-%m-%d %H:%M:%S" y la imprime
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Fecha y hora actual: {fecha_actual}"


def comando_validar_pass(usuario: str) -> str:
    """Valida una contrasena propuesta segun reglas basicas.

    Solicita una contrasena al usuario y verifica que tenga al menos
    ocho caracteres y que no sea igual al nombre del usuario autenticado.

    Args:
        usuario (str): Usuario autenticado.

    Returns:
        str: Respuesta de validacion que indica si la contrasena es valida
            o enumera los errores encontrados.
    """
    contrasena = input("Ingresa una contrasena propuesta: ")
    # Errores es de tipo lista, este tipo de variable es iterable
    errores: list[str] = []

    if len(contrasena) < 8:
        # Append() agrega un elemento a la lista
        errores.append("Debe tener al menos 8 caracteres.")

    if contrasena == usuario:
        errores.append("No puede ser igual al nombre de usuario.")

    if errores:
        encabezado = "[Error] La contrasena no es valida por las siguientes razones:"
        detalle_errores = "\n".join(f"- {error}" for error in errores)
        return f"{encabezado}\n{detalle_errores}"

    return "La contrasena es valida."


def comando_calculadora() -> str:
    """Realiza una operacion matematica basica.

    Solicita dos numeros y un operador aritmetico al usuario para ejecutar
    una suma, resta, multiplicacion o division.

    Returns:
        str: Respuesta con el resultado del calculo o un mensaje de error
            si los datos ingresados no son validos.
    """
    # Se usa float() para castear el texto ingresado a tipo float
    # Si el casteo falla se levanta una excepcion de tipo ValueError
    # Asi se asegura que el valor ingresado sea un numero valido
    try:
        primer_numero = float(input("Ingresa el primer numero: "))
        operador = input("Ingresa el operador (+ - * /): ").strip()
        segundo_numero = float(input("Ingresa el segundo numero: "))
    except ValueError:
        return "[Error] Debes ingresar numeros validos."

    if operador == "+":
        resultado = primer_numero + segundo_numero
    elif operador == "-":
        resultado = primer_numero - segundo_numero
    elif operador == "*":
        resultado = primer_numero * segundo_numero
    elif operador == "/":
        if segundo_numero == 0:
            return "[Error] No se puede dividir entre cero."
        resultado = primer_numero / segundo_numero
    else:
        return "[Error] El operador ingresado no es valido."

    return f"Operacion: {primer_numero} {operador} {segundo_numero} Resultado: {resultado}"


def comando_ayuda() -> str:
    """Construye la ayuda con los comandos disponibles.

    Returns:
        str: Respuesta con el texto de los comandos disponibles.
    """
    return mostrar_ayuda()


def comando_historial(historial_comandos: HistorialComandos, opcion: str) -> str:
    """Gestiona la visualizacion, limpieza y busqueda del historial.

    Permite mostrar todo el historial con la opcion `all`, eliminarlo con
    la opcion `clear` o solicitar una palabra clave para buscar coincidencias
    dentro de las respuestas almacenadas.

    Args:
        historial_comandos (HistorialComandos): Historial almacenado del
            pseudoagente.
        opcion (str): Subcomando opcional para operar sobre el historial.
            Puede ser `all`, `clear` o una cadena vacia para iniciar una
            busqueda interactiva.

    Returns:
        str: Respuesta del comando con el historial completo, el resultado
            de una busqueda o la confirmacion de limpieza.
    """
    opcion = opcion.strip().lower()

    if opcion == "all":
        if not historial_comandos:
            return "[Alerta] No hay historial almacenado."

        lineas = ["Historial completo:"]
        lineas.append("Fecha | Comando | Usuario | Respuesta")

        for registro in historial_comandos:
            linea = (
                f"{registro['timestamp']} | "
                f"{registro['comando']} | "
                f"{registro['usuario']} | "
                f"{registro['respuesta']}"
            )
            lineas.append(linea)
        # Si se retorna todo el contenido vuelve
        # y se guarda un nuevo mensaje duplicando el historial
        return "\n".join(lineas)

    if opcion == "clear":
        historial_comandos.clear()
        return "[Alerta] Historial eliminado correctamente."

    palabra_clave = input("Ingresa la palabra clave a buscar: ").strip().lower()
    coincidencias: HistorialComandos = []
    if len(palabra_clave) == 0:
        return "[Error] Debes ingresar una palabra clave para la busqueda."
    # Iterar en el historico de comandos
    for registro in historial_comandos:
        # En cada respuesta de cada elemento de la historia se busca la cadena con el operador in
        # El operador in busca si un elemento esta dentro de otro,
        # en este caso un conjunto de caracteres
        if palabra_clave in registro["respuesta"].lower():
            coincidencias.append(registro)

    if not coincidencias:
        return "[Alerta] No se encontraron registros que coincidan con la palabra ingresada."

    encabezado = (
        f"Buscando {palabra_clave} encontre {len(coincidencias)} "
        "registro(s) coincidente(s)."
    )
    lineas = [encabezado]

    for registro in coincidencias:
        fecha = registro["timestamp"]
        autor = registro["usuario"]
        comando = registro["comando"]
        mensaje = registro["respuesta"]
        detalle = (
            f"Fecha: {fecha} Comando: {comando} "
            f"Autor: {autor} | Mensaje: {mensaje}"
        )
        lineas.append(detalle)

    return "\n".join(lineas)


def comando_salir() -> NoReturn:
    """Apaga el sistema y finaliza el programa.

    Raises:
        SystemExit: Finaliza la ejecucion del programa.
    """
    print("Apagando pseudoagente...")
    # Hace uso del modulo importado para salir del programa limpiamente
    sys.exit()


# Diccionario global de comandos
# Define un diccionario con cada comando.
# A su vez cada elemento del diccionario tiene
# otro diccionario con los datos requeridos para definir cada comando
# funcion: Es una referencia a la funcion definida con la logica de cada comando
# descripcion: un breve texto que describe el comando
# requiere_usuario: define si se requiere ejecutar alguna validacion
# con los datos del usuario logueado
# requiere_historial: define si la funcion requiere el objeto con el historial de comando
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


# Funcion principal
def main() -> None:
    """Ejecuta el flujo principal del agente de consola.

    Inicializa los usuarios permitidos, autentica la sesion actual,
    muestra el menu de ayuda y procesa comandos en un ciclo continuo
    hasta que el programa finaliza.
    """
    usuarios = {
        "admin": "admin123",
        "invitado": "invitado123",
    }

    historial_comandos: HistorialComandos = []

    usuario_autenticado = autenticar_usuario(usuarios)
    # Si no hay usuario autenticado se usa return para
    # terminar la ejecucion de la funcion principal y asi terminar el programa
    if usuario_autenticado is None:
        return

    print("\n" + "-" * 40)
    print("Acceso concedido. Cargando menu principal...")
    print("-" * 40)
    print("\nUsa alguno de estos comandos:")
    print(mostrar_ayuda())

    while True:
        # Se implementa excepcion para control input CTRL + C
        # para que no termine el programa con excepcion no controlada
        try:
            comando = input("\nIngresa un comando: ").strip().lower()
        except KeyboardInterrupt:
            print("\n[Alerta] Operacion cancelada por el usuario.")
            continue
        if not comando:
            print("[Error] Debes ingresar un comando valido.")
            continue

        # Como el comando historial puede recibir una opcion adicional
        # es necesario extraer la posible opcion del input del usuario
        partes = comando.split(maxsplit=1)
        nombre_comando = partes[0]
        argumento = partes[1] if len(partes) > 1 else ""
        # Se busca en el diccionario haciendo uso de la llave, en este caso el nombre del comando
        comando_info = comandos.get(nombre_comando)

        # Si en el diccionario no se encuentra coincidencia se valida a None
        if comando_info is None:
            respuesta = "[Error] Comando no reconocido. Usa 'ayuda' para ver las opciones disponibles."
            print(respuesta)
            registrar_comando(
                historial_comandos,
                comando,
                usuario_autenticado,
                respuesta,
            )
            # Usado para saltar a la siguiente iteracion del ciclo
            continue

        try:
            respuesta = ejecutar_comando(
                comando_info, usuario_autenticado, historial_comandos, argumento
            )
        except PermissionError:
            respuesta = (
                "[Acceso Denegado] Este comando requiere privilegios de "
                "administrador."
            )
        except KeyboardInterrupt:
            print("\n[Alerta] Operacion cancelada por el usuario.")
            continue
        print(respuesta)
        registrar_comando(
            historial_comandos,
            comando,
            usuario_autenticado,
            respuesta,
        )


# Bloque de entrada
if __name__ == "__main__":
    main()
