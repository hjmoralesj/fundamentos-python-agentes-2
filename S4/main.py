"""
Agente de consola con autenticacion y ejecucion de comandos.
Taller Semana 4
Julian Morales
hector.morales@sofka.com.co
Notas:
- Se crea la clase PseudoAgente, AdminAgente para encapsular 
comportamiento de los comandos del pseudoagente
- Se define TokensInsuficientesException para controlar 
claramente excepción cuando ya no hayan tokens suficientes
- Se agrega nuevo comando lanzar_dado
- De acuerdo a si el usuario es invitado o admin 
se instancia un agente PseudoAgente o AdminAgente respectivamente
"""

# Imports
from agente import PseudoAgente, AdminAgente, TokensInsuficientesException

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

    usuario_autenticado = autenticar_usuario(usuarios)
    # Si no hay usuario autenticado se usa return para
    # terminar la ejecucion de la funcion principal y asi terminar el programa
    if usuario_autenticado is not None:
        if usuario_autenticado == "admin":
            agente = AdminAgente()
        else:
            agente = PseudoAgente()
    else:
        return

    print("\n" + "-" * 40)
    print("Acceso concedido. Cargando menu principal...")
    print("-" * 40)
    print("\nUsa alguno de estos comandos:")
    print(agente.mostrar_ayuda())

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
        comando_info = agente.comandos.get(nombre_comando)

        # Si en el diccionario no se encuentra coincidencia se valida a None
        if comando_info is None:
            respuesta = "[Error] Comando no reconocido. Usa 'ayuda' para ver las opciones disponibles."
            print(respuesta)
            agente.registrar_comando(
                comando,
                usuario_autenticado,
                respuesta
            )
            # Usado para saltar a la siguiente iteracion del ciclo
            continue

        try:
            respuesta = agente.ejecutar_comando(
                comando_info, usuario_autenticado, argumento
            )
            print(respuesta)
        except PermissionError:
            respuesta = (
                "[Acceso Denegado] Este comando requiere privilegios de "
                "administrador."
            )
        except KeyboardInterrupt:
            print("\n[Alerta] Operacion cancelada por el usuario.")
        except TokensInsuficientesException:
            print("\n[Alerta] No tiene tokens suficientes para ejecutar el comando.")

        print(f"\nTokens disponibles: {agente.tokens}")
        agente.registrar_comando(
            comando,
            usuario_autenticado,
            respuesta
        )


# Bloque de entrada
if __name__ == "__main__":
    main()
