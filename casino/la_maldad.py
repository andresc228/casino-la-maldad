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

casino = Casino()

ventana = tk.Tk()
ventana.title("Casino la maldad")
ventana.geometry("950x650")
ventana.configure(bg="#0b3d2e")

titulo = tk.Label(
    ventana,
    text="Casino la maldad",
    font=("Arial", 28, "bold"),
    bg="#0b3d2e",
    fg="gold"
)
titulo.pack(pady=10)

frame = tk.Frame(ventana, bg="#145a32")
frame.pack(fill="both", expand=True, padx=20, pady=20)


def limpiar():
    for w in frame.winfo_children():
        w.destroy()


def boton(txt, cmd, ancho=20):
    return tk.Button(
        frame,
        text=txt,
        command=cmd,
        font=("Arial", 12, "bold"),
        bg="#1abc9c",
        fg="black",
        activebackground="#16a085",
        width=ancho,
        pady=6,
        relief="raised",
        bd=3
    )


def dibujar_carta(canvas, x, y, carta, oculta=False, tag=None):
    tags = ()
    if tag:
        tags = (tag,)

    canvas.create_rectangle(x, y, x + 60, y + 90, fill="white", outline="black", width=2, tags=tags)

    if oculta:
        canvas.create_rectangle(x + 5, y + 5, x + 55, y + 85, fill="#2980b9", outline="#1f618d", tags=tags)
        canvas.create_text(x + 30, y + 45, text="?", font=("Arial", 18, "bold"), fill="white", tags=tags)
    else:
        canvas.create_text(
            x + 30,
            y + 45,
            text=texto_carta(carta),
            font=("Arial", 16, "bold"),
            fill=color_palo(carta),
            tags=tags
        )


# ---------------- PANTALLAS ---------------- #

def pantalla_registro():
    limpiar()
    tk.Label(frame, text="Ingrese su nombre", font=("Arial", 18), bg="#145a32", fg="white").pack(pady=20)
    entrada = tk.Entry(frame, font=("Arial", 14))
    entrada.pack()

    mensaje = tk.Label(frame, text="", bg="#145a32", fg="yellow", font=("Arial", 11))
    mensaje.pack(pady=10)

    def entrar():
        nombre = entrada.get().strip()
        if not nombre:
            mensaje.config(text="Debes ingresar un nombre")
            return
        registrar(nombre)

    boton("Entrar", entrar).pack(pady=20)


def registrar(nombre):
    casino.registrar_jugador(nombre)
    pantalla_menu()


def pantalla_menu():
    limpiar()
    j = casino.jugador
    d, f = j.consultar_saldo()

    tk.Label(frame, text=f"{j.nombre}", font=("Arial", 18, "bold"), bg="#145a32", fg="white").pack()
    tk.Label(frame, text=f"Dinero: {d}", font=("Arial", 13), bg="#145a32", fg="white").pack()
    tk.Label(frame, text=f"Fichas: {f}", font=("Arial", 13), bg="#145a32", fg="white").pack(pady=10)

    boton("Convertir", pantalla_convertir).pack(pady=5)
    boton("Blackjack", lambda: pantalla_juego("blackjack")).pack(pady=5)
    boton("Poker", lambda: pantalla_juego("poker")).pack(pady=5)
    boton("Carrera", lambda: pantalla_juego("carrera")).pack(pady=5)


# -------- CONVERTIR -------- #

def pantalla_convertir():
    limpiar()

    tk.Label(frame, text="¿Qué deseas hacer?", font=("Arial", 18), bg="#145a32", fg="white").pack(pady=10)
    mensaje = tk.Label(frame, text="", bg="#145a32", fg="yellow", font=("Arial", 11))
    mensaje.pack()

    def elegir(tipo):
        limpiar()
        tk.Label(frame, text="Cantidad:", font=("Arial", 14), bg="#145a32", fg="white").pack(pady=10)
        entrada = tk.Entry(frame, font=("Arial", 14))
        entrada.pack()

        aviso = tk.Label(frame, text="", bg="#145a32", fg="yellow", font=("Arial", 11))
        aviso.pack(pady=10)

        def hacer():
            try:
                cantidad = int(entrada.get())
            except ValueError:
                aviso.config(text="Ingrese un número válido")
                return

            ok = casino.jugador.convertir(tipo, cantidad)
            if not ok:
                aviso.config(text="Cantidad inválida o saldo insuficiente")
                return

            pantalla_menu()

        boton("Confirmar", hacer).pack(pady=10)
        boton("Volver", pantalla_menu).pack()

    boton("Dinero → Fichas", lambda: elegir("dinero_a_fichas")).pack(pady=5)
    boton("Fichas → Dinero", lambda: elegir("fichas_a_dinero")).pack(pady=5)
    boton("Volver", pantalla_menu).pack(pady=10)


# ---------------- JUEGOS ---------------- #

def pantalla_juego(tipo):
    limpiar()

    j = casino.jugador

    tk.Label(frame, text="Ingrese apuesta (FICHAS)", font=("Arial", 14), bg="#145a32", fg="white").pack()
    entrada = tk.Entry(frame, font=("Arial", 14))
    entrada.pack(pady=5)

    canvas = tk.Canvas(frame, width=860, height=320, bg="darkgreen", highlightthickness=0)
    canvas.pack(pady=10)

    resultado_label = tk.Label(frame, text="", bg="#145a32", fg="white", font=("Arial", 12, "bold"))
    resultado_label.pack(pady=5)

    controles = tk.Frame(frame, bg="#145a32")
    controles.pack(pady=5)

    def limpiar_controles():
        for w in controles.winfo_children():
            w.destroy()

    def boton_control(txt, cmd, ancho=16):
        return tk.Button(
            controles,
            text=txt,
            command=cmd,
            font=("Arial", 11, "bold"),
            bg="#f4d03f",
            fg="black",
            activebackground="#d4ac0d",
            width=ancho,
            pady=5,
            relief="raised",
            bd=3
        )

    def volver_unico():
        limpiar_controles()
        boton_control("Volver al menú", pantalla_menu, 18).pack(pady=5)

    def iniciar():
        if not entrada.get():
            resultado_label.config(text="Ingresa una apuesta")
            return

        try:
            monto = int(entrada.get())
        except ValueError:
            resultado_label.config(text="La apuesta debe ser un número")
            return

        if monto <= 0:
            resultado_label.config(text="La apuesta debe ser mayor que 0")
            return

        if monto > j.saldoFichas:
            resultado_label.config(text="No tienes fichas suficientes")
            return

        entrada.config(state="disabled")

        apuesta = Apuesta(monto, tipo)
        juego = casino.seleccionar_juego(tipo)

        limpiar_controles()

        # -------- BLACKJACK -------- #
        if tipo == "blackjack":
            juego.manoJugador = []
            juego.manoCrupier = []

            tk.Label

            def redibujar():
                canvas.delete("all")
                canvas.create_text(130, 20, text="Crupier", fill="white", font=("Arial", 14, "bold"))
                canvas.create_text(130, 180, text="Jugador", fill="white", font=("Arial", 14, "bold"))

                for i, carta in enumerate(juego.manoCrupier):
                    dibujar_carta(canvas, 80 + i * 75, 40, carta)

                for i, carta in enumerate(juego.manoJugador):
                    dibujar_carta(canvas, 80 + i * 75, 200, carta)

                total_j = calcular_total_blackjack(juego.manoJugador)
                total_c = calcular_total_blackjack(juego.manoCrupier)

                canvas.create_text(700, 235, text=f"Total jugador: {total_j}", fill="white", font=("Arial", 12, "bold"))
                canvas.create_text(700, 75, text=f"Total crupier: {total_c}", fill="white", font=("Arial", 12, "bold"))

            def pedir():
                carta = crear_carta()
                juego.manoJugador.append(carta)
                redibujar()

                total_j = calcular_total_blackjack(juego.manoJugador)
                if total_j > 21:
                    r = juego.jugar(apuesta)
                    j.actualizar_saldo(r, monto)
                    resultado_label.config(text="Perdiste. Te pasaste de 21.")
                    volver_unico()

            def plantarse():
                while calcular_total_blackjack(juego.manoCrupier) < 17:
                    juego.manoCrupier.append(crear_carta())

                redibujar()

                r = juego.jugar(apuesta)
                j.actualizar_saldo(r, monto)

                total_j = calcular_total_blackjack(juego.manoJugador)
                total_c = calcular_total_blackjack(juego.manoCrupier)

                if r.gano:
                    resultado_label.config(text=f"Ganaste. Tu total: {total_j} | Crupier: {total_c}")
                else:
                    resultado_label.config(text=f"Perdiste. Tu total: {total_j} | Crupier: {total_c}")

                volver_unico()

            # cartas iniciales
            juego.manoJugador.append(crear_carta())
            juego.manoJugador.append(crear_carta())
            juego.manoCrupier.append(crear_carta())
            juego.manoCrupier.append(crear_carta())

            redibujar()

            boton_control("Pedir carta", pedir).pack(side="left", padx=5)
            boton_control("Plantarse", plantarse).pack(side="left", padx=5)
            boton_control("Volver al menú", pantalla_menu, 18).pack(side="left", padx=5)

        # -------- POKER -------- #
        elif tipo == "poker":
            mano_j = [crear_carta() for _ in range(2)]
            mano_bot = [crear_carta() for _ in range(2)]
            mesa = []

            def dibujar_mesa(mostrar_bot=False):
                canvas.delete("all")

                canvas.create_text(120, 20, text="Bot", fill="white", font=("Arial", 14, "bold"))
                canvas.create_text(120, 280, text="Jugador", fill="white", font=("Arial", 14, "bold"))
                canvas.create_text(430, 120, text="Mesa", fill="white", font=("Arial", 14, "bold"))

                for i, carta in enumerate(mano_bot):
                    dibujar_carta(canvas, 80 + i * 75, 40, carta, oculta=not mostrar_bot)

                for i, carta in enumerate(mesa):
                    dibujar_carta(canvas, 280 + i * 75, 140, carta)

                for i, carta in enumerate(mano_j):
                    dibujar_carta(canvas, 80 + i * 75, 200, carta)

            def flop():
                if len(mesa) == 0:
                    for _ in range(3):
                        mesa.append(crear_carta())
                    dibujar_mesa()

            def turn():
                if len(mesa) == 3:
                    mesa.append(crear_carta())
                    dibujar_mesa()

            def river():
                if len(mesa) == 4:
                    mesa.append(crear_carta())

                    juego.manoJugador = mano_j + mesa
                    juego.manoOponente = mano_bot + mesa

                    r = juego.jugar(apuesta)
                    j.actualizar_saldo(r, monto)

                    dibujar_mesa(mostrar_bot=True)

                    total_jugador = sum(valor_poker(carta) for carta in juego.manoJugador)
                    total_bot = sum(valor_poker(carta) for carta in juego.manoOponente)

                    if r.gano:
                        resultado_label.config(
                            text=f"Ganaste. Total jugador: {total_jugador} | Total bot: {total_bot}"
                        )
                    else:
                        resultado_label.config(
                            text=f"Perdiste. Total jugador: {total_jugador} | Total bot: {total_bot}"
                        )

                    limpiar_controles()
                    boton_control("Volver al menú", pantalla_menu, 18).pack(pady=5)

            dibujar_mesa()

            boton_control("Flop", flop).pack(side="left", padx=5)
            boton_control("Turn", turn).pack(side="left", padx=5)
            boton_control("River", river).pack(side="left", padx=5)
            boton_control("Volver al menú", pantalla_menu, 18).pack(side="left", padx=5)

        # -------- CARRERA -------- #
        elif tipo == "carrera":
            canvas.delete("all")

            meta_x = 760
            canvas.create_line(meta_x, 20, meta_x, 300, fill="white", width=4)

            for y in range(20, 300, 20):
                color = "white" if (y // 20) % 2 == 0 else "black"
                canvas.create_rectangle(meta_x, y, meta_x + 25, y + 20, fill=color, outline=color)

            caballos = []
            textos = []
            pos = [0, 0, 0]
            nombres = ["Caballo 1", "Caballo 2", "Caballo 3"]

            for i in range(3):
                y1 = 50 + i * 80
                y2 = 95 + i * 80
                rect = canvas.create_rectangle(20, y1, 150, y2, fill="#8B4513", outline="black", width=2)
                texto = canvas.create_text(85, (y1 + y2) / 2, text=nombres[i], fill="white", font=("Arial", 11, "bold"))
                caballos.append(rect)
                textos.append(texto)

            seleccion = tk.IntVar(value=-1)

            def seleccionar_caballo(i):
                seleccion.set(i)
                resultado_label.config(text=f"Apostaste por {nombres[i]}")

            for i in range(3):
                boton_control(f"Apostar {nombres[i]}", lambda i=i: seleccionar_caballo(i), 15).pack(side="left", padx=4)

            def correr():
                if seleccion.get() == -1:
                    resultado_label.config(text="Debes elegir un caballo")
                    return

                ganador = None

                while ganador is None:
                    for i in range(3):
                        m = random.randint(5, 20)
                        canvas.move(caballos[i], m, 0)
                        canvas.move(textos[i], m, 0)
                        pos[i] += m

                        coords = canvas.coords(caballos[i])
                        if coords[2] >= meta_x:
                            ganador = i
                            break

                    ventana.update()
                    ventana.after(50)

                juego.caballoGanador = "jugador" if ganador == seleccion.get() else "otro"

                r = juego.jugar(apuesta)
                j.actualizar_saldo(r, monto)

                if r.gano:
                    resultado_label.config(text=f"Ganaste. Llegó primero {nombres[ganador]}")
                else:
                    resultado_label.config(text=f"Perdiste. Llegó primero {nombres[ganador]}")

                limpiar_controles()
                boton_control("Volver al menú", pantalla_menu, 18).pack(pady=5)

            boton_control("Iniciar carrera", correr, 15).pack(side="left", padx=4)
            boton_control("Volver al menú", pantalla_menu, 18).pack(side="left", padx=4)

    boton("Apostar", iniciar).pack(pady=8)



pantalla_registro()
ventana.mainloop()