"""
Agente de consola con autenticacion y ejecucion de comandos.
Taller Semana 1
Julián Morales
hector.morales@sofka.com.co
Notas:
- Se utilizó Codex para generar script 
- Se agregan comentarios a funciones con estilo Google
- Se crea diccionario de comandos para facilitar la lectura del código y su mantenibilidad
"""
#Importa todo el módulo sys
import sys
#Impota del módulo datetime solo la clase datetime
from datetime import datetime


def comando_ping():
    """Responde con un mensaje simple."""
    print("pong!")


def comando_contar():
    """Cuenta vocales y consonantes en una frase."""
    frase = input("Ingresa una frase: ")
    vocales = 0
    consonantes = 0
    #For se puede utilizar con una variable tipo str ya que este tipo es iterable
    for caracter in frase.lower():
        #Se utiliza isalpha() para evaluar si cada caracter de la cadena es una letra
        if not caracter.isalpha():
            continue

        if caracter in "aeiou":
            vocales += 1
        else:
            consonantes += 1

    print(f"Vocales: {vocales}")
    print(f"Consonantes: {consonantes}")


def comando_fecha_hoy(usuario):
    """Muestra la fecha actual si el usuario es administrador.

    Args:
        usuario (str): Usuario autenticado.
    """
    #Comando recibe usuario logueado, si no es admin no puede continuar
    if usuario != "admin":
        print(
            "[Acceso Denegado] Este comando requiere privilegios de administrador."
        )
        return
    #Formatea la fecha con "%Y-%m-%d %H:%M:%S y la imprime
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Fecha y hora actual: {fecha_actual}")


def comando_validar_pass(usuario):
    """Valida una contrasena propuesta segun reglas basicas.

    Args:
        usuario (str): Usuario autenticado.
    """
    contrasena = input("Ingresa una contrasena propuesta: ")
    errores = []

    if len(contrasena) < 8:
        #Append() agrega un elemento a a lista
        errores.append("Debe tener al menos 8 caracteres.")
    print(contrasena)
    print(usuario)
    if contrasena == usuario:
        errores.append("No puede ser igual al nombre de usuario.")

    if errores:
        print("La contrasena no es valida por las siguientes razones:")
        #Errores es de tipo lista, este tipo de variable es iterabla
        for error in errores:
            print(f"- {error}")
        return

    print("La contrasena es valida.")


def comando_calculadora():
    """Realiza una operacion matematica basica."""
    #Se usa float() para castear el texto ingresado a tipo float
    #Si falla se levanta una excepción de tipo ValueError controlando así que solo se realiza la operación con números
    try:
        primer_numero = float(input("Ingresa el primer numero: "))
        operador = input("Ingresa el operador (+ - * /): ").strip()
        segundo_numero = float(input("Ingresa el segundo numero: "))
    except ValueError:
        print("Error: Debes ingresar numeros validos.")
        return

    if operador == "+":
        resultado = primer_numero + segundo_numero
    elif operador == "-":
        resultado = primer_numero - segundo_numero
    elif operador == "*":
        resultado = primer_numero * segundo_numero
    elif operador == "/":
        if segundo_numero == 0:
            print("Error: No se puede dividir entre cero.")
            return
        resultado = primer_numero / segundo_numero
    else:
        print("Error: Operador no valido.")
        return

    print(f"Resultado: {resultado}")


def comando_ayuda():
    """Muestra los comandos disponibles y su descripcion."""
    mostrar_ayuda()


def comando_salir():
    """Apaga el sistema y finaliza el programa."""
    print("Apagando sistema...")
    #Hace uso del módulo importado para salir del programa limpiamente
    sys.exit()


def autenticar_usuario(usuarios):
    """Solicita credenciales y autentica al usuario.

    Args:
        usuarios (dict[str, str]): Diccionario de usuarios y contrasenas.

    Returns:
        str | None: Nombre del usuario autenticado o `None` si falla.
    """
    #La función recibe un diccionario con los posibles usuarios

    intentos_maximos = 3

    #Solicita un usuario y contraseña, se eliminan espacios al inicio y al final de cada input
    for intento in range(intentos_maximos):
        usuario = input("Usuario: ").strip()
        contrasena = input("Contrasena: ").strip()
        #Si los inputs ingresados coinciden con algún elemento del diccionario se retorna el elemento
        if usuarios.get(usuario) == contrasena:
            print(f"Bienvenido, {usuario}.")
            return usuario
        
        intentos_restantes = intentos_maximos - intento - 1

        #Si usuario/contraseña no existe se valida si se puede volver a intentar
        if intentos_restantes > 0:
            print(
                "Credenciales incorrectas. "
                f"Intentos restantes: {intentos_restantes}"
            )
    #Si se acaban los intentos no se devuelve usuario
    print("[Alerta] Usuario bloqueado. Cerrando sistema.")
    return None


def mostrar_ayuda():
    """Imprime la lista de comandos disponibles."""
    print("Comandos disponibles:")
    #Itere en cada item del diccionario, en este caso extrea el nombre del diccionario principal y descripción del diccionario anidado
    for nombre, datos in comandos.items():
        print(f"- {nombre}: {datos['descripcion']}")


def ejecutar_comando(comando_info, usuario):
    """Ejecuta un comando y envia el usuario solo cuando es necesario.

    Args:
        comando_info (dict): Informacion del comando seleccionado.
        usuario (str): Usuario autenticado.
    """
    #Obtiene la referencia a la función asociada a cada comando
    funcion = comando_info["funcion"]
    #Si la función requiere usuario entonces le envía el objeto usuario
    #Luego ejecuta la función asociada al comando y termina la ejecución de esta función
    if comando_info.get("requiere_usuario", False):
        funcion(usuario)
        return
    #Ejecuta la función que no requiere los datos del usuario
    funcion()

#Define un diccionario con cada comando.
#A su vez cada elemento del diccionario tiene otro diccionario con los datos requeridos para definir cada comando
#funcion: Es una referencia a la función definida con la lógica de cada comando
#descripcion: un breve texto que describe el comando
#requiere_usuario: define si se requiere ejecutar alguna validación con los datos del usuario logueado

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

    usuario_autenticado = autenticar_usuario(usuarios)
    #Si no hay usuario autenticado se usa return para terminar la ejecución de la función principal y así terminar el programa
    if usuario_autenticado is None:
        return

    mostrar_ayuda()

    while True:
        #Se limpia cada input del usuario para validar si coincide con el nombre de un comando definido
        comando = input("\nIngresa un comando: ").strip().lower()
        #Se busca en el diccionario haciendo uso de la llave, en este caso el nombre del comando
        comando_info = comandos.get(comando)
        #Si en el diccionario no se encuentra coincidencia se valida a None
        if comando_info is None:
            print("Comando no reconocido. Usa 'ayuda' para ver las opciones.")
            #Usado para saltar a la siguiente iteración del ciclo
            continue

        ejecutar_comando(comando_info, usuario_autenticado)


if __name__ == "__main__":
    main()
