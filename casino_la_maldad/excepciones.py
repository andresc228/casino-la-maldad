class CasinoError(Exception):
    """Excepción base del casino."""

class NombreInvalidoError(CasinoError):
    """Se lanza cuando el nombre del jugador no es válido."""

class SaldoInsuficienteError(CasinoError):
    """Se lanza cuando el jugador no tiene saldo suficiente."""

class CantidadInvalidaError(CasinoError):
    """Se lanza cuando una cantidad ingresada no es válida."""

class JuegoInvalidoError(CasinoError):
    """Se lanza cuando se selecciona un juego inexistente."""

class ApuestaInvalidaError(CasinoError):
    """Se lanza cuando la apuesta no cumple las reglas."""
