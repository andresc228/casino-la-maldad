from typing import List, Optional
from .dominio import Apuesta, Baraja, Caballo, Carta, Resultado

class Blackjack:
    def __init__(self):
        self.baraja = Baraja()
        self.mano_jugador: List[Carta] = []
        self.mano_crupier: List[Carta] = []
        self.estado_partida = "sin iniciar"
    def iniciar(self):
        self.estado_partida = "en curso"
        self.mano_jugador = [self.baraja.tomar_carta(), self.baraja.tomar_carta()]
        self.mano_crupier = [self.baraja.tomar_carta(), self.baraja.tomar_carta()]
    @staticmethod
    def valor_carta(carta: Carta) -> int:
        if carta.valor in ["J", "Q", "K"]: return 10
        if carta.valor == "A": return 11
        return int(carta.valor)
    @classmethod
    def calcular_total(cls, mano: List[Carta]) -> int:
        total, ases = 0, 0
        for carta in mano:
            if carta.valor == "A": ases += 1
            total += cls.valor_carta(carta)
        while total > 21 and ases > 0:
            total -= 10
            ases -= 1
        return total
    def pedir_carta(self):
        self.mano_jugador.append(self.baraja.tomar_carta())
    def turno_crupier(self):
        while self.calcular_total(self.mano_crupier) < 17:
            self.mano_crupier.append(self.baraja.tomar_carta())
    def jugar(self, apuesta: Apuesta) -> Resultado:
        total_jugador = self.calcular_total(self.mano_jugador)
        total_crupier = self.calcular_total(self.mano_crupier)
        if total_jugador > 21:
            return Resultado(False, 0, f"Perdiste. Te pasaste de 21. Total: {total_jugador}")
        if total_crupier > 21:
            return Resultado(True, apuesta.monto * 2, f"Ganaste. El crupier se pasó. Crupier: {total_crupier}")
        if total_jugador > total_crupier:
            return Resultado(True, apuesta.monto * 2, f"Ganaste. Tú: {total_jugador} | Crupier: {total_crupier}")
        if total_jugador == total_crupier:
            return Resultado(True, apuesta.monto, f"Empate. Recuperas la apuesta. Tú: {total_jugador} | Crupier: {total_crupier}")
        return Resultado(False, 0, f"Perdiste. Tú: {total_jugador} | Crupier: {total_crupier}")

class Poker:
    def __init__(self):
        self.baraja = Baraja()
        self.mano_jugador: List[Carta] = []
        self.mano_oponente: List[Carta] = []
        self.cartas_mesa: List[Carta] = []
    @staticmethod
    def valor_carta(carta: Carta) -> int:
        valores = {"A": 14, "K": 13, "Q": 12, "J": 11}
        return valores.get(carta.valor, int(carta.valor) if carta.valor.isdigit() else 0)
    def iniciar(self):
        self.mano_jugador = [self.baraja.tomar_carta(), self.baraja.tomar_carta()]
        self.mano_oponente = [self.baraja.tomar_carta(), self.baraja.tomar_carta()]
        self.cartas_mesa = []
    def flop(self):
        if len(self.cartas_mesa) == 0:
            self.cartas_mesa.extend([self.baraja.tomar_carta(), self.baraja.tomar_carta(), self.baraja.tomar_carta()])
    def turn(self):
        if len(self.cartas_mesa) == 3:
            self.cartas_mesa.append(self.baraja.tomar_carta())
    def river(self):
        if len(self.cartas_mesa) == 4:
            self.cartas_mesa.append(self.baraja.tomar_carta())
    def puntaje(self, mano: List[Carta]) -> int:
        return sum(self.valor_carta(carta) for carta in mano)
    def jugar(self, apuesta: Apuesta) -> Resultado:
        puntos_jugador = self.puntaje(self.mano_jugador + self.cartas_mesa)
        puntos_oponente = self.puntaje(self.mano_oponente + self.cartas_mesa)
        if puntos_jugador >= puntos_oponente:
            return Resultado(True, apuesta.monto * 2, f"Ganaste. Puntos: {puntos_jugador} | Bot: {puntos_oponente}")
        return Resultado(False, 0, f"Perdiste. Puntos: {puntos_jugador} | Bot: {puntos_oponente}")

class CarreraCaballo:
    def __init__(self):
        self.lista_caballos = [Caballo("Relámpago"), Caballo("Tormenta"), Caballo("Furia")]
        self.caballo_ganador: Optional[Caballo] = None
    def jugar(self, apuesta: Apuesta, caballo_elegido: Caballo) -> Resultado:
        if self.caballo_ganador == caballo_elegido:
            return Resultado(True, apuesta.monto * 2, f"Ganaste. Llegó primero {self.caballo_ganador.nombre}")
        return Resultado(False, 0, f"Perdiste. Llegó primero {self.caballo_ganador.nombre}")
