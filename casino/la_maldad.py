"""
CASINO LA MALDAD - Versión profesional mejorada
Autor: Proyecto académico POO
Tecnología: Python + Tkinter

Incluye:
- Registro de jugador.
- Gestión de saldo en dinero y fichas.
- Conversión dinero <-> fichas.
- Sistema de apuestas con validaciones.
- Blackjack interactivo.
- Poker simplificado.
- Carrera de caballos animada.
- Interfaz gráfica moderna.
- Manejo de excepciones.
- Modularización interna por clases.
"""

import random
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import messagebox
from typing import List, Optional


# ============================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================

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


# ============================================================
# MODELO DEL DOMINIO
# ============================================================

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
        juegos = {
            "blackjack": Blackjack(),
            "poker": Poker(),
            "carrera": CarreraCaballo()
        }

        if opcion not in juegos:
            raise JuegoInvalidoError("Juego no disponible.")

        return juegos[opcion]


# ============================================================
# LÓGICA DE JUEGOS
# ============================================================

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
        if carta.valor in ["J", "Q", "K"]:
            return 10
        if carta.valor == "A":
            return 11
        return int(carta.valor)

    @classmethod
    def calcular_total(cls, mano: List[Carta]) -> int:
        total = 0
        ases = 0

        for carta in mano:
            if carta.valor == "A":
                ases += 1
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
        self.lista_caballos = [
            Caballo("Relámpago"),
            Caballo("Tormenta"),
            Caballo("Furia")
        ]
        self.caballo_ganador: Optional[Caballo] = None

    def jugar(self, apuesta: Apuesta, caballo_elegido: Caballo) -> Resultado:
        if self.caballo_ganador == caballo_elegido:
            return Resultado(True, apuesta.monto * 2, f"Ganaste. Llegó primero {self.caballo_ganador.nombre}")
        return Resultado(False, 0, f"Perdiste. Llegó primero {self.caballo_ganador.nombre}")


# ============================================================
# INTERFAZ GRÁFICA
# ============================================================

class CasinoApp:
    COLOR_FONDO = "#081C15"
    COLOR_PANEL = "#12372A"
    COLOR_PANEL_2 = "#1B4332"
    COLOR_DORADO = "#F2C94C"
    COLOR_TEXTO = "#F8F9FA"
    COLOR_BOTON = "#2D6A4F"
    COLOR_BOTON_HOVER = "#40916C"
    COLOR_ERROR = "#FFDD57"

    def __init__(self):
        self.casino = Casino()

        self.ventana = tk.Tk()
        self.ventana.title("Casino La Maldad - Versión Profesional")
        self.ventana.geometry("1100x720")
        self.ventana.minsize(1000, 650)
        self.ventana.configure(bg=self.COLOR_FONDO)

        self.frame_principal = tk.Frame(self.ventana, bg=self.COLOR_FONDO)
        self.frame_principal.pack(fill="both", expand=True)

        self.crear_encabezado()
        self.contenedor = tk.Frame(self.frame_principal, bg=self.COLOR_PANEL, bd=0)
        self.contenedor.pack(fill="both", expand=True, padx=28, pady=20)

        self.pantalla_registro()

    # ---------------- UTILIDADES UI ---------------- #

    def crear_encabezado(self):
        encabezado = tk.Frame(self.frame_principal, bg=self.COLOR_FONDO)
        encabezado.pack(fill="x", padx=28, pady=(18, 0))

        tk.Label(
            encabezado,
            text="♛ CASINO LA MALDAD",
            font=("Arial", 30, "bold"),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_DORADO
        ).pack(side="left")

        tk.Label(
            encabezado,
            text="Blackjack • Poker • Carrera de caballos",
            font=("Arial", 12),
            bg=self.COLOR_FONDO,
            fg="#B7E4C7"
        ).pack(side="right", pady=15)

    def limpiar(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    def crear_boton(self, padre, texto, comando, ancho=22, color=None):
        boton = tk.Button(
            padre,
            text=texto,
            command=comando,
            font=("Arial", 12, "bold"),
            bg=color or self.COLOR_BOTON,
            fg="white",
            activebackground=self.COLOR_BOTON_HOVER,
            activeforeground="white",
            width=ancho,
            pady=9,
            relief="flat",
            cursor="hand2"
        )
        return boton

    def crear_tarjeta(self, padre):
        tarjeta = tk.Frame(padre, bg=self.COLOR_PANEL_2, bd=0)
        tarjeta.pack(pady=20, padx=30, fill="both", expand=True)
        return tarjeta

    def mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)

    def mostrar_info(self, mensaje):
        messagebox.showinfo("Casino La Maldad", mensaje)

    def obtener_entero(self, entrada: tk.Entry) -> int:
        try:
            return int(entrada.get())
        except ValueError:
            raise CantidadInvalidaError("Debes ingresar un número entero válido.")

    def color_palo(self, carta: Carta) -> str:
        return "#D00000" if carta.palo in ["♥", "♦"] else "#111111"

    def dibujar_carta(self, canvas, x, y, carta: Optional[Carta], oculta=False):
        canvas.create_rectangle(x + 4, y + 4, x + 74, y + 104, fill="#000000", outline="")
        canvas.create_rectangle(x, y, x + 70, y + 100, fill="white", outline="#D4AF37", width=2)

        if oculta:
            canvas.create_rectangle(x + 8, y + 8, x + 62, y + 92, fill="#1D3557", outline="#457B9D", width=2)
            canvas.create_text(x + 35, y + 50, text="♛", font=("Arial", 24, "bold"), fill=self.COLOR_DORADO)
        else:
            canvas.create_text(
                x + 35,
                y + 50,
                text=carta.texto(),
                font=("Arial", 18, "bold"),
                fill=self.color_palo(carta)
            )

    def panel_saldo(self, padre):
        jugador = self.casino.obtener_jugador()
        dinero, fichas = jugador.consultar_saldo()

        barra = tk.Frame(padre, bg=self.COLOR_PANEL, height=55)
        barra.pack(fill="x", pady=(0, 10))

        tk.Label(
            barra,
            text=f"Jugador: {jugador.nombre}",
            font=("Arial", 13, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO
        ).pack(side="left", padx=15)

        tk.Label(
            barra,
            text=f"Dinero: ${dinero}",
            font=("Arial", 13, "bold"),
            bg=self.COLOR_PANEL,
            fg="#95D5B2"
        ).pack(side="right", padx=15)

        tk.Label(
            barra,
            text=f"Fichas: {fichas}",
            font=("Arial", 13, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_DORADO
        ).pack(side="right", padx=15)

    # ---------------- PANTALLAS ---------------- #

    def pantalla_registro(self):
        self.limpiar()

        tarjeta = self.crear_tarjeta(self.contenedor)

        tk.Label(
            tarjeta,
            text="Bienvenido al casino",
            font=("Arial", 26, "bold"),
            bg=self.COLOR_PANEL_2,
            fg=self.COLOR_DORADO
        ).pack(pady=(80, 10))

        tk.Label(
            tarjeta,
            text="Registra tu nombre para iniciar la partida.",
            font=("Arial", 14),
            bg=self.COLOR_PANEL_2,
            fg=self.COLOR_TEXTO
        ).pack(pady=5)

        entrada_nombre = tk.Entry(
            tarjeta,
            font=("Arial", 16),
            justify="center",
            width=30,
            relief="flat"
        )
        entrada_nombre.pack(pady=25, ipady=8)
        entrada_nombre.focus()

        def registrar():
            try:
                self.casino.registrar_jugador(entrada_nombre.get())
                self.pantalla_menu()
            except CasinoError as error:
                self.mostrar_error(str(error))

        self.crear_boton(tarjeta, "Entrar al casino", registrar, 24, self.COLOR_DORADO).pack(pady=10)

    def pantalla_menu(self):
        self.limpiar()
        self.panel_saldo(self.contenedor)

        tarjeta = self.crear_tarjeta(self.contenedor)

        tk.Label(
            tarjeta,
            text="Menú principal",
            font=("Arial", 26, "bold"),
            bg=self.COLOR_PANEL_2,
            fg=self.COLOR_DORADO
        ).pack(pady=(35, 15))

        tk.Label(
            tarjeta,
            text="Selecciona una opción para continuar.",
            font=("Arial", 13),
            bg=self.COLOR_PANEL_2,
            fg=self.COLOR_TEXTO
        ).pack(pady=(0, 20))

        grid = tk.Frame(tarjeta, bg=self.COLOR_PANEL_2)
        grid.pack(pady=10)

        opciones = [
            ("Convertir dinero / fichas", self.pantalla_convertir),
            ("Jugar Blackjack", lambda: self.pantalla_apuesta("blackjack")),
            ("Jugar Poker", lambda: self.pantalla_apuesta("poker")),
            ("Carrera de caballos", lambda: self.pantalla_apuesta("carrera")),
        ]

        for i, (texto, comando) in enumerate(opciones):
            self.crear_boton(grid, texto, comando, 26).grid(row=i // 2, column=i % 2, padx=12, pady=12)

    def pantalla_convertir(self):
        self.limpiar()
        self.panel_saldo(self.contenedor)

        tarjeta = self.crear_tarjeta(self.contenedor)

        tk.Label(
            tarjeta,
            text="Conversión de saldo",
            font=("Arial", 24, "bold"),
            bg=self.COLOR_PANEL_2,
            fg=self.COLOR_DORADO
        ).pack(pady=30)

        tk.Label(
            tarjeta,
            text="Cantidad",
            font=("Arial", 13, "bold"),
            bg=self.COLOR_PANEL_2,
            fg=self.COLOR_TEXTO
        ).pack()

        entrada = tk.Entry(tarjeta, font=("Arial", 15), justify="center", width=20, relief="flat")
        entrada.pack(pady=12, ipady=7)

        def convertir(tipo):
            try:
                cantidad = self.obtener_entero(entrada)
                jugador = self.casino.obtener_jugador()
                jugador.convertir(tipo, cantidad)
                self.mostrar_info("Conversión realizada correctamente.")
                self.pantalla_menu()
            except CasinoError as error:
                self.mostrar_error(str(error))

        botones = tk.Frame(tarjeta, bg=self.COLOR_PANEL_2)
        botones.pack(pady=18)

        self.crear_boton(botones, "Dinero → Fichas", lambda: convertir("dinero_a_fichas"), 20).grid(row=0, column=0, padx=10)
        self.crear_boton(botones, "Fichas → Dinero", lambda: convertir("fichas_a_dinero"), 20).grid(row=0, column=1, padx=10)
        self.crear_boton(tarjeta, "Volver", self.pantalla_menu, 18).pack(pady=18)

    def pantalla_apuesta(self, tipo_juego: str):
        self.limpiar()
        self.panel_saldo(self.contenedor)

        nombres = {
            "blackjack": "Blackjack",
            "poker": "Poker",
            "carrera": "Carrera de caballos"
        }

        tarjeta = self.crear_tarjeta(self.contenedor)

        tk.Label(
            tarjeta,
            text=f"Apuesta para {nombres[tipo_juego]}",
            font=("Arial", 24, "bold"),
            bg=self.COLOR_PANEL_2,
            fg=self.COLOR_DORADO
        ).pack(pady=30)

        tk.Label(
            tarjeta,
            text="Ingresa la cantidad de fichas que deseas apostar.",
            font=("Arial", 13),
            bg=self.COLOR_PANEL_2,
            fg=self.COLOR_TEXTO
        ).pack()

        entrada = tk.Entry(tarjeta, font=("Arial", 15), justify="center", width=20, relief="flat")
        entrada.pack(pady=18, ipady=7)

        def iniciar():
            try:
                monto = self.obtener_entero(entrada)
                apuesta = Apuesta(monto, tipo_juego)
                apuesta.validar()

                jugador = self.casino.obtener_jugador()
                jugador.descontar_apuesta(monto)

                if tipo_juego == "blackjack":
                    self.pantalla_blackjack(apuesta)
                elif tipo_juego == "poker":
                    self.pantalla_poker(apuesta)
                elif tipo_juego == "carrera":
                    self.pantalla_carrera(apuesta)

            except CasinoError as error:
                self.mostrar_error(str(error))

        self.crear_boton(tarjeta, "Iniciar juego", iniciar, 20, self.COLOR_DORADO).pack(pady=8)
        self.crear_boton(tarjeta, "Volver", self.pantalla_menu, 18).pack(pady=8)

    # ---------------- BLACKJACK ---------------- #

    def pantalla_blackjack(self, apuesta: Apuesta):
        self.limpiar()
        self.panel_saldo(self.contenedor)

        juego: Blackjack = self.casino.seleccionar_juego("blackjack")
        juego.iniciar()

        zona = tk.Frame(self.contenedor, bg=self.COLOR_PANEL_2)
        zona.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(zona, width=1000, height=410, bg="#0B6E4F", highlightthickness=0)
        canvas.pack(pady=15)

        mensaje = tk.Label(zona, text="", font=("Arial", 13, "bold"), bg=self.COLOR_PANEL_2, fg=self.COLOR_DORADO)
        mensaje.pack(pady=8)

        controles = tk.Frame(zona, bg=self.COLOR_PANEL_2)
        controles.pack(pady=8)

        def redibujar(mostrar_crupier=True):
            canvas.delete("all")
            canvas.create_text(120, 30, text="CRUPIER", fill="white", font=("Arial", 15, "bold"))
            canvas.create_text(120, 225, text="JUGADOR", fill="white", font=("Arial", 15, "bold"))

            for i, carta in enumerate(juego.mano_crupier):
                self.dibujar_carta(canvas, 80 + i * 85, 55, carta, oculta=(not mostrar_crupier and i == 1))

            for i, carta in enumerate(juego.mano_jugador):
                self.dibujar_carta(canvas, 80 + i * 85, 250, carta)

            total_j = juego.calcular_total(juego.mano_jugador)
            total_c = juego.calcular_total(juego.mano_crupier) if mostrar_crupier else "?"

            canvas.create_text(780, 95, text=f"Total crupier: {total_c}", fill="white", font=("Arial", 14, "bold"))
            canvas.create_text(780, 295, text=f"Total jugador: {total_j}", fill="white", font=("Arial", 14, "bold"))

        def finalizar(resultado: Resultado):
            jugador = self.casino.obtener_jugador()
            jugador.sumar_fichas(resultado.recompensa)
            mensaje.config(text=resultado.mensaje)
            for widget in controles.winfo_children():
                widget.destroy()
            self.crear_boton(controles, "Volver al menú", self.pantalla_menu, 18).pack(side="left", padx=8)

        def pedir():
            juego.pedir_carta()
            redibujar(False)

            if juego.calcular_total(juego.mano_jugador) > 21:
                resultado = juego.jugar(apuesta)
                redibujar(True)
                finalizar(resultado)

        def plantarse():
            juego.turno_crupier()
            redibujar(True)
            resultado = juego.jugar(apuesta)
            finalizar(resultado)

        redibujar(False)

        self.crear_boton(controles, "Pedir carta", pedir, 16).pack(side="left", padx=8)
        self.crear_boton(controles, "Plantarse", plantarse, 16).pack(side="left", padx=8)
        self.crear_boton(controles, "Rendirse", self.pantalla_menu, 16).pack(side="left", padx=8)

    # ---------------- POKER ---------------- #

    def pantalla_poker(self, apuesta: Apuesta):
        self.limpiar()
        self.panel_saldo(self.contenedor)

        juego: Poker = self.casino.seleccionar_juego("poker")
        juego.iniciar()

        zona = tk.Frame(self.contenedor, bg=self.COLOR_PANEL_2)
        zona.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(zona, width=1000, height=410, bg="#0B6E4F", highlightthickness=0)
        canvas.pack(pady=15)

        mensaje = tk.Label(zona, text="Revela las cartas de la mesa.", font=("Arial", 13, "bold"), bg=self.COLOR_PANEL_2, fg=self.COLOR_DORADO)
        mensaje.pack(pady=8)

        controles = tk.Frame(zona, bg=self.COLOR_PANEL_2)
        controles.pack(pady=8)

        def dibujar(mostrar_bot=False):
            canvas.delete("all")
            canvas.create_text(120, 30, text="BOT", fill="white", font=("Arial", 15, "bold"))
            canvas.create_text(500, 150, text="MESA", fill="white", font=("Arial", 15, "bold"))
            canvas.create_text(120, 305, text="JUGADOR", fill="white", font=("Arial", 15, "bold"))

            for i, carta in enumerate(juego.mano_oponente):
                self.dibujar_carta(canvas, 80 + i * 85, 55, carta, oculta=not mostrar_bot)

            for i, carta in enumerate(juego.cartas_mesa):
                self.dibujar_carta(canvas, 300 + i * 85, 175, carta)

            for i, carta in enumerate(juego.mano_jugador):
                self.dibujar_carta(canvas, 80 + i * 85, 325, carta)

        def limpiar_controles():
            for widget in controles.winfo_children():
                widget.destroy()

        def hacer_flop():
            juego.flop()
            mensaje.config(text="Flop revelado.")
            dibujar()

        def hacer_turn():
            juego.turn()
            mensaje.config(text="Turn revelado.")
            dibujar()

        def hacer_river():
            juego.river()
            dibujar(True)

            resultado = juego.jugar(apuesta)
            jugador = self.casino.obtener_jugador()
            jugador.sumar_fichas(resultado.recompensa)
            mensaje.config(text=resultado.mensaje)

            limpiar_controles()
            self.crear_boton(controles, "Volver al menú", self.pantalla_menu, 18).pack(side="left", padx=8)

        dibujar()

        self.crear_boton(controles, "Flop", hacer_flop, 14).pack(side="left", padx=8)
        self.crear_boton(controles, "Turn", hacer_turn, 14).pack(side="left", padx=8)
        self.crear_boton(controles, "River", hacer_river, 14).pack(side="left", padx=8)
        self.crear_boton(controles, "Volver", self.pantalla_menu, 14).pack(side="left", padx=8)

    # ---------------- CARRERA ---------------- #

    def pantalla_carrera(self, apuesta: Apuesta):
        self.limpiar()
        self.panel_saldo(self.contenedor)

        juego: CarreraCaballo = self.casino.seleccionar_juego("carrera")

        zona = tk.Frame(self.contenedor, bg=self.COLOR_PANEL_2)
        zona.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(zona, width=1000, height=430, bg="#184E77", highlightthickness=0)
        canvas.pack(pady=15)

        mensaje = tk.Label(
            zona,
            text="Selecciona el caballo por el que vas a apostar.",
            font=("Arial", 13, "bold"),
            bg=self.COLOR_PANEL_2,
            fg=self.COLOR_DORADO
        )
        mensaje.pack(pady=8)

        controles = tk.Frame(zona, bg=self.COLOR_PANEL_2)
        controles.pack(pady=8)

        caballo_elegido = {"caballo": None}
        objetos = []

        def dibujar_pista():
            canvas.delete("all")
            objetos.clear()

            meta_x = 850
            canvas.create_text(500, 30, text="GRAN CARRERA LA MALDAD", fill=self.COLOR_DORADO, font=("Arial", 20, "bold"))
            canvas.create_line(meta_x, 70, meta_x, 380, fill="white", width=4)

            for y in range(70, 380, 20):
                color = "white" if (y // 20) % 2 == 0 else "black"
                canvas.create_rectangle(meta_x, y, meta_x + 30, y + 20, fill=color, outline=color)

            for i, caballo in enumerate(juego.lista_caballos):
                y = 105 + i * 95
                canvas.create_line(60, y + 45, 900, y + 45, fill="white", dash=(8, 8))
                cuerpo = canvas.create_rectangle(60, y, 190, y + 45, fill="#8B4513", outline="#3E1F00", width=2)
                texto = canvas.create_text(125, y + 23, text=f"♞ {caballo.nombre}", fill="white", font=("Arial", 12, "bold"))
                objetos.append((cuerpo, texto, caballo))

        def seleccionar(caballo: Caballo):
            caballo_elegido["caballo"] = caballo
            mensaje.config(text=f"Apostaste por {caballo.nombre}. Ahora inicia la carrera.")

        def limpiar_controles():
            for widget in controles.winfo_children():
                widget.destroy()

        def correr():
            if caballo_elegido["caballo"] is None:
                mensaje.config(text="Primero debes seleccionar un caballo.")
                return

            limpiar_controles()

            meta_x = 850
            ganador = None

            for caballo in juego.lista_caballos:
                caballo.posicion = 0

            while ganador is None:
                for cuerpo, texto, caballo in objetos:
                    avance = random.randint(6, 23)
                    caballo.posicion += avance
                    canvas.move(cuerpo, avance, 0)
                    canvas.move(texto, avance, 0)

                    coords = canvas.coords(cuerpo)
                    if coords[2] >= meta_x:
                        ganador = caballo
                        break

                self.ventana.update()
                self.ventana.after(45)

            juego.caballo_ganador = ganador
            resultado = juego.jugar(apuesta, caballo_elegido["caballo"])

            jugador = self.casino.obtener_jugador()
            jugador.sumar_fichas(resultado.recompensa)

            mensaje.config(text=resultado.mensaje)
            self.crear_boton(controles, "Volver al menú", self.pantalla_menu, 18).pack(side="left", padx=8)

        dibujar_pista()

        for caballo in juego.lista_caballos:
            self.crear_boton(controles, caballo.nombre, lambda c=caballo: seleccionar(c), 14).pack(side="left", padx=6)

        self.crear_boton(controles, "Iniciar carrera", correr, 16, self.COLOR_DORADO).pack(side="left", padx=8)
        self.crear_boton(controles, "Volver", self.pantalla_menu, 14).pack(side="left", padx=6)

    def ejecutar(self):
        self.ventana.mainloop()


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    app = CasinoApp()
    app.ejecutar()