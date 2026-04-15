"""Clases para representar agentes de la agencia."""

from dataclasses import dataclass

# Notas del reto
# - Redefino las clases PseudoAgente y AgenteAdmin con el decorador dataclass que reduce
# la cantidad de código a escribir para usar en clases que principalmente sirven como
# contenedores de datos.
# - Elimino todos los métodos relacionados a las primeras sesiones ya que no tiene sentido
# agregarlas en el contexto actual del reto.
# - La clase AgenteAdmin difiere de PseudoAgente en que la primera
# tiene un descuento de 10 unidades de energía en la ejecución de las misiones.

@dataclass
class PseudoAgente:
    """Representa un agente base con energia y rol configurable.

    Attributes:
        nombre: Nombre unico del agente.
        rol: Rol funcional del agente.
        energia: Energia disponible para ejecutar misiones.
    """

    nombre: str
    rol: str
    energia: int
    descuento_energia = 0

    def consumir_energia(self, energia_requerida: int) -> int:
        """Descuenta energia al agente si cuenta con recursos suficientes.

        Args:
            energia_requerida: Energia necesaria para completar la mision.

        Returns:
            int: Energia restante del agente.

        Raises:
            ValueError: Si la energia requerida es negativa o insuficiente.
        """
        if energia_requerida < 0:
            raise ValueError("La energia requerida no puede ser negativa")
        costo = max(0, energia_requerida - self.descuento_energia)
        if self.energia < costo:
            raise ValueError(
                "El agente no tiene energia suficiente para completar la mision"
            )
        self.energia -= costo
        return self.energia


@dataclass
class AgenteAdmin(PseudoAgente):
    """Agente con un descuento fijo de energia al ejecutar misiones."""

    descuento_energia = 10


def reconstruir_agente_desde_fila(
    fila: dict[str, object] | None,
) -> PseudoAgente | AgenteAdmin | None:
    """Reconstruye la clase correcta del agente desde una fila de base de datos.

    Args:
        fila: Registro de la tabla `agentes`.

    Returns:
        PseudoAgente | AgenteAdmin | None: Instancia del agente o `None`.
    """
    if fila is None:
        return None

    nombre = str(fila["nombre"])
    rol = str(fila["rol"])
    energia = int(fila["energia"])

    if rol == "admin":
        return AgenteAdmin(nombre=nombre, rol=rol, energia=energia)
    return PseudoAgente(nombre=nombre, rol=rol, energia=energia)
