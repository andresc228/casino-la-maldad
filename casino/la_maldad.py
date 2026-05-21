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
# INTERFAZ GRÁFICA PREMIUM
# ============================================================

class CasinoApp:
    COLOR_FONDO = "#050B0F"
    COLOR_FONDO_2 = "#081820"
    COLOR_PANEL = "#0D1F24"
    COLOR_PANEL_2 = "#102B2C"
    COLOR_PANEL_3 = "#173D35"
    COLOR_MESA = "#075A3C"
    COLOR_MESA_OSCURO = "#053A2A"
    COLOR_DORADO = "#F6C453"
    COLOR_DORADO_2 = "#B88917"
    COLOR_TEXTO = "#F8F9FA"
    COLOR_TEXTO_SUAVE = "#B7E4C7"
    COLOR_BOTON = "#1B6B4A"
    COLOR_BOTON_HOVER = "#2EA66F"
    COLOR_ERROR = "#FFDD57"
    FUENTE_TITULO = ("Segoe UI", 30, "bold")
    FUENTE_SUBTITULO = ("Segoe UI", 13)
    FUENTE_NORMAL = ("Segoe UI", 12)
    FUENTE_BOTON = ("Segoe UI", 12, "bold")

    def __init__(self):
        self.casino = Casino()
        self.particulas = []

        self.ventana = tk.Tk()
        self.ventana.title("Casino La Maldad - Ultra Premium")
        self.ventana.geometry("1180x760")
        self.ventana.minsize(1050, 680)
        self.ventana.configure(bg=self.COLOR_FONDO)

        self.frame_principal = tk.Frame(self.ventana, bg=self.COLOR_FONDO)
        self.frame_principal.pack(fill="both", expand=True)

        self.fondo_animado = tk.Canvas(self.frame_principal, bg=self.COLOR_FONDO, highlightthickness=0)
        self.fondo_animado.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.crear_fondo_premium()
        self.animar_particulas()

        self.capa_ui = tk.Frame(self.frame_principal, bg=self.COLOR_FONDO)
        self.capa_ui.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.crear_encabezado()
        self.contenedor = tk.Frame(self.capa_ui, bg=self.COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground="#21453D")
        self.contenedor.pack(fill="both", expand=True, padx=30, pady=20)

        self.pantalla_registro()

    # ---------------- UTILIDADES UI PREMIUM ---------------- #

    def crear_fondo_premium(self):
        self.fondo_animado.delete("all")
        for i in range(0, 760, 8):
            r = min(18, 5 + i // 60)
            color = f"#{r:02x}{max(11, 20 + i // 35):02x}{max(15, 25 + i // 45):02x}"
            self.fondo_animado.create_rectangle(0, i, 2000, i + 8, fill=color, outline="")

        for _ in range(55):
            x = random.randint(0, 1180)
            y = random.randint(0, 760)
            size = random.choice([1, 1, 2, 2, 3])
            vel = random.choice([0.15, 0.25, 0.35, 0.5])
            item = self.fondo_animado.create_oval(x, y, x + size, y + size, fill=self.COLOR_DORADO, outline="")
            self.particulas.append([item, vel])

    def animar_particulas(self):
        for item, vel in self.particulas:
            self.fondo_animado.move(item, 0, vel)
            coords = self.fondo_animado.coords(item)
            if coords and coords[1] > 780:
                self.fondo_animado.move(item, 0, -800)
        self.ventana.after(45, self.animar_particulas)

    def crear_encabezado(self):
        encabezado = tk.Frame(self.capa_ui, bg=self.COLOR_FONDO)
        encabezado.pack(fill="x", padx=30, pady=(18, 0))

        izquierda = tk.Frame(encabezado, bg=self.COLOR_FONDO)
        izquierda.pack(side="left")

        tk.Label(
            izquierda,
            text="♛ CASINO LA MALDAD",
            font=self.FUENTE_TITULO,
            bg=self.COLOR_FONDO,
            fg=self.COLOR_DORADO
        ).pack(anchor="w")

        tk.Label(
            izquierda,
            text="Experiencia premium · Blackjack · Poker · Carrera de caballos",
            font=("Segoe UI", 11),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO_SUAVE
        ).pack(anchor="w", pady=(0, 4))

        insignia = tk.Label(
            encabezado,
            text="● LIVE TABLES",
            font=("Segoe UI", 11, "bold"),
            bg="#112D25",
            fg="#63E6BE",
            padx=18,
            pady=8
        )
        insignia.pack(side="right", pady=16)

    def limpiar(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    def efecto_hover(self, boton, color_base, color_hover):
        boton.bind("<Enter>", lambda _e: boton.config(bg=color_hover))
        boton.bind("<Leave>", lambda _e: boton.config(bg=color_base))

    def crear_boton(self, padre, texto, comando, ancho=22, color=None):
        color_base = color or self.COLOR_BOTON
        color_hover = self.COLOR_DORADO_2 if color == self.COLOR_DORADO else self.COLOR_BOTON_HOVER
        boton = tk.Button(
            padre,
            text=texto,
            command=comando,
            font=self.FUENTE_BOTON,
            bg=color_base,
            fg="#07110D" if color == self.COLOR_DORADO else "white",
            activebackground=color_hover,
            activeforeground="white",
            width=ancho,
            pady=10,
            relief="flat",
            cursor="hand2",
            bd=0
        )
        self.efecto_hover(boton, color_base, color_hover)
        return boton

    def crear_tarjeta(self, padre, relleno=True):
        exterior = tk.Frame(padre, bg="#050805")
        exterior.pack(pady=20, padx=30, fill="both", expand=relleno)
        tarjeta = tk.Frame(exterior, bg=self.COLOR_PANEL_2, bd=0, highlightthickness=1, highlightbackground="#2A6F59")
        tarjeta.pack(padx=2, pady=2, fill="both", expand=True)
        return tarjeta

    def titulo_pantalla(self, padre, titulo, subtitulo=""):
        tk.Label(padre, text=titulo, font=("Segoe UI", 26, "bold"), bg=self.COLOR_PANEL_2, fg=self.COLOR_DORADO).pack(pady=(32, 8))
        if subtitulo:
            tk.Label(padre, text=subtitulo, font=self.FUENTE_SUBTITULO, bg=self.COLOR_PANEL_2, fg=self.COLOR_TEXTO_SUAVE).pack(pady=(0, 18))

    def mostrar_error(self, mensaje):
        messagebox.showerror("Casino La Maldad", mensaje)

    def mostrar_info(self, mensaje):
        messagebox.showinfo("Casino La Maldad", mensaje)

    def obtener_entero(self, entrada: tk.Entry) -> int:
        try:
            return int(entrada.get())
        except ValueError:
            raise CantidadInvalidaError("Debes ingresar un número entero válido.")

    def color_palo(self, carta: Carta) -> str:
        return "#C1121F" if carta.palo in ["♥", "♦"] else "#111111"

    def dibujar_carta(self, canvas, x, y, carta: Optional[Carta], oculta=False, escala=1.0):
        w, h = int(74 * escala), int(108 * escala)
        canvas.create_rectangle(x + 6, y + 7, x + w + 6, y + h + 7, fill="#000000", outline="", stipple="gray50")
        canvas.create_rectangle(x, y, x + w, y + h, fill="#FFFDF7", outline=self.COLOR_DORADO, width=2)
        canvas.create_rectangle(x + 5, y + 5, x + w - 5, y + h - 5, outline="#D9B650", width=1)

        if oculta:
            canvas.create_rectangle(x + 10, y + 10, x + w - 10, y + h - 10, fill="#0A2342", outline="#2D6A9F", width=2)
            canvas.create_text(x + w / 2, y + h / 2, text="♛", font=("Segoe UI", int(27 * escala), "bold"), fill=self.COLOR_DORADO)
        else:
            canvas.create_text(x + 15, y + 18, text=carta.valor, font=("Segoe UI", int(12 * escala), "bold"), fill=self.color_palo(carta))
            canvas.create_text(x + w - 15, y + h - 18, text=carta.valor, font=("Segoe UI", int(12 * escala), "bold"), fill=self.color_palo(carta))
            canvas.create_text(x + w / 2, y + h / 2, text=carta.palo, font=("Segoe UI", int(29 * escala), "bold"), fill=self.color_palo(carta))

    def dibujar_mesa_premium(self, canvas, titulo):
        canvas.delete("all")
        canvas.create_rectangle(0, 0, 1200, 460, fill=self.COLOR_MESA_OSCURO, outline="")
        for i in range(30):
            color = "#086344" if i % 2 == 0 else "#07563B"
            canvas.create_oval(80 - i * 7, 20 - i * 3, 1120 + i * 7, 470 + i * 4, outline=color, width=2)
        canvas.create_oval(60, 30, 1140, 445, outline=self.COLOR_DORADO, width=4)
        canvas.create_oval(90, 58, 1110, 420, outline="#3EA875", width=2)
        canvas.create_text(590, 40, text=titulo, fill=self.COLOR_DORADO, font=("Segoe UI", 18, "bold"))

    def animar_carta_desde_mazo(self, canvas, destino_x, destino_y, carta, oculta=False):
        inicio_x, inicio_y = 560, 175
        pasos = 22
        for paso in range(1, pasos + 1):
            progreso = self.easing_suave(paso / pasos)
            x = inicio_x + (destino_x - inicio_x) * progreso
            y = inicio_y + (destino_y - inicio_y) * progreso
            temporal = "carta_animada"
            canvas.delete(temporal)
            canvas.create_rectangle(x + 7, y + 8, x + 87, y + 122, fill="#000000", outline="", tags=temporal)
            canvas.create_rectangle(x, y, x + 80, y + 114, fill="#FFFDF7", outline=self.COLOR_DORADO, width=3, tags=temporal)
            canvas.create_text(x + 40, y + 57, text="♛" if oculta else carta.texto(), font=("Segoe UI", 23, "bold"), fill=self.COLOR_DORADO if oculta else self.color_palo(carta), tags=temporal)
            canvas.update()
            self.ventana.after(10)
        canvas.delete("carta_animada")

    def easing_suave(self, t):
        return t * t * (3 - 2 * t)

    def panel_saldo(self, padre):
        jugador = self.casino.obtener_jugador()
        dinero, fichas = jugador.consultar_saldo()
        barra = tk.Frame(padre, bg=self.COLOR_PANEL, height=58)
        barra.pack(fill="x", pady=(0, 10))
        datos = [(f"👤 {jugador.nombre}", self.COLOR_TEXTO), (f"💵 ${dinero}", "#95D5B2"), (f"🪙 {fichas} fichas", self.COLOR_DORADO)]
        for texto, color in datos:
            tk.Label(barra, text=texto, font=("Segoe UI", 13, "bold"), bg=self.COLOR_PANEL, fg=color, padx=14, pady=12).pack(side="left")

    # ---------------- PANTALLAS ---------------- #

    def pantalla_registro(self):
        self.limpiar()
        tarjeta = self.crear_tarjeta(self.contenedor)
        tk.Label(tarjeta, text="♛", font=("Segoe UI", 54, "bold"), bg=self.COLOR_PANEL_2, fg=self.COLOR_DORADO).pack(pady=(58, 0))
        self.titulo_pantalla(tarjeta, "Bienvenido al casino", "Registra tu nombre para iniciar una experiencia de casino premium.")
        entrada_nombre = tk.Entry(tarjeta, font=("Segoe UI", 16), justify="center", width=32, relief="flat", bg="#EEF5F0", fg="#09110D")
        entrada_nombre.pack(pady=22, ipady=10)
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
        self.titulo_pantalla(tarjeta, "Menú principal", "Elige una mesa, convierte fichas o entra a la carrera.")
        grid = tk.Frame(tarjeta, bg=self.COLOR_PANEL_2)
        grid.pack(pady=8)
        opciones = [
            ("💱 Convertir dinero / fichas", "Gestiona tu saldo", self.pantalla_convertir),
            ("🂡 Jugar Blackjack", "Pide cartas y vence al crupier", lambda: self.pantalla_apuesta("blackjack")),
            ("♠ Jugar Poker", "Revela flop, turn y river", lambda: self.pantalla_apuesta("poker")),
            ("🏇 Carrera de caballos", "Apuesta por tu ganador", lambda: self.pantalla_apuesta("carrera")),
        ]
        for i, (titulo, desc, comando) in enumerate(opciones):
            card = tk.Frame(grid, bg=self.COLOR_PANEL_3, highlightthickness=1, highlightbackground="#2A6F59")
            card.grid(row=i // 2, column=i % 2, padx=14, pady=14, sticky="nsew")
            tk.Label(card, text=titulo, font=("Segoe UI", 15, "bold"), bg=self.COLOR_PANEL_3, fg=self.COLOR_DORADO).pack(padx=24, pady=(18, 4))
            tk.Label(card, text=desc, font=("Segoe UI", 10), bg=self.COLOR_PANEL_3, fg=self.COLOR_TEXTO_SUAVE).pack(pady=(0, 14))
            self.crear_boton(card, "Abrir", comando, 20).pack(pady=(0, 18))

    def pantalla_convertir(self):
        self.limpiar()
        self.panel_saldo(self.contenedor)
        tarjeta = self.crear_tarjeta(self.contenedor)
        self.titulo_pantalla(tarjeta, "Conversión de saldo", "Convierte tu dinero en fichas o tus fichas en dinero.")
        tk.Label(tarjeta, text="Cantidad", font=("Segoe UI", 13, "bold"), bg=self.COLOR_PANEL_2, fg=self.COLOR_TEXTO).pack()
        entrada = tk.Entry(tarjeta, font=("Segoe UI", 15), justify="center", width=22, relief="flat", bg="#EEF5F0")
        entrada.pack(pady=14, ipady=8)

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
        nombres = {"blackjack": "Blackjack", "poker": "Poker", "carrera": "Carrera de caballos"}
        tarjeta = self.crear_tarjeta(self.contenedor)
        self.titulo_pantalla(tarjeta, f"Apuesta para {nombres[tipo_juego]}", "Ingresa la cantidad de fichas que deseas apostar.")
        entrada = tk.Entry(tarjeta, font=("Segoe UI", 15), justify="center", width=22, relief="flat", bg="#EEF5F0")
        entrada.pack(pady=18, ipady=8)

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
        canvas = tk.Canvas(zona, width=1080, height=430, bg=self.COLOR_MESA, highlightthickness=0)
        canvas.pack(pady=15)
        mensaje = tk.Label(zona, text="Mesa abierta. Decide si pides carta o te plantas.", font=("Segoe UI", 13, "bold"), bg=self.COLOR_PANEL_2, fg=self.COLOR_DORADO)
        mensaje.pack(pady=8)
        controles = tk.Frame(zona, bg=self.COLOR_PANEL_2)
        controles.pack(pady=8)

        def redibujar(mostrar_crupier=True, animar=False):
            self.dibujar_mesa_premium(canvas, "BLACKJACK")
            canvas.create_text(130, 85, text="CRUPIER", fill="white", font=("Segoe UI", 15, "bold"))
            canvas.create_text(130, 260, text="JUGADOR", fill="white", font=("Segoe UI", 15, "bold"))
            for i, carta in enumerate(juego.mano_crupier):
                x, y = 95 + i * 88, 105
                if animar: self.animar_carta_desde_mazo(canvas, x, y, carta, oculta=(not mostrar_crupier and i == 1))
                self.dibujar_carta(canvas, x, y, carta, oculta=(not mostrar_crupier and i == 1))
            for i, carta in enumerate(juego.mano_jugador):
                x, y = 95 + i * 88, 285
                if animar: self.animar_carta_desde_mazo(canvas, x, y, carta)
                self.dibujar_carta(canvas, x, y, carta)
            total_j = juego.calcular_total(juego.mano_jugador)
            total_c = juego.calcular_total(juego.mano_crupier) if mostrar_crupier else "?"
            canvas.create_rectangle(790, 145, 1030, 255, fill="#092B22", outline=self.COLOR_DORADO, width=2)
            canvas.create_text(910, 175, text=f"Crupier: {total_c}", fill="white", font=("Segoe UI", 15, "bold"))
            canvas.create_text(910, 220, text=f"Jugador: {total_j}", fill=self.COLOR_DORADO, font=("Segoe UI", 15, "bold"))

        def finalizar(resultado: Resultado):
            jugador = self.casino.obtener_jugador()
            jugador.sumar_fichas(resultado.recompensa)
            mensaje.config(text=resultado.mensaje)
            for widget in controles.winfo_children(): widget.destroy()
            self.crear_boton(controles, "Volver al menú", self.pantalla_menu, 18).pack(side="left", padx=8)

        def pedir():
            juego.pedir_carta()
            redibujar(False, animar=True)
            if juego.calcular_total(juego.mano_jugador) > 21:
                resultado = juego.jugar(apuesta)
                redibujar(True)
                finalizar(resultado)

        def plantarse():
            juego.turno_crupier()
            redibujar(True, animar=True)
            resultado = juego.jugar(apuesta)
            finalizar(resultado)

        redibujar(False, animar=True)
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
        canvas = tk.Canvas(zona, width=1080, height=430, bg=self.COLOR_MESA, highlightthickness=0)
        canvas.pack(pady=15)
        mensaje = tk.Label(zona, text="Revela las cartas de la mesa.", font=("Segoe UI", 13, "bold"), bg=self.COLOR_PANEL_2, fg=self.COLOR_DORADO)
        mensaje.pack(pady=8)
        controles = tk.Frame(zona, bg=self.COLOR_PANEL_2)
        controles.pack(pady=8)

        def dibujar(mostrar_bot=False, animar=False):
            self.dibujar_mesa_premium(canvas, "POKER")
            canvas.create_text(120, 83, text="BOT", fill="white", font=("Segoe UI", 15, "bold"))
            canvas.create_text(540, 170, text="MESA", fill="white", font=("Segoe UI", 15, "bold"))
            canvas.create_text(120, 302, text="JUGADOR", fill="white", font=("Segoe UI", 15, "bold"))
            for i, carta in enumerate(juego.mano_oponente):
                x, y = 92 + i * 88, 105
                self.dibujar_carta(canvas, x, y, carta, oculta=not mostrar_bot)
            for i, carta in enumerate(juego.cartas_mesa):
                x, y = 330 + i * 88, 195
                if animar: self.animar_carta_desde_mazo(canvas, x, y, carta)
                self.dibujar_carta(canvas, x, y, carta)
            for i, carta in enumerate(juego.mano_jugador):
                self.dibujar_carta(canvas, 92 + i * 88, 322, carta)

        def limpiar_controles():
            for widget in controles.winfo_children(): widget.destroy()

        def hacer_flop():
            juego.flop(); mensaje.config(text="Flop revelado."); dibujar(animar=True)
        def hacer_turn():
            juego.turn(); mensaje.config(text="Turn revelado."); dibujar(animar=True)
        def hacer_river():
            juego.river(); dibujar(True, animar=True)
            resultado = juego.jugar(apuesta)
            jugador = self.casino.obtener_jugador(); jugador.sumar_fichas(resultado.recompensa)
            mensaje.config(text=resultado.mensaje)
            limpiar_controles(); self.crear_boton(controles, "Volver al menú", self.pantalla_menu, 18).pack(side="left", padx=8)

        dibujar()
        self.crear_boton(controles, "Flop", hacer_flop, 14).pack(side="left", padx=8)
        self.crear_boton(controles, "Turn", hacer_turn, 14).pack(side="left", padx=8)
        self.crear_boton(controles, "River", hacer_river, 14).pack(side="left", padx=8)
        self.crear_boton(controles, "Volver", self.pantalla_menu, 14).pack(side="left", padx=8)

    # ---------------- CARRERA ---------------- #

    def dibujar_caballo_silueta(self, canvas, x, y, fase=0, escala=0.62, color="#111111", tag=""):
        canvas.create_polygon(x+30*escala,y+45*escala,x+75*escala,y+20*escala,x+135*escala,y+32*escala,x+165*escala,y+55*escala,x+120*escala,y+70*escala,x+70*escala,y+70*escala,fill=color,smooth=True,tags=tag)
        canvas.create_polygon(x+125*escala,y+28*escala,x+160*escala,y-10*escala,x+190*escala,y+8*escala,x+165*escala,y+45*escala,fill=color,smooth=True,tags=tag)
        canvas.create_polygon(x+185*escala,y+2*escala,x+230*escala,y+10*escala,x+220*escala,y+30*escala,x+180*escala,y+22*escala,fill=color,smooth=True,tags=tag)
        canvas.create_polygon(x+190*escala,y-4*escala,x+198*escala,y-20*escala,x+205*escala,y-2*escala,fill=color,tags=tag)
        canvas.create_line(x+25*escala,y+48*escala,x-15*escala,y+15*escala,fill=color,width=max(3,int(10*escala)),smooth=True,tags=tag)
        patas = [(80,65,60,120),(105,65,120,122),(130,65,112,120),(150,60,168,118)] if fase % 2 == 0 else [(80,65,98,120),(105,65,90,122),(130,65,150,120),(150,60,132,118)]
        for x1,y1,x2,y2 in patas:
            canvas.create_line(x+x1*escala,y+y1*escala,x+x2*escala,y+y2*escala,fill=color,width=max(3,int(9*escala)),smooth=True,tags=tag)

    def pantalla_carrera(self, apuesta: Apuesta):
        self.limpiar(); self.panel_saldo(self.contenedor)
        juego: CarreraCaballo = self.casino.seleccionar_juego("carrera")
        zona = tk.Frame(self.contenedor, bg=self.COLOR_PANEL_2); zona.pack(fill="both", expand=True, padx=20, pady=10)
        canvas = tk.Canvas(zona, width=1080, height=445, bg="#123C52", highlightthickness=0); canvas.pack(pady=15)
        mensaje = tk.Label(zona, text="Selecciona el caballo por el que vas a apostar.", font=("Segoe UI", 13, "bold"), bg=self.COLOR_PANEL_2, fg=self.COLOR_DORADO); mensaje.pack(pady=8)
        controles = tk.Frame(zona, bg=self.COLOR_PANEL_2); controles.pack(pady=8)
        caballo_elegido = {"caballo": None}
        objetos = []

        def dibujar_pista(fase=0):
            canvas.delete("all"); objetos.clear()
            canvas.create_rectangle(0,0,1080,445,fill="#123C52",outline="")
            canvas.create_text(540, 32, text="GRAN CARRERA LA MALDAD", fill=self.COLOR_DORADO, font=("Segoe UI", 21, "bold"))
            meta_x = 900
            for y in range(70, 400, 22):
                color = "white" if (y // 22) % 2 == 0 else "black"
                canvas.create_rectangle(meta_x, y, meta_x + 34, y + 22, fill=color, outline=color)
            canvas.create_line(meta_x, 70, meta_x, 400, fill=self.COLOR_DORADO, width=3)
            colores = ["#111111", "#2B1608", "#071A2C"]
            for i, caballo in enumerate(juego.lista_caballos):
                y = 100 + i * 100
                canvas.create_rectangle(50, y + 78, 955, y + 83, fill="#E8D7A2", outline="")
                canvas.create_line(60, y + 84, 955, y + 84, fill="white", dash=(10, 10))
                tag = f"caballo_{i}"
                self.dibujar_caballo_silueta(canvas, 70 + caballo.posicion, y, fase, 0.62, colores[i], tag)
                canvas.create_text(88 + caballo.posicion, y + 88, text=caballo.nombre, fill="white", font=("Segoe UI", 11, "bold"), anchor="w", tags=tag)
                objetos.append((tag, caballo))

        def seleccionar(caballo: Caballo):
            caballo_elegido["caballo"] = caballo
            mensaje.config(text=f"Apostaste por {caballo.nombre}. Ahora inicia la carrera.")

        def limpiar_controles():
            for widget in controles.winfo_children(): widget.destroy()

        def correr():
            if caballo_elegido["caballo"] is None:
                mensaje.config(text="Primero debes seleccionar un caballo."); return
            limpiar_controles(); meta_x = 900; ganador = None; fase = 0
            for caballo in juego.lista_caballos: caballo.posicion = 0
            while ganador is None:
                fase += 1
                for caballo in juego.lista_caballos:
                    caballo.posicion += random.randint(6, 23)
                    if 70 + caballo.posicion + 145 >= meta_x:
                        ganador = caballo; break
                dibujar_pista(fase)
                canvas.update(); self.ventana.after(45)
            juego.caballo_ganador = ganador
            resultado = juego.jugar(apuesta, caballo_elegido["caballo"])
            jugador = self.casino.obtener_jugador(); jugador.sumar_fichas(resultado.recompensa)
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