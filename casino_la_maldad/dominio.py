import random
from dataclasses import dataclass
from typing import List, Optional
from .excepciones import *

@dataclass
class Resultado:
    gano: bool
    recompensa: int
    mensaje: str

@dataclass
class Carta:
    valor: str
    palo: str
    def texto(self) -> str:
        return f"{self.valor}{self.palo}"

class Baraja:
    valores = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    palos = ["♠", "♥", "♦", "♣"]
    def __init__(self):
        self.cartas: List[Carta] = []
        self.reiniciar()
    def reiniciar(self):
        self.cartas = [Carta(valor, palo) for valor in self.valores for palo in self.palos]
        random.shuffle(self.cartas)
    def tomar_carta(self) -> Carta:
        if not self.cartas:
            self.reiniciar()
        return self.cartas.pop()

@dataclass
class Jugador:
    nombre: str
    saldo_dinero: int = 1000
    saldo_fichas: int = 0
    def __post_init__(self):
        self.nombre = self.validar_nombre(self.nombre)
    @staticmethod
    def validar_nombre(nombre: str) -> str:
        nombre = nombre.strip()
        if len(nombre) < 2:
            raise NombreInvalidoError("El nombre debe tener mínimo 2 caracteres.")
        return nombre.title()
    def consultar_saldo(self):
        return self.saldo_dinero, self.saldo_fichas
    def convertir(self, tipo: str, cantidad: int):
        if cantidad <= 0:
            raise CantidadInvalidaError("La cantidad debe ser mayor que cero.")
        if tipo == "dinero_a_fichas":
            if cantidad > self.saldo_dinero:
                raise SaldoInsuficienteError("No tienes dinero suficiente.")
            self.saldo_dinero -= cantidad
            self.saldo_fichas += cantidad
        elif tipo == "fichas_a_dinero":
            if cantidad > self.saldo_fichas:
                raise SaldoInsuficienteError("No tienes fichas suficientes.")
            self.saldo_fichas -= cantidad
            self.saldo_dinero += cantidad
        else:
            raise CantidadInvalidaError("Tipo de conversión no válido.")
    def descontar_apuesta(self, monto: int):
        if monto <= 0:
            raise ApuestaInvalidaError("La apuesta debe ser mayor que cero.")
        if monto > self.saldo_fichas:
            raise SaldoInsuficienteError("No tienes fichas suficientes para apostar.")
        self.saldo_fichas -= monto
    def sumar_fichas(self, cantidad: int):
        if cantidad > 0:
            self.saldo_fichas += cantidad

@dataclass
class Apuesta:
    monto: int
    tipo_juego: str
    def validar(self):
        if self.monto <= 0:
            raise ApuestaInvalidaError("La apuesta debe ser mayor que cero.")

@dataclass
class Caballo:
    nombre: str
    posicion: int = 0

class Caja:
    def __init__(self, tasa_cambio: int = 1):
        self.tasa_cambio = tasa_cambio
    def convertir(self, cantidad: int) -> int:
        return cantidad * self.tasa_cambio

class Casino:
    def __init__(self):
        self.jugador: Optional[Jugador] = None
        self.caja = Caja()
    def registrar_jugador(self, nombre: str):
        self.jugador = Jugador(nombre)
    def obtener_jugador(self) -> Jugador:
        if self.jugador is None:
            raise CasinoError("No hay jugador registrado.")
        return self.jugador
    def seleccionar_juego(self, opcion: str):
        from .juegos import Blackjack, Poker, CarreraCaballo
        juegos = {"blackjack": Blackjack(), "poker": Poker(), "carrera": CarreraCaballo()}
        if opcion not in juegos:
            raise JuegoInvalidoError("Juego no disponible.")
        return juegos[opcion]
