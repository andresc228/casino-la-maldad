import random
import tkinter as tk
from tkinter import messagebox
from typing import Optional
from .dominio import Apuesta, Caballo, Carta, Casino, Resultado
from .excepciones import CantidadInvalidaError, CasinoError
from .juegos import Blackjack, CarreraCaballo, Poker

class CasinoApp:
    COLOR_FONDO = "#03080D"; COLOR_PANEL = "#0A171B"; COLOR_PANEL_2 = "#0E2226"; COLOR_PANEL_3 = "#123239"
    COLOR_MESA = "#07563B"; COLOR_MESA_OSCURO = "#043326"; COLOR_DORADO = "#F6C453"; COLOR_DORADO_2 = "#C89325"
    COLOR_TEXTO = "#F8F9FA"; COLOR_TEXTO_SUAVE = "#B7E4C7"; COLOR_TEXTO_APAGADO = "#7CA394"
    COLOR_BOTON = "#1B6B4A"; COLOR_BOTON_HOVER = "#2EA66F"; COLOR_ERROR = "#FFDD57"; COLOR_ROJO = "#C1121F"

    def __init__(self):
        self.casino = Casino(); self.particulas = []
        self.ventana = tk.Tk(); self.ventana.title("Casino La Maldad | Premium Edition")
        ancho = max(980, min(1240, self.ventana.winfo_screenwidth() - 80)); alto = max(660, min(800, self.ventana.winfo_screenheight() - 90))
        self.ventana.geometry(f"{ancho}x{alto}"); self.ventana.minsize(860, 600); self.ventana.configure(bg=self.COLOR_FONDO)
        self.frame_principal = tk.Frame(self.ventana, bg=self.COLOR_FONDO); self.frame_principal.pack(fill="both", expand=True)
        self.fondo_animado = tk.Canvas(self.frame_principal, bg=self.COLOR_FONDO, highlightthickness=0); self.fondo_animado.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.fondo_animado.bind("<Configure>", lambda _e: self.crear_fondo_premium())
        self.crear_fondo_premium(); self.animar_particulas()
        self.capa_ui = tk.Frame(self.frame_principal, bg=self.COLOR_FONDO); self.capa_ui.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.crear_encabezado()
        self.contenedor = tk.Frame(self.capa_ui, bg=self.COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground="#21453D", highlightcolor=self.COLOR_DORADO)
        self.contenedor.pack(fill="both", expand=True, padx=18, pady=(12, 18)); self.pantalla_registro()

    def crear_fondo_premium(self):
        if not hasattr(self, "fondo_animado"): return
        self.fondo_animado.delete("all"); self.particulas.clear()
        w = max(self.fondo_animado.winfo_width(), self.ventana.winfo_width(), 900); h = max(self.fondo_animado.winfo_height(), self.ventana.winfo_height(), 650)
        for i in range(0, h + 20, 6):
            color = f"#{3+min(12,i//80):02x}{8+min(25,i//35):02x}{13+min(30,i//45):02x}"
            self.fondo_animado.create_rectangle(0, i, w, i + 6, fill=color, outline="")
        self.fondo_animado.create_oval(-160, 80, int(w * 0.35), int(h * 0.80), fill="#062318", outline="")
        self.fondo_animado.create_oval(int(w * 0.65), -190, w + 180, int(h * 0.55), fill="#151006", outline="")
        self.fondo_animado.create_text(int(w * 0.77), int(h * 0.82), text="♠   ♥   ♦   ♣", font=("Segoe UI", max(32, int(w * 0.045)), "bold"), fill="#071C1C")
        for _ in range(70):
            x = random.randint(0, w); y = random.randint(0, h); size = random.choice([1,1,2,2,3]); vel = random.choice([0.12,0.18,0.25,0.32,0.45])
            item = self.fondo_animado.create_oval(x, y, x + size, y + size, fill=random.choice([self.COLOR_DORADO,"#63E6BE","#E9C46A"]), outline="")
            self.particulas.append([item, vel])

    def animar_particulas(self):
        h = max(self.fondo_animado.winfo_height(), 650)
        for item, vel in self.particulas:
            self.fondo_animado.move(item, 0, vel); coords = self.fondo_animado.coords(item)
            if coords and coords[1] > h: self.fondo_animado.move(item, 0, -h - 20)
        self.ventana.after(45, self.animar_particulas)

    def crear_encabezado(self):
        encabezado = tk.Frame(self.capa_ui, bg=self.COLOR_FONDO); encabezado.pack(fill="x", padx=18, pady=(12, 0))
        izquierda = tk.Frame(encabezado, bg=self.COLOR_FONDO); izquierda.pack(side="left", fill="x", expand=True)
        tk.Label(izquierda, text="♛ CASINO LA MALDAD", font=("Segoe UI", 24, "bold"), bg=self.COLOR_FONDO, fg=self.COLOR_DORADO).pack(anchor="w")
        tk.Label(izquierda, text="Blackjack · Poker · Carrera de caballos · Experiencia premium", font=("Segoe UI", 10), bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO_SUAVE).pack(anchor="w", pady=(0,4))
        derecha = tk.Frame(encabezado, bg=self.COLOR_FONDO); derecha.pack(side="right")
        tk.Label(derecha, text="● MESAS ABIERTAS", font=("Segoe UI", 9, "bold"), bg="#112D25", fg="#63E6BE", padx=12, pady=7).pack(side="right", padx=(8,0))

    def limpiar(self):
        for widget in self.contenedor.winfo_children(): widget.destroy()
    def crear_boton(self, padre, texto, comando, ancho=18, color=None):
        color_base = color or self.COLOR_BOTON; color_hover = self.COLOR_DORADO_2 if color == self.COLOR_DORADO else self.COLOR_BOTON_HOVER
        boton = tk.Button(padre, text=texto, command=comando, font=("Segoe UI",10,"bold"), bg=color_base, fg="#07110D" if color == self.COLOR_DORADO else "white", activebackground=color_hover, activeforeground="white", width=ancho, pady=8, relief="flat", cursor="hand2", bd=0)
        boton.bind("<Enter>", lambda _e: boton.config(bg=color_hover)); boton.bind("<Leave>", lambda _e: boton.config(bg=color_base)); return boton
    def crear_entrada(self, padre, ancho=24):
        cont = tk.Frame(padre, bg="#D9B650"); entrada = tk.Entry(cont, font=("Segoe UI",13), justify="center", width=ancho, relief="flat", bg="#EEF5F0", fg="#09110D", insertbackground="#09110D")
        entrada.pack(padx=2, pady=2, ipady=7); return cont, entrada
    def crear_tarjeta(self, padre, relleno=True):
        exterior = tk.Frame(padre, bg="#020404"); exterior.pack(pady=12, padx=16, fill="both", expand=relleno)
        tarjeta = tk.Frame(exterior, bg=self.COLOR_PANEL_2, bd=0, highlightthickness=1, highlightbackground="#2A6F59"); tarjeta.pack(padx=2, pady=2, fill="both", expand=True); return tarjeta
    def titulo_pantalla(self, padre, titulo, subtitulo=""):
        tk.Label(padre, text=titulo, font=("Segoe UI",22,"bold"), bg=self.COLOR_PANEL_2, fg=self.COLOR_DORADO).pack(pady=(20,6))
        if subtitulo: tk.Label(padre, text=subtitulo, font=("Segoe UI",10), bg=self.COLOR_PANEL_2, fg=self.COLOR_TEXTO_SUAVE, wraplength=760).pack(pady=(0,12))
    def mostrar_error(self, mensaje): messagebox.showerror("Casino La Maldad", mensaje)
    def mostrar_info(self, mensaje): messagebox.showinfo("Casino La Maldad", mensaje)
    def obtener_entero(self, entrada):
        try: return int(entrada.get())
        except ValueError: raise CantidadInvalidaError("Debes ingresar un número entero válido.")
    def color_palo(self, carta): return self.COLOR_ROJO if carta.palo in ["♥","♦"] else "#111111"
    def panel_saldo(self, padre):
        jugador = self.casino.obtener_jugador(); dinero, fichas = jugador.consultar_saldo(); barra = tk.Frame(padre, bg=self.COLOR_PANEL, height=52); barra.pack(fill="x", pady=(0,6))
        for texto, color in [(f"👤  {jugador.nombre}", self.COLOR_TEXTO), (f"💵  ${dinero:,}".replace(",","."), "#95D5B2"), (f"🪙  {fichas:,} fichas".replace(",","."), self.COLOR_DORADO)]:
            caja = tk.Frame(barra, bg="#0F2528", highlightthickness=1, highlightbackground="#1F4A42"); caja.pack(side="left", padx=6, pady=6)
            tk.Label(caja, text=texto, font=("Segoe UI",10,"bold"), bg="#0F2528", fg=color, padx=12, pady=7).pack()

    def dibujar_carta(self, canvas, x, y, carta, oculta=False, escala=1.0):
        w,h = int(70*escala), int(103*escala); canvas.create_rectangle(x+6,y+8,x+w+6,y+h+8, fill="#000000", outline=""); canvas.create_rectangle(x,y,x+w,y+h, fill="#FFFDF7", outline=self.COLOR_DORADO, width=2)
        canvas.create_rectangle(x+5,y+5,x+w-5,y+h-5, outline="#D9B650", width=1)
        if oculta: canvas.create_rectangle(x+9,y+9,x+w-9,y+h-9, fill="#0A2342", outline="#2D6A9F", width=2); canvas.create_text(x+w/2,y+h/2,text="♛",font=("Segoe UI",int(24*escala),"bold"),fill=self.COLOR_DORADO); return
        if carta is None: return
        color = self.color_palo(carta); canvas.create_text(x+15,y+17,text=carta.valor,font=("Segoe UI",int(11*escala),"bold"),fill=color); canvas.create_text(x+15,y+34,text=carta.palo,font=("Segoe UI",int(12*escala),"bold"),fill=color); canvas.create_text(x+w/2,y+h/2+4,text=carta.palo,font=("Segoe UI",int(30*escala),"bold"),fill=color)
    def dibujar_mesa_premium(self, canvas, titulo):
        canvas.delete("all"); w=max(canvas.winfo_width(),900); h=max(canvas.winfo_height(),360); canvas.create_rectangle(0,0,w,h,fill=self.COLOR_MESA_OSCURO,outline="")
        for i in range(30): canvas.create_oval(60-i*7,10-i*3,w-60+i*7,h+i*4,outline="#086344" if i%2==0 else "#07563B",width=2)
        canvas.create_oval(45,22,w-45,h-22,outline=self.COLOR_DORADO,width=4); canvas.create_oval(78,50,w-78,h-50,outline="#3EA875",width=2); canvas.create_text(w//2,35,text=titulo,fill=self.COLOR_DORADO,font=("Segoe UI",17,"bold")); canvas.create_text(w//2,h//2,text="LA MALDAD",fill="#0A6A49",font=("Segoe UI",max(26,int(w*0.04)),"bold"))

    def pantalla_registro(self):
        self.limpiar(); tarjeta = self.crear_tarjeta(self.contenedor); tk.Label(tarjeta,text="♛",font=("Segoe UI",48,"bold"),bg=self.COLOR_PANEL_2,fg=self.COLOR_DORADO).pack(pady=(35,0)); self.titulo_pantalla(tarjeta,"Bienvenido al casino","Registra tu nombre para entrar a una experiencia visual premium.")
        cont, entrada = self.crear_entrada(tarjeta,30); cont.pack(pady=16); entrada.focus()
        def registrar():
            try: self.casino.registrar_jugador(entrada.get()); self.pantalla_menu()
            except CasinoError as error: self.mostrar_error(str(error))
        entrada.bind("<Return>", lambda _e: registrar()); self.crear_boton(tarjeta,"Entrar al casino",registrar,22,self.COLOR_DORADO).pack(pady=8)
    def pantalla_menu(self):
        self.limpiar(); self.panel_saldo(self.contenedor); tarjeta = self.crear_tarjeta(self.contenedor); self.titulo_pantalla(tarjeta,"Menú principal","Elige una mesa, convierte fichas o entra a la carrera.")
        grid = tk.Frame(tarjeta,bg=self.COLOR_PANEL_2); grid.pack(pady=6,fill="both",expand=True); [grid.columnconfigure(c,weight=1) for c in range(2)]; [grid.rowconfigure(r,weight=1) for r in range(2)]
        opciones=[("💱","Convertir saldo","Dinero ↔ fichas",self.pantalla_convertir),("🂡","Blackjack","Pide cartas y vence al crupier",lambda:self.pantalla_apuesta("blackjack")),("♠","Poker","Flop · Turn · River",lambda:self.pantalla_apuesta("poker")),("●","Carrera de caballos","Apuesta por tu ganador",lambda:self.pantalla_apuesta("carrera"))]
        for i,(icono,titulo,desc,comando) in enumerate(opciones):
            card=tk.Frame(grid,bg=self.COLOR_PANEL_3,highlightthickness=1,highlightbackground="#2A6F59"); card.grid(row=i//2,column=i%2,padx=10,pady=10,sticky="nsew")
            tk.Label(card,text=icono,font=("Segoe UI",25,"bold"),bg=self.COLOR_PANEL_3,fg=self.COLOR_DORADO).pack(pady=(12,0)); tk.Label(card,text=titulo,font=("Segoe UI",13,"bold"),bg=self.COLOR_PANEL_3,fg=self.COLOR_DORADO).pack(padx=16,pady=(2,3)); tk.Label(card,text=desc,font=("Segoe UI",9),bg=self.COLOR_PANEL_3,fg=self.COLOR_TEXTO_SUAVE).pack(pady=(0,8)); self.crear_boton(card,"Abrir mesa",comando,16).pack(pady=(0,12))
    def pantalla_convertir(self):
        self.limpiar(); self.panel_saldo(self.contenedor); tarjeta=self.crear_tarjeta(self.contenedor); self.titulo_pantalla(tarjeta,"Conversión de saldo","Convierte tu dinero en fichas o tus fichas en dinero."); cont,entrada=self.crear_entrada(tarjeta,22); cont.pack(pady=14)
        def convertir(tipo):
            try: cantidad=self.obtener_entero(entrada); self.casino.obtener_jugador().convertir(tipo,cantidad); self.mostrar_info("Conversión realizada correctamente."); self.pantalla_menu()
            except CasinoError as error: self.mostrar_error(str(error))
        botones=tk.Frame(tarjeta,bg=self.COLOR_PANEL_2); botones.pack(pady=14); self.crear_boton(botones,"Dinero → Fichas",lambda:convertir("dinero_a_fichas"),18).grid(row=0,column=0,padx=8); self.crear_boton(botones,"Fichas → Dinero",lambda:convertir("fichas_a_dinero"),18).grid(row=0,column=1,padx=8); self.crear_boton(tarjeta,"Volver",self.pantalla_menu,16).pack(pady=12)
    def pantalla_apuesta(self,tipo_juego):
        self.limpiar(); self.panel_saldo(self.contenedor); nombres={"blackjack":"Blackjack","poker":"Poker","carrera":"Carrera de caballos"}; tarjeta=self.crear_tarjeta(self.contenedor); self.titulo_pantalla(tarjeta,f"Apuesta para {nombres[tipo_juego]}","Ingresa la cantidad de fichas que deseas apostar."); cont,entrada=self.crear_entrada(tarjeta,22); cont.pack(pady=16)
        def iniciar():
            try:
                monto=self.obtener_entero(entrada); apuesta=Apuesta(monto,tipo_juego); apuesta.validar(); self.casino.obtener_jugador().descontar_apuesta(monto)
                {"blackjack":self.pantalla_blackjack,"poker":self.pantalla_poker,"carrera":self.pantalla_carrera}[tipo_juego](apuesta)
            except CasinoError as error: self.mostrar_error(str(error))
        entrada.bind("<Return>",lambda _e:iniciar()); self.crear_boton(tarjeta,"Iniciar juego",iniciar,18,self.COLOR_DORADO).pack(pady=7); self.crear_boton(tarjeta,"Volver",self.pantalla_menu,16).pack(pady=7)

    def pantalla_blackjack(self, apuesta):
        self.limpiar(); self.panel_saldo(self.contenedor); juego=self.casino.seleccionar_juego("blackjack"); juego.iniciar(); zona=tk.Frame(self.contenedor,bg=self.COLOR_PANEL_2); zona.pack(fill="both",expand=True,padx=12,pady=8); canvas=tk.Canvas(zona,bg=self.COLOR_MESA,highlightthickness=0); canvas.pack(fill="both",expand=True,pady=8); mensaje=tk.Label(zona,text="Mesa abierta. Decide si pides carta o te plantas.",font=("Segoe UI",11,"bold"),bg=self.COLOR_PANEL_2,fg=self.COLOR_DORADO); mensaje.pack(pady=5); controles=tk.Frame(zona,bg=self.COLOR_PANEL_2); controles.pack(pady=6)
        def redibujar(mostrar_crupier=True):
            self.dibujar_mesa_premium(canvas,"BLACKJACK"); w=max(canvas.winfo_width(),900); h=max(canvas.winfo_height(),360); escala=max(0.72,min(1.0,w/1100)); canvas.create_text(105,76,text="CRUPIER",fill="white",font=("Segoe UI",13,"bold")); canvas.create_text(105,h-150,text="JUGADOR",fill="white",font=("Segoe UI",13,"bold"))
            for i,carta in enumerate(juego.mano_crupier): self.dibujar_carta(canvas,85+i*int(80*escala),92,carta,oculta=(not mostrar_crupier and i==1),escala=escala)
            for i,carta in enumerate(juego.mano_jugador): self.dibujar_carta(canvas,85+i*int(80*escala),h-128,carta,escala=escala)
            total_j=juego.calcular_total(juego.mano_jugador); total_c=juego.calcular_total(juego.mano_crupier) if mostrar_crupier else "?"; panel_x=int(w*0.72); canvas.create_rectangle(panel_x,115,w-45,245,fill="#092B22",outline=self.COLOR_DORADO,width=2); canvas.create_text((panel_x+w-45)//2,145,text="MARCADOR",fill=self.COLOR_TEXTO_SUAVE,font=("Segoe UI",10,"bold")); canvas.create_text((panel_x+w-45)//2,178,text=f"Crupier: {total_c}",fill="white",font=("Segoe UI",14,"bold")); canvas.create_text((panel_x+w-45)//2,210,text=f"Jugador: {total_j}",fill=self.COLOR_DORADO,font=("Segoe UI",14,"bold"))
        canvas.bind("<Configure>",lambda _e:redibujar(False))
        def finalizar(resultado):
            self.casino.obtener_jugador().sumar_fichas(resultado.recompensa); mensaje.config(text=resultado.mensaje,fg="#95D5B2" if resultado.gano else self.COLOR_ERROR); [w.destroy() for w in controles.winfo_children()]; self.crear_boton(controles,"Volver al menú",self.pantalla_menu,16).pack(side="left",padx=6)
        def pedir():
            juego.pedir_carta(); redibujar(False)
            if juego.calcular_total(juego.mano_jugador)>21: resultado=juego.jugar(apuesta); redibujar(True); finalizar(resultado)
        def plantarse(): juego.turno_crupier(); redibujar(True); finalizar(juego.jugar(apuesta))
        redibujar(False); self.crear_boton(controles,"Pedir carta",pedir,14).pack(side="left",padx=6); self.crear_boton(controles,"Plantarse",plantarse,14).pack(side="left",padx=6); self.crear_boton(controles,"Rendirse",self.pantalla_menu,14).pack(side="left",padx=6)

    def pantalla_poker(self, apuesta):
        self.limpiar(); self.panel_saldo(self.contenedor); juego=self.casino.seleccionar_juego("poker"); juego.iniciar(); zona=tk.Frame(self.contenedor,bg=self.COLOR_PANEL_2); zona.pack(fill="both",expand=True,padx=12,pady=8); canvas=tk.Canvas(zona,bg=self.COLOR_MESA,highlightthickness=0); canvas.pack(fill="both",expand=True,pady=8); mensaje=tk.Label(zona,text="Revela las cartas de la mesa en orden.",font=("Segoe UI",11,"bold"),bg=self.COLOR_PANEL_2,fg=self.COLOR_DORADO); mensaje.pack(pady=5); controles=tk.Frame(zona,bg=self.COLOR_PANEL_2); controles.pack(pady=6)
        def dibujar(mostrar_bot=False):
            self.dibujar_mesa_premium(canvas,"POKER"); w=max(canvas.winfo_width(),900); h=max(canvas.winfo_height(),360); escala=max(0.70,min(1.0,w/1100)); canvas.create_text(100,72,text="BOT",fill="white",font=("Segoe UI",13,"bold")); canvas.create_text(w//2,int(h*0.35),text="CARTAS DE MESA",fill="white",font=("Segoe UI",13,"bold")); canvas.create_text(100,h-140,text="JUGADOR",fill="white",font=("Segoe UI",13,"bold"))
            for i,carta in enumerate(juego.mano_oponente): self.dibujar_carta(canvas,88+i*int(80*escala),92,carta,oculta=not mostrar_bot,escala=escala)
            start_x=max(250,w//2-int(len(juego.cartas_mesa)*40*escala))
            for i,carta in enumerate(juego.cartas_mesa): self.dibujar_carta(canvas,start_x+i*int(80*escala),int(h*0.42),carta,escala=escala)
            for i,carta in enumerate(juego.mano_jugador): self.dibujar_carta(canvas,88+i*int(80*escala),h-120,carta,escala=escala)
        canvas.bind("<Configure>",lambda _e:dibujar(False))
        def limpiar_controles(): [w.destroy() for w in controles.winfo_children()]
        def hacer_flop(): juego.flop(); mensaje.config(text="Flop revelado. Sigue con el turn."); dibujar()
        def hacer_turn(): juego.turn(); mensaje.config(text="Turn revelado. Falta el river."); dibujar()
        def hacer_river(): juego.river(); dibujar(True); resultado=juego.jugar(apuesta); self.casino.obtener_jugador().sumar_fichas(resultado.recompensa); mensaje.config(text=resultado.mensaje,fg="#95D5B2" if resultado.gano else self.COLOR_ERROR); limpiar_controles(); self.crear_boton(controles,"Volver al menú",self.pantalla_menu,16).pack(side="left",padx=6)
        dibujar(); self.crear_boton(controles,"Flop",hacer_flop,12).pack(side="left",padx=6); self.crear_boton(controles,"Turn",hacer_turn,12).pack(side="left",padx=6); self.crear_boton(controles,"River",hacer_river,12).pack(side="left",padx=6); self.crear_boton(controles,"Volver",self.pantalla_menu,12).pack(side="left",padx=6)

    def dibujar_corredor(self, canvas, x, y, nombre, color, elegido=False):
        radio=16; canvas.create_oval(x-radio,y-radio,x+radio,y+radio,fill=color,outline=self.COLOR_DORADO if elegido else "#E8F1F2",width=3); canvas.create_oval(x-5,y-5,x+5,y+5,fill="#FFFFFF",outline="")
        if elegido: canvas.create_text(x,y-30,text="★ TU APUESTA",fill=self.COLOR_DORADO,font=("Segoe UI",9,"bold"))
        canvas.create_text(x,y+31,text=nombre,fill="white",font=("Segoe UI",9,"bold"))
    def pantalla_carrera(self, apuesta):
        self.limpiar(); self.panel_saldo(self.contenedor); juego=self.casino.seleccionar_juego("carrera"); zona=tk.Frame(self.contenedor,bg=self.COLOR_PANEL_2); zona.pack(fill="both",expand=True,padx=12,pady=8); canvas=tk.Canvas(zona,bg="#123C52",highlightthickness=0); canvas.pack(fill="both",expand=True,pady=8); mensaje=tk.Label(zona,text="Selecciona el corredor por el que vas a apostar.",font=("Segoe UI",11,"bold"),bg=self.COLOR_PANEL_2,fg=self.COLOR_DORADO); mensaje.pack(pady=5); controles=tk.Frame(zona,bg=self.COLOR_PANEL_2); controles.pack(pady=6); caballo_elegido={"caballo":None}
        def dibujar_pista():
            canvas.delete("all"); w=max(canvas.winfo_width(),820); h=max(canvas.winfo_height(),330); margen_izq=90; margen_der=70; meta_x=w-margen_der; pista_ancho=meta_x-margen_izq; canvas.create_rectangle(0,0,w,h,fill="#123C52",outline=""); canvas.create_rectangle(0,0,w,62,fill="#0B2536",outline=""); canvas.create_text(w//2,26,text="GRAN CARRERA LA MALDAD",fill=self.COLOR_DORADO,font=("Segoe UI",18,"bold")); canvas.create_text(w//2,50,text=f"Apuesta activa: {apuesta.monto} fichas",fill=self.COLOR_TEXTO_SUAVE,font=("Segoe UI",9,"bold"))
            meta_y_inicio=82; meta_y_fin=h-35
            for y in range(meta_y_inicio,meta_y_fin,20): canvas.create_rectangle(meta_x,y,meta_x+24,y+20,fill="white" if (y//20)%2==0 else "black",outline="")
            canvas.create_line(meta_x,meta_y_inicio,meta_x,meta_y_fin,fill=self.COLOR_DORADO,width=3); canvas.create_text(meta_x+38,meta_y_inicio+10,text="META",fill=self.COLOR_DORADO,font=("Segoe UI",10,"bold"),angle=90)
            colores=["#34D399","#F97316","#60A5FA"]; separacion=max(70,(h-130)//3)
            for i,caballo in enumerate(juego.lista_caballos):
                y=105+i*separacion; avance=min(caballo.posicion/850,1); x=margen_izq+avance*pista_ancho; canvas.create_line(margen_izq,y,meta_x,y,fill="#D6A63A",width=9); canvas.create_line(margen_izq,y+17,meta_x,y+17,fill="white",dash=(10,10)); canvas.create_text(48,y,text=str(i+1),fill=self.COLOR_DORADO,font=("Segoe UI",14,"bold")); self.dibujar_corredor(canvas,x,y,caballo.nombre,colores[i],caballo_elegido["caballo"]==caballo)
        canvas.bind("<Configure>",lambda _e:dibujar_pista())
        def seleccionar(caballo): caballo_elegido["caballo"]=caballo; mensaje.config(text=f"Apostaste por {caballo.nombre}. Ahora inicia la carrera.",fg=self.COLOR_DORADO); dibujar_pista()
        def limpiar_controles(): [w.destroy() for w in controles.winfo_children()]
        def correr():
            if caballo_elegido["caballo"] is None: mensaje.config(text="Primero debes seleccionar un corredor.",fg=self.COLOR_ERROR); return
            limpiar_controles(); ganador=None
            for caballo in juego.lista_caballos: caballo.posicion=0
            while ganador is None:
                for caballo in juego.lista_caballos:
                    caballo.posicion += random.randint(8,24)
                    if caballo.posicion >= 850: ganador=caballo; break
                dibujar_pista(); canvas.update(); self.ventana.after(36)
            juego.caballo_ganador=ganador; resultado=juego.jugar(apuesta,caballo_elegido["caballo"]); self.casino.obtener_jugador().sumar_fichas(resultado.recompensa); mensaje.config(text=resultado.mensaje,fg="#95D5B2" if resultado.gano else self.COLOR_ERROR); self.crear_boton(controles,"Volver al menú",self.pantalla_menu,16).pack(side="left",padx=6)
        dibujar_pista()
        for caballo in juego.lista_caballos: self.crear_boton(controles,caballo.nombre,lambda c=caballo:seleccionar(c),13).pack(side="left",padx=5)
        self.crear_boton(controles,"Iniciar carrera",correr,15,self.COLOR_DORADO).pack(side="left",padx=6); self.crear_boton(controles,"Volver",self.pantalla_menu,12).pack(side="left",padx=5)
    def ejecutar(self): self.ventana.mainloop()
