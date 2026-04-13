from datetime import datetime
import random
import sys
from typing import Any, NoReturn


RegistroHistorial = dict[str, str]
HistorialComandos = list[RegistroHistorial]


class PseudoAgente:
    """Representa un pseudoagente con comandos y cantidad de tokens limitado"""

    def __init__(self, nombre:str = "Athena") -> None:
        self.nombre = nombre
        self.tokens = 100
        self.historial_comandos: HistorialComandos = []
        # Diccionario global de comandos
        # Define un diccionario con cada comando.
        # A su vez cada elemento del diccionario tiene
        # otro diccionario con los datos requeridos para definir cada comando
        # funcion: Es una referencia a la funcion definida con la logica de cada comando
        # descripcion: un breve texto que describe el comando
        # tokens: cantidad de tokens que se usan con cada ejecución del comando
        # requiere_usuario: define si se requiere ejecutar alguna validacion
        # con los datos del usuario logueado
        self.comandos = {
            "ping": {
                "funcion": self.comando_ping,
                "descripcion": "Responde con un mensaje simple.",
                "tokens": 5,
            },
            "lanzar_dado":{
                "funcion": self.comando_lanzar_dado,
                "descripcion": "Genera un número aleatorio entre 1 y 6.",
                "tokens": 1,
            },
            "contar": {
                "funcion": self.comando_contar,
                "descripcion": "Cuenta vocales y consonantes de una frase.",
                "tokens": 5,
            },
            "fecha_hoy": {
                "funcion": self.comando_fecha_hoy,
                "descripcion": "Muestra la fecha y hora actual. Solo admin.",
                "requiere_usuario": True,
                "tokens": 5,
            },
            "validar_pass": {
                "funcion": self.comando_validar_pass,
                "descripcion": "Valida una contrasena segun reglas basicas.",
                "requiere_usuario": True,
                "tokens": 10,
            },
            "calculadora": {
                "funcion": self.comando_calculadora,
                "descripcion": "Realiza operaciones matematicas basicas.",
                "tokens": 10,
            },
            "historial": {
                "funcion": self.comando_historial,
                "descripcion": "Consulta, busca o limpia el historial del pseudoagente.",
                "requiere_argumento": True,
                "tokens": 20,
            },
            "ayuda": {
                "funcion": self.comando_ayuda,
                "descripcion": "Muestra la ayuda del sistema.",
                "tokens": 1,
            },
            "salir": {
                "funcion": self.comando_salir,
                "descripcion": "Cierra el programa.",
                "tokens": 0,
            },
        }

    def ejecutar_comando(
            self,
            comando_info: dict[str, Any],
            usuario: str,
            argumento: str,
            ) -> str:
        """Ejecuta un comando y envia el usuario o el historial_comandos solo cuando es necesario.

        Args:
            comando_info (dict[str, Any]): Informacion del comando seleccionado.
            usuario (str): Usuario autenticado.
            argumento (str): Argumento adicional del comando.

        Returns:
            str: Respuesta generada por el comando.
        """
        # Se valida si hay suficientes tokens para ejecutar el comando solicitado
        if(comando_info["tokens"] > self.tokens):
            raise TokensInsuficientesException
        # Obtiene la referencia a la funcion asociada a cada comando
        funcion = comando_info["funcion"]
        # Se resta de la cantidad de tokens disponibles los usados por el comando
        self.tokens -= comando_info["tokens"]
        # Si la funcion requiere el historial entonces envia los objetos necesarios
        # Luego ejecuta la funcion asociada al comando y termina la ejecucion de esta funcion
        if comando_info.get("requiere_argumento", False):
            return funcion(argumento)
        # Si la funcion requiere el usuario entonces envia los objetos necesarios
        # Luego ejecuta la funcion asociada al comando y termina la ejecucion de esta funcion
        if comando_info.get("requiere_usuario", False):
            return funcion(usuario)
        # Ejecuta la funcion que no requiere los datos del usuario
        return funcion()

    def registrar_comando(
            self,
            nombre_comando: str,
            usuario: str,
            respuesta: str,
        ) -> None:
        """Guarda la respuesta de cada comando ejecutado.

        Args:
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
        self.historial_comandos.append(registro)

    def mostrar_ayuda(self) -> str:
        """Construye la lista de comandos disponibles.

        Returns:
            str: Menu de ayuda en formato de texto con comandos disponibles.
        """
        menu: list[str] = []
        # Itera en cada item del diccionario.
        # En este caso extrae el nombre del diccionario principal
        # y descripcion del diccionario anidado
        for nombre, datos in self.comandos.items():
            menu.append(f"- {nombre}: {datos['descripcion']}\n")
        respuesta = "".join(menu)
        return respuesta

    def comando_lanzar_dado(self) -> str:
        """Responde con un número aleotorio entre 1 y 6.

        Returns:
            str: Respuesta del comando.
        """
        return f"El número aleatorio es {random.randint(1, 6)}"

    def comando_ping(self) -> str:
        """Responde con un mensaje de respuesta a ping.

        Returns:
            str: Respuesta del comando.
        """
        return "pong!"

    def comando_contar(self) -> str:
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

    def comando_fecha_hoy(self, usuario: str) -> str:
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

    def comando_validar_pass(self, usuario: str) -> str:
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

    def comando_calculadora(self) -> str:
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

    def comando_ayuda(self) -> str:
        """Construye la ayuda con los comandos disponibles.

        Returns:
            str: Respuesta con el texto de los comandos disponibles.
        """
        return self.mostrar_ayuda()

    def comando_historial(self, opcion: str) -> str:
        """Gestiona la visualizacion, limpieza y busqueda del historial.

        Permite mostrar todo el historial con la opcion `all`, eliminarlo con
        la opcion `clear` o solicitar una palabra clave para buscar coincidencias
        dentro de las respuestas almacenadas.

        Args:

            opcion (str): Subcomando opcional para operar sobre el historial.
                Puede ser `all`, `clear` o una cadena vacia para iniciar una
                busqueda interactiva.

        Returns:
            str: Respuesta del comando con el historial completo, el resultado
                de una busqueda o la confirmacion de limpieza.
        """
        opcion = opcion.strip().lower()

        if opcion == "all":
            if not self.historial_comandos:
                return "[Alerta] No hay historial almacenado."

            lineas = ["Historial completo:"]
            lineas.append("Fecha | Comando | Usuario | Respuesta")

            for registro in self.historial_comandos:
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
            self.historial_comandos.clear()
            return "[Alerta] Historial eliminado correctamente."

        palabra_clave = input("Ingresa la palabra clave a buscar: ").strip().lower()
        coincidencias: HistorialComandos = []
        if len(palabra_clave) == 0:
            return "[Error] Debes ingresar una palabra clave para la busqueda."
        # Iterar en el historico de comandos
        for registro in self.historial_comandos:
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

    def comando_salir(self) -> NoReturn:
        """Apaga el sistema y finaliza el programa.

        Raises:
            SystemExit: Finaliza la ejecucion del programa.
        """
        print("Apagando pseudoagente...")
        # Hace uso del modulo importado para salir del programa limpiamente
        sys.exit()


class AdminAgente(PseudoAgente):
    """Representa un pseudoagente tipo daministrador con comandos 
    cuyo comando historial no gasta tokens"""
    def __init__(self, nombre:str = "Athena") -> None:
        super().__init__(nombre)
        # Luego de la definición de la colección comandos al llamar __init__ de la clase padre
        # sobrescribo la cantidad de tokens que gasta el comando historial para que sean 0
        self.comandos["historial"]["tokens"] = 0

#Definiendo un tipo de excepción genérico se da claridad al código al momento de levantar la excepción
class TokensInsuficientesException(Exception):
    """Define una excepción personalizada para levantarla cuándo ya no hayan tokens disponibles"""
