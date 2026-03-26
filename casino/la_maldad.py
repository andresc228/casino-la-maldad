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


