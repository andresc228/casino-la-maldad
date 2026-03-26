import tkinter as tk
import random

# ---------------- LOGICA ---------------- #

class Jugador:
    def __init__(self, nombre, saldo_dinero=1000, saldo_fichas=0):
        self.nombre = nombre
        self.saldoDinero = saldo_dinero
        self.saldoFichas = saldo_fichas

    def validar_nombre(self, nombre):
        return nombre.strip()

    def consultar_saldo(self):
        return self.saldoDinero, self.saldoFichas

    def convertir(self, tipo, cantidad):
        if cantidad <= 0:
            return False

        if tipo == "dinero_a_fichas":
            if cantidad > self.saldoDinero:
                return False
            self.saldoDinero -= cantidad
            self.saldoFichas += cantidad
            return True

        elif tipo == "fichas_a_dinero":
            if cantidad > self.saldoFichas:
                return False
            self.saldoFichas -= cantidad
            self.saldoDinero += cantidad
            return True

        return False

    def actualizar_saldo(self, resultado, monto):
        if resultado.gano:
            self.saldoFichas += resultado.recompensa
        else:
            self.saldoFichas -= monto


class Casino:
    def __init__(self):
        self.jugador = None

    def registrar_jugador(self, nombre):
        self.jugador = Jugador(nombre)

    def mostrar_menu(self):
        pass

    def seleccionar_juego(self, opcion):
        if opcion == "blackjack":
            return Blackjack()
        elif opcion == "poker":
            return Poker()
        elif opcion == "carrera":
            return CarreraCaballo()


class Caja:
    def __init__(self, tasaCambio):
        self.tasaCambio = tasaCambio

    def convertir(self, tipo, cantidad):
        return cantidad * self.tasaCambio


class Apuesta:
    def __init__(self, monto, tipoJuego):
        self.monto = monto
        self.tipoJuego = tipoJuego

    def apostar(self, monto):
        self.monto = monto


class Carta:
    def __init__(self, valor, palo):
        self.valor = valor
        self.palo = palo


class Blackjack:
    def __init__(self):
        self.manoJugador = []
        self.manoCrupier = []
        self.estadoPartida = None

    def jugar(self, apuesta):
        j = calcular_total_blackjack(self.manoJugador)
        c = calcular_total_blackjack(self.manoCrupier)

        gano = j <= 21 and (c > 21 or j > c)
        return Resultado(gano, apuesta.monto * 2)


class Poker:
    def __init__(self):
        self.manoJugador = []
        self.manoOponente = []

    def jugar(self, apuesta):
        total_jugador = sum(valor_poker(carta) for carta in self.manoJugador)
        total_oponente = sum(valor_poker(carta) for carta in self.manoOponente)
        return Resultado(total_jugador > total_oponente, apuesta.monto * 2)


class CarreraCaballo:
    def __init__(self):
        self.listaCaballos = []
        self.caballoGanador = None

    def jugar(self, apuesta):
        return Resultado(self.caballoGanador == "jugador", apuesta.monto * 2)


class Caballo:
    def __init__(self, nombre, posicion):
        self.nombre = nombre
        self.posicion = posicion


class Resultado:
    def __init__(self, gano, recompensa):
        self.gano = gano
        self.recompensa = recompensa


# ---------------- FUNCIONES DE APOYO ---------------- #

def crear_carta():
    valores = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    palos = ["♠", "♥", "♦", "♣"]
    return Carta(random.choice(valores), random.choice(palos))


def valor_blackjack(carta):
    if carta.valor in ["J", "Q", "K"]:
        return 10
    if carta.valor == "A":
        return 11
    return int(carta.valor)


def calcular_total_blackjack(mano):
    total = 0
    ases = 0

    for carta in mano:
        if carta.valor == "A":
            ases += 1
        total += valor_blackjack(carta)

    while total > 21 and ases > 0:
        total -= 10
        ases -= 1

    return total


def valor_poker(carta):
    if carta.valor == "A":
        return 14
    if carta.valor == "K":
        return 13
    if carta.valor == "Q":
        return 12
    if carta.valor == "J":
        return 11
    return int(carta.valor)


def color_palo(carta):
    return "red" if carta.palo in ["♥", "♦"] else "black"


def texto_carta(carta):
    return f"{carta.valor}{carta.palo}"


# ---------------- INTERFAZ ---------------- #

