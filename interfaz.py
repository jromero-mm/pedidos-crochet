import math
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import font as tkfont, messagebox, ttk

from tkcalendar import Calendar, DateEntry

from pedidos import (
    actualizar_estado,
    actualizar_pedido,
    crear_base_datos,
    eliminar_pedido,
    insertar_pedido,
    obtener_pedido,
    obtener_pedidos,
)


# Paleta pastel: rosa, lavanda, melocotón y menta.
COLORES = {
    "fondo": "#FFF7FB",
    "superficie": "#FFFFFF",
    "superficie_suave": "#FFF9FC",
    "sidebar": "#704A6E",
    "sidebar_hover": "#80577E",
    "sidebar_activo": "#D98BB0",
    "rosa": "#C85F91",
    "rosa_oscuro": "#A84A77",
    "rosa_suave": "#F8E3EE",
    "lavanda": "#EEE7F6",
    "lavanda_oscuro": "#76608C",
    "menta": "#E3F4EE",
    "menta_oscuro": "#477A68",
    "melocoton": "#FFF0E5",
    "melocoton_oscuro": "#A7653C",
    "texto": "#4A3448",
    "texto_suave": "#927D91",
    "borde": "#F0DCE8",
    "borde_fuerte": "#E4C9DA",
    "encabezado": "#F8EFF5",
    "peligro": "#C65D72",
    "blanco": "#FFFFFF",
}

ESTADOS = ("Pendiente", "En proceso", "Terminado", "Entregado")
DIAS_ES = (
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
)
MESES_ES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


class CrochetApp(tk.Tk):
    """Interfaz visual del gestor de pedidos de crochet."""

    def __init__(self):
        super().__init__()

        self.title("Atelier de pedidos · Crochet")
        self.geometry("1180x760")
        self.minsize(1024, 680)
        self.configure(bg=COLORES["fondo"])

        try:
            self.familia_fuente = tkfont.nametofont("TkDefaultFont").actual("family")
        except tk.TclError:
            self.familia_fuente = "Sans"

        self.seleccion_actual = None
        self.arbol_pedidos = None
        self.todos_los_pedidos = []
        self.calendario = None
        self.detalles_canvas = None
        self.detalles_scroll = None
        self.marco_detalles = None
        self.pedidos_calendario = []
        self.formulario_cuerpo = None
        self.formulario_izquierdo = None
        self.formulario_resumen = None

        self.busqueda_var = tk.StringVar(self)
        self.filtro_var = tk.StringVar(self, value="Todos")
        self.busqueda_var.trace_add("write", self._al_cambiar_filtro)
        self.filtro_var.trace_add("write", self._al_cambiar_filtro)

        self._configurar_estilos()
        self._construir_estructura()
        self.mostrar_inicio()

    # ------------------------------------------------------------------
    # Estilos y estructura general
    # ------------------------------------------------------------------
    def _configurar_estilos(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        fuente = self.familia_fuente
        self.style.configure(
            ".",
            font=(fuente, 10),
            background=COLORES["fondo"],
            foreground=COLORES["texto"],
        )
        self.style.configure("TFrame", background=COLORES["fondo"])
        self.style.configure(
            "Surface.TFrame",
            background=COLORES["superficie"],
        )
        self.style.configure(
            "TSeparator",
            background=COLORES["borde"],
        )

        # Entradas y selectores.
        self.style.configure(
            "Modern.TEntry",
            fieldbackground=COLORES["superficie"],
            background=COLORES["superficie"],
            foreground=COLORES["texto"],
            bordercolor=COLORES["borde_fuerte"],
            lightcolor=COLORES["borde_fuerte"],
            darkcolor=COLORES["borde_fuerte"],
            insertcolor=COLORES["texto"],
            padding=(11, 9),
            relief="solid",
            borderwidth=1,
        )
        self.style.map(
            "Modern.TEntry",
            bordercolor=[("focus", COLORES["rosa"])],
            lightcolor=[("focus", COLORES["rosa"])],
            darkcolor=[("focus", COLORES["rosa"])],
        )
        self.style.configure(
            "Modern.TCombobox",
            fieldbackground=COLORES["superficie"],
            background=COLORES["superficie"],
            foreground=COLORES["texto"],
            bordercolor=COLORES["borde_fuerte"],
            lightcolor=COLORES["borde_fuerte"],
            darkcolor=COLORES["borde_fuerte"],
            arrowcolor=COLORES["rosa"],
            padding=(9, 8),
            relief="solid",
            borderwidth=1,
        )
        self.style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", COLORES["superficie"])],
            bordercolor=[("focus", COLORES["rosa"])],
            arrowcolor=[("active", COLORES["rosa_oscuro"])],
        )
        self.style.configure(
            "Modern.TSpinbox",
            fieldbackground=COLORES["superficie"],
            background=COLORES["superficie"],
            foreground=COLORES["texto"],
            bordercolor=COLORES["borde_fuerte"],
            lightcolor=COLORES["borde_fuerte"],
            darkcolor=COLORES["borde_fuerte"],
            arrowcolor=COLORES["rosa"],
            padding=(9, 8),
            relief="solid",
            borderwidth=1,
        )

        # Botones.
        button_font = (fuente, 10, "bold")
        self.style.configure(
            "Primary.TButton",
            background=COLORES["rosa"],
            foreground=COLORES["blanco"],
            borderwidth=0,
            focusthickness=0,
            padding=(16, 10),
            font=button_font,
            relief="flat",
        )
        self.style.map(
            "Primary.TButton",
            background=[
                ("active", COLORES["rosa_oscuro"]),
                ("disabled", "#D9A7BE"),
            ],
            foreground=[("disabled", COLORES["blanco"])],
        )
        self.style.configure(
            "Soft.TButton",
            background=COLORES["rosa_suave"],
            foreground=COLORES["rosa_oscuro"],
            borderwidth=0,
            focusthickness=0,
            padding=(15, 9),
            font=(fuente, 10, "bold"),
            relief="flat",
        )
        self.style.map(
            "Soft.TButton",
            background=[
                ("active", "#F1C8DB"),
                ("disabled", "#F5E8EF"),
            ],
            foreground=[("disabled", "#B79AAA")],
        )
        self.style.configure(
            "Outline.TButton",
            background=COLORES["superficie"],
            foreground=COLORES["rosa_oscuro"],
            bordercolor=COLORES["borde_fuerte"],
            lightcolor=COLORES["borde_fuerte"],
            darkcolor=COLORES["borde_fuerte"],
            borderwidth=1,
            focusthickness=0,
            padding=(14, 9),
            font=(fuente, 10, "bold"),
            relief="solid",
        )
        self.style.map(
            "Outline.TButton",
            background=[("active", COLORES["rosa_suave"])],
            bordercolor=[("active", COLORES["rosa"])],
        )
        self.style.configure(
            "Danger.TButton",
            background=COLORES["peligro"],
            foreground=COLORES["blanco"],
            borderwidth=0,
            focusthickness=0,
            padding=(14, 9),
            font=(fuente, 10, "bold"),
            relief="flat",
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", "#A9485D")],
        )
        self.style.configure(
            "Quiet.TButton",
            background=COLORES["superficie_suave"],
            foreground=COLORES["texto_suave"],
            borderwidth=0,
            focusthickness=0,
            padding=(10, 7),
            font=(fuente, 9),
            relief="flat",
        )
        self.style.map(
            "Quiet.TButton",
            background=[("active", COLORES["rosa_suave"])],
            foreground=[("active", COLORES["rosa_oscuro"])],
        )

        # Tablas.
        self.style.configure(
            "Orders.Treeview",
            background=COLORES["superficie"],
            fieldbackground=COLORES["superficie"],
            foreground=COLORES["texto"],
            rowheight=42,
            borderwidth=0,
            font=(fuente, 10),
        )
        self.style.map(
            "Orders.Treeview",
            background=[("selected", COLORES["rosa_suave"])],
            foreground=[("selected", COLORES["texto"])],
        )
        self.style.configure(
            "Orders.Treeview.Heading",
            background=COLORES["encabezado"],
            foreground=COLORES["texto_suave"],
            relief="flat",
            borderwidth=0,
            padding=(9, 10),
            font=(fuente, 9, "bold"),
        )
        self.style.map(
            "Orders.Treeview.Heading",
            background=[("active", COLORES["rosa_suave"])],
            foreground=[("active", COLORES["rosa_oscuro"])],
        )
        self.style.configure(
            "Recent.Treeview",
            background=COLORES["superficie"],
            fieldbackground=COLORES["superficie"],
            foreground=COLORES["texto"],
            rowheight=38,
            borderwidth=0,
            font=(fuente, 10),
        )
        self.style.map(
            "Recent.Treeview",
            background=[("selected", COLORES["rosa_suave"])],
        )
        self.style.configure(
            "Recent.Treeview.Heading",
            background=COLORES["encabezado"],
            foreground=COLORES["texto_suave"],
            relief="flat",
            borderwidth=0,
            padding=(8, 8),
            font=(fuente, 8, "bold"),
        )

        self.style.configure(
            "Soft.Vertical.TScrollbar",
            troughcolor=COLORES["encabezado"],
            background=COLORES["borde_fuerte"],
            bordercolor=COLORES["encabezado"],
            arrowcolor=COLORES["rosa_oscuro"],
            lightcolor=COLORES["borde_fuerte"],
            darkcolor=COLORES["borde_fuerte"],
            relief="flat",
            borderwidth=0,
        )
        self.style.configure(
            "Soft.Horizontal.TScrollbar",
            troughcolor=COLORES["encabezado"],
            background=COLORES["borde_fuerte"],
            bordercolor=COLORES["encabezado"],
            arrowcolor=COLORES["rosa_oscuro"],
            lightcolor=COLORES["borde_fuerte"],
            darkcolor=COLORES["borde_fuerte"],
            relief="flat",
            borderwidth=0,
        )

    def _construir_estructura(self):
        # Barra lateral.
        self.sidebar = tk.Frame(
            self,
            bg=COLORES["sidebar"],
            width=235,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        marca = tk.Frame(self.sidebar, bg=COLORES["sidebar"])
        marca.pack(fill="x", padx=22, pady=(28, 30))

        logo_caja = tk.Frame(
            marca,
            bg=COLORES["rosa"],
            width=48,
            height=48,
        )
        logo_caja.pack(side="left", padx=(0, 12))
        logo_caja.pack_propagate(False)
        tk.Label(
            logo_caja,
            text="✦",
            bg=COLORES["rosa"],
            fg=COLORES["blanco"],
            font=(self.familia_fuente, 24, "bold"),
        ).pack(expand=True)

        tk.Label(
            marca,
            text="Atelier\nCrochet",
            justify="left",
            bg=COLORES["sidebar"],
            fg=COLORES["blanco"],
            font=(self.familia_fuente, 15, "bold"),
        ).pack(side="left", anchor="w")

        tk.Label(
            self.sidebar,
            text="NAVEGACIÓN",
            bg=COLORES["sidebar"],
            fg="#DCC8DA",
            font=(self.familia_fuente, 8, "bold"),
            anchor="w",
        ).pack(fill="x", padx=27, pady=(0, 8))

        elementos_menu = (
            ("inicio", "⌂", "Inicio"),
            ("pedidos", "▦", "Pedidos"),
            ("nuevo", "＋", "Nuevo pedido"),
            ("calendario", "◷", "Calendario"),
        )
        self.botones_menu = {}

        for clave, icono, texto in elementos_menu:
            boton = tk.Button(
                self.sidebar,
                text=f"  {icono}    {texto}",
                anchor="w",
                relief="flat",
                bd=0,
                highlightthickness=0,
                bg=COLORES["sidebar"],
                fg=COLORES["blanco"],
                activebackground=COLORES["sidebar_hover"],
                activeforeground=COLORES["blanco"],
                font=(self.familia_fuente, 10, "bold"),
                padx=12,
                pady=12,
                cursor="hand2",
                command=lambda c=clave: self._navegar(c),
            )
            boton.pack(fill="x", padx=14, pady=3)
            self.botones_menu[clave] = boton

        pie_sidebar = tk.Frame(
            self.sidebar,
            bg=COLORES["sidebar_hover"],
            padx=15,
            pady=14,
        )
        pie_sidebar.pack(side="bottom", fill="x", padx=18, pady=20)
        tk.Label(
            pie_sidebar,
            text="♡",
            bg=COLORES["sidebar_hover"],
            fg="#FFD6E7",
            font=(self.familia_fuente, 22, "bold"),
        ).pack(anchor="w")
        tk.Label(
            pie_sidebar,
            text="Cada puntada cuenta",
            bg=COLORES["sidebar_hover"],
            fg=COLORES["blanco"],
            font=(self.familia_fuente, 10, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(4, 2))
        tk.Label(
            pie_sidebar,
            text="Organiza tu atelier\ncon cariño y calma.",
            justify="left",
            bg=COLORES["sidebar_hover"],
            fg="#E7D3E5",
            font=(self.familia_fuente, 9),
            anchor="w",
        ).pack(anchor="w")

        # Área principal y encabezado.
        self.area_principal = tk.Frame(self, bg=COLORES["fondo"])
        self.area_principal.pack(side="right", fill="both", expand=True)

        encabezado = tk.Frame(self.area_principal, bg=COLORES["fondo"])
        encabezado.pack(fill="x", padx=32, pady=(25, 0))

        textos = tk.Frame(encabezado, bg=COLORES["fondo"])
        textos.pack(side="left", fill="x", expand=True)

        self.etiqueta_seccion = tk.Label(
            textos,
            text="PANEL GENERAL",
            bg=COLORES["fondo"],
            fg=COLORES["rosa"],
            font=(self.familia_fuente, 9, "bold"),
            anchor="w",
        )
        self.etiqueta_seccion.pack(anchor="w")
        self.titulo_pagina = tk.Label(
            textos,
            text="Resumen",
            bg=COLORES["fondo"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 23, "bold"),
            anchor="w",
        )
        self.titulo_pagina.pack(anchor="w", pady=(3, 0))
        self.subtitulo_pagina = tk.Label(
            textos,
            text="",
            bg=COLORES["fondo"],
            fg=COLORES["texto_suave"],
            font=(self.familia_fuente, 10),
            anchor="w",
        )
        self.subtitulo_pagina.pack(anchor="w", pady=(3, 0))

        indicadores = tk.Frame(encabezado, bg=COLORES["fondo"])
        indicadores.pack(side="right", anchor="e", pady=8)
        self.etiqueta_fecha = tk.Label(
            indicadores,
            text=datetime.now().strftime("%d/%m/%Y"),
            bg=COLORES["fondo"],
            fg=COLORES["texto_suave"],
            font=(self.familia_fuente, 10),
        )
        self.etiqueta_fecha.pack(side="right", padx=(0, 15))
        tk.Label(
            indicadores,
            text="●  Base de datos lista",
            bg=COLORES["menta"],
            fg=COLORES["menta_oscuro"],
            font=(self.familia_fuente, 9, "bold"),
            padx=12,
            pady=6,
        ).pack(side="right")

        # El contenido vive dentro de un área desplazable para que la
        # aplicación siga siendo cómoda en pantallas pequeñas.
        self.contenido_externo = tk.Frame(self.area_principal, bg=COLORES["fondo"])
        self.contenido_externo.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=(14, 18),
        )
        self.contenido_canvas = tk.Canvas(
            self.contenido_externo,
            bg=COLORES["fondo"],
            highlightthickness=0,
            bd=0,
        )
        self.contenido_scroll = ttk.Scrollbar(
            self.contenido_externo,
            orient="vertical",
            command=self.contenido_canvas.yview,
            style="Soft.Vertical.TScrollbar",
        )
        self.contenido_scroll.pack(side="right", fill="y", padx=(8, 0))
        self.contenido_canvas.pack(side="left", fill="both", expand=True)
        self.contenido_canvas.configure(yscrollcommand=self.contenido_scroll.set)
        self.contenido = tk.Frame(self.contenido_canvas, bg=COLORES["fondo"])
        self.contenido_window = self.contenido_canvas.create_window(
            (0, 0),
            window=self.contenido,
            anchor="nw",
        )
        self.contenido.bind("<Configure>", self._configurar_scroll_contenido)
        self.contenido_canvas.bind("<Configure>", self._ajustar_ancho_contenido)
        self.contenido_canvas.bind("<MouseWheel>", self._desplazar_contenido)
        self.contenido_canvas.bind("<Button-4>", self._desplazar_contenido)
        self.contenido_canvas.bind("<Button-5>", self._desplazar_contenido)

    def _configurar_scroll_contenido(self, _evento):
        self.contenido_canvas.configure(
            scrollregion=self.contenido_canvas.bbox("all")
        )

    def _ajustar_ancho_contenido(self, evento):
        self.contenido_canvas.itemconfigure(
            self.contenido_window,
            width=evento.width,
        )

    def _desplazar_contenido(self, evento):
        if not self.contenido_canvas.winfo_exists():
            return
        numero = getattr(evento, "num", None)
        delta = getattr(evento, "delta", 0)
        if numero == 4:
            direccion = -1
        elif numero == 5:
            direccion = 1
        elif delta:
            direccion = -1 if delta > 0 else 1
        else:
            return

        region = self.contenido_canvas.bbox("all")
        if not region or region[3] <= self.contenido_canvas.winfo_height():
            return "break"
        self.contenido_canvas.yview_scroll(direccion, "units")
        return "break"

    def _navegar(self, destino):
        if destino == "inicio":
            self.mostrar_inicio()
        elif destino == "pedidos":
            self.mostrar_pedidos()
        elif destino == "nuevo":
            self.mostrar_formulario()
        elif destino == "calendario":
            self.mostrar_calendario()

    def _activar_menu(self, activo):
        for clave, boton in self.botones_menu.items():
            if clave == activo:
                boton.configure(
                    bg=COLORES["sidebar_activo"],
                    fg=COLORES["blanco"],
                    activebackground=COLORES["sidebar_activo"],
                )
            else:
                boton.configure(
                    bg=COLORES["sidebar"],
                    fg=COLORES["blanco"],
                    activebackground=COLORES["sidebar_hover"],
                )

    def _configurar_pagina(self, seccion, titulo, subtitulo):
        self.etiqueta_seccion.config(text=seccion.upper())
        self.titulo_pagina.config(text=titulo)
        self.subtitulo_pagina.config(text=subtitulo)

    def _limpiar_contenido(self):
        for hijo in self.contenido.winfo_children():
            hijo.destroy()
        self.arbol_pedidos = None
        self.calendario = None
        self.detalles_canvas = None
        self.detalles_scroll = None
        self.marco_detalles = None
        self.formulario_cuerpo = None
        self.formulario_izquierdo = None
        self.formulario_resumen = None
        self.contenido_canvas.yview_moveto(0)

    def _crear_tarjeta(
        self,
        padre,
        bg=COLORES["superficie"],
        border=COLORES["borde"],
        **opciones_pack,
    ):
        marco = tk.Frame(padre, bg=border, padx=1, pady=1)
        marco.pack(**opciones_pack)
        tarjeta = tk.Frame(marco, bg=bg)
        tarjeta.pack(fill="both", expand=False)
        return tarjeta

    def _crear_boton(self, padre, texto, comando, tipo="suave", ancho=None):
        estilos = {
            "primario": "Primary.TButton",
            "suave": "Soft.TButton",
            "contorno": "Outline.TButton",
            "peligro": "Danger.TButton",
            "discreto": "Quiet.TButton",
        }
        argumentos = {
            "text": texto,
            "command": comando,
            "style": estilos.get(tipo, "Soft.TButton"),
            "cursor": "hand2",
        }
        if ancho is not None:
            argumentos["width"] = ancho
        return ttk.Button(padre, **argumentos)

    @staticmethod
    def _dinero(valor):
        try:
            return f"S/ {float(valor):,.2f}"
        except (TypeError, ValueError):
            return "S/ 0.00"

    @staticmethod
    def _fecha_corta(fecha):
        try:
            return datetime.strptime(str(fecha), "%Y-%m-%d").strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return str(fecha)

    @staticmethod
    def _fecha_larga(fecha):
        try:
            valor = datetime.strptime(str(fecha), "%Y-%m-%d")
            dia = DIAS_ES[valor.weekday()]
            mes = MESES_ES[valor.month - 1]
            return f"{dia}, {valor.day} de {mes} de {valor.year}"
        except (TypeError, ValueError):
            return str(fecha)

    def _leer_pedidos(self):
        try:
            return obtener_pedidos()
        except sqlite3.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron cargar los pedidos:\n{error}",
                parent=self,
            )
            return []

    # ------------------------------------------------------------------
    # Inicio
    # ------------------------------------------------------------------
    def mostrar_inicio(self):
        self._activar_menu("inicio")
        self._configurar_pagina(
            "Panel general",
            "Resumen",
            "Una mirada amable a todo lo que estás creando.",
        )
        self._limpiar_contenido()
        pedidos = self._leer_pedidos()

        # Tarjeta de bienvenida.
        bienvenida = self._crear_tarjeta(self.contenido, fill="x", pady=(0, 18))
        izquierda = tk.Frame(bienvenida, bg=COLORES["superficie"])
        izquierda.pack(side="left", fill="both", expand=True, padx=(28, 10), pady=16)
        derecha = tk.Canvas(
            bienvenida,
            width=185,
            height=145,
            bg=COLORES["superficie"],
            highlightthickness=0,
        )
        derecha.pack(side="right", padx=22, pady=16)
        derecha.create_oval(
            28, 20, 160, 150,
            fill=COLORES["rosa_suave"],
            outline="",
        )
        derecha.create_oval(
            78, 4, 178, 105,
            fill=COLORES["lavanda"],
            outline="",
        )
        derecha.create_text(
            100, 76,
            text="♡",
            fill=COLORES["rosa"],
            font=(self.familia_fuente, 36, "bold"),
        )
        derecha.create_text(
            100, 129,
            text="creando con calma",
            fill=COLORES["rosa_oscuro"],
            font=(self.familia_fuente, 8, "bold"),
        )

        tk.Label(
            izquierda,
            text="✦  TU ESPACIO CREATIVO",
            bg=COLORES["rosa_suave"],
            fg=COLORES["rosa_oscuro"],
            font=(self.familia_fuente, 9, "bold"),
            padx=11,
            pady=5,
        ).pack(anchor="w")
        tk.Label(
            izquierda,
            text="Cada puntada cuenta.",
            bg=COLORES["superficie"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 23, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(14, 3))
        tk.Label(
            izquierda,
            text="Lleva tus pedidos, fechas y pagos en un solo lugar\npara dedicarte más a lo que te encanta.",
            justify="left",
            bg=COLORES["superficie"],
            fg=COLORES["texto_suave"],
            font=(self.familia_fuente, 10),
            anchor="w",
        ).pack(anchor="w", pady=(0, 15))
        acciones = tk.Frame(izquierda, bg=COLORES["superficie"])
        acciones.pack(anchor="w")
        self._crear_boton(
            acciones,
            "＋  Crear pedido",
            self.mostrar_formulario,
            tipo="primario",
        ).pack(side="left")
        self._crear_boton(
            acciones,
            "Ver pedidos",
            self.mostrar_pedidos,
            tipo="contorno",
        ).pack(side="left", padx=(10, 0))

        # Indicadores.
        indicadores = tk.Frame(self.contenido, bg=COLORES["fondo"])
        indicadores.pack(fill="x", pady=(0, 18))

        pendientes = sum(1 for pedido in pedidos if pedido[7] == "Pendiente")
        en_proceso = sum(1 for pedido in pedidos if pedido[7] == "En proceso")
        saldo_total = sum(float(pedido[5] or 0) for pedido in pedidos)

        self._tarjeta_metrica(
            indicadores,
            "Pedidos",
            str(len(pedidos)),
            "▦",
            COLORES["rosa"],
            COLORES["rosa_suave"],
        )
        self._tarjeta_metrica(
            indicadores,
            "Pendientes",
            str(pendientes),
            "○",
            "#B7772B",
            COLORES["melocoton"],
        )
        self._tarjeta_metrica(
            indicadores,
            "En proceso",
            str(en_proceso),
            "✧",
            COLORES["lavanda_oscuro"],
            COLORES["lavanda"],
        )
        self._tarjeta_metrica(
            indicadores,
            "Saldo por cobrar",
            self._dinero(saldo_total),
            "♡",
            COLORES["menta_oscuro"],
            COLORES["menta"],
        )

        # Últimos pedidos.
        recientes = self._crear_tarjeta(
            self.contenido,
            fill="both",
            expand=True,
        )
        cabecera = tk.Frame(recientes, bg=COLORES["superficie"])
        cabecera.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(
            cabecera,
            text="Pedidos recientes",
            bg=COLORES["superficie"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 12, "bold"),
        ).pack(side="left")
        self._crear_boton(
            cabecera,
            "Ver todos",
            self.mostrar_pedidos,
            tipo="discreto",
        ).pack(side="right")

        if not pedidos:
            self._estado_vacio(
                recientes,
                " todavía no hay pedidos",
                "Cuando guardes tu primer pedido aparecerá aquí.",
            )
        else:
            tabla_caja = tk.Frame(recientes, bg=COLORES["superficie"])
            tabla_caja.pack(fill="both", expand=True, padx=20, pady=(0, 18))
            columnas = ("id", "cliente", "producto", "total", "estado")
            tabla = ttk.Treeview(
                tabla_caja,
                columns=columnas,
                show="headings",
                height=2,
                style="Recent.Treeview",
            )
            titulos = {
                "id": "PEDIDO",
                "cliente": "CLIENTE",
                "producto": "PRODUCTO",
                "total": "TOTAL",
                "estado": "ESTADO",
            }
            anchos = {"id": 65, "cliente": 170, "producto": 190, "total": 100, "estado": 115}
            for columna in columnas:
                tabla.heading(columna, text=titulos[columna])
                tabla.column(
                    columna,
                    width=anchos[columna],
                    anchor="center" if columna in ("id", "total", "estado") else "w",
                )
            for pedido in pedidos[:2]:
                tag = self._tag_estado(pedido[7])
                tabla.insert(
                    "",
                    "end",
                    values=(
                        f"#{pedido[0]}",
                        pedido[1],
                        pedido[2],
                        self._dinero(pedido[3]),
                        pedido[7],
                    ),
                    tags=(tag,),
                )
            tabla.tag_configure("par", background=COLORES["superficie_suave"])
            tabla.tag_configure("Pendiente", background=COLORES["melocoton"], foreground=COLORES["melocoton_oscuro"])
            tabla.tag_configure("En proceso", background=COLORES["lavanda"], foreground=COLORES["lavanda_oscuro"])
            tabla.tag_configure("Terminado", background=COLORES["menta"], foreground=COLORES["menta_oscuro"])
            tabla.tag_configure("Entregado", background=COLORES["rosa_suave"], foreground=COLORES["rosa_oscuro"])
            tabla.pack(fill="both", expand=True)

    def _tarjeta_metrica(self, padre, titulo, valor, icono, color, fondo):
        tarjeta = self._crear_tarjeta(
            padre,
            fill="both",
            expand=True,
            side="left",
            padx=(0, 12),
        )
        barra = tk.Frame(tarjeta, bg=color, width=5)
        barra.pack(side="left", fill="y", padx=(17, 13), pady=17)
        textos = tk.Frame(tarjeta, bg=fondo)
        textos.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=13)
        tk.Label(
            textos,
            text=f"{icono}  {titulo.upper()}",
            bg=fondo,
            fg=COLORES["texto_suave"],
            font=(self.familia_fuente, 8, "bold"),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            textos,
            text=valor,
            bg=fondo,
            fg=COLORES["texto"],
            font=(self.familia_fuente, 19, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(5, 0))

    def _estado_vacio(self, padre, titulo, descripcion):
        marco = tk.Frame(padre, bg=COLORES["superficie_suave"])
        marco.pack(fill="both", expand=True, padx=20, pady=(3, 20))
        tk.Label(
            marco,
            text="♡",
            bg=COLORES["superficie_suave"],
            fg=COLORES["rosa"],
            font=(self.familia_fuente, 30, "bold"),
        ).pack(pady=(17, 2))
        tk.Label(
            marco,
            text=titulo,
            bg=COLORES["superficie_suave"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 11, "bold"),
        ).pack()
        tk.Label(
            marco,
            text=descripcion,
            bg=COLORES["superficie_suave"],
            fg=COLORES["texto_suave"],
            font=(self.familia_fuente, 9),
        ).pack(pady=(4, 17))

    # ------------------------------------------------------------------
    # Listado de pedidos
    # ------------------------------------------------------------------
    def mostrar_pedidos(self):
        self._activar_menu("pedidos")
        self._configurar_pagina(
            "Gestión",
            "Pedidos",
            "Consulta, organiza y actualiza cada encargo de tu atelier.",
        )
        self._limpiar_contenido()
        self.todos_los_pedidos = self._leer_pedidos()
        self.seleccion_actual = None
        self.busqueda_var.set("")
        self.filtro_var.set("Todos")

        herramientas = self._crear_tarjeta(
            self.contenido,
            fill="x",
            pady=(0, 15),
        )
        fila_herramientas = tk.Frame(herramientas, bg=COLORES["superficie"])
        fila_herramientas.pack(fill="x", padx=20, pady=17)
        tk.Label(
            fila_herramientas,
            text="Todos tus encargos",
            bg=COLORES["superficie"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 12, "bold"),
        ).pack(side="left")
        self._crear_boton(
            fila_herramientas,
            "＋  Nuevo pedido",
            self.mostrar_formulario,
            tipo="primario",
        ).pack(side="right")

        controles = tk.Frame(herramientas, bg=COLORES["superficie"])
        controles.pack(fill="x", padx=20, pady=(0, 17))
        buscar = tk.Frame(controles, bg=COLORES["superficie"])
        buscar.pack(side="left", fill="x", expand=True)
        tk.Label(
            buscar,
            text="⌕",
            bg=COLORES["superficie"],
            fg=COLORES["rosa"],
            font=(self.familia_fuente, 17, "bold"),
        ).pack(side="left", padx=(0, 7))
        ttk.Entry(
            buscar,
            textvariable=self.busqueda_var,
            style="Modern.TEntry",
            width=30,
        ).pack(side="left", fill="x", expand=True, padx=(0, 12))

        filtro_caja = tk.Frame(controles, bg=COLORES["superficie"])
        filtro_caja.pack(side="right")
        tk.Label(
            filtro_caja,
            text="Estado:",
            bg=COLORES["superficie"],
            fg=COLORES["texto_suave"],
            font=(self.familia_fuente, 9),
        ).pack(side="left", padx=(0, 7))
        ttk.Combobox(
            filtro_caja,
            textvariable=self.filtro_var,
            values=("Todos",) + ESTADOS,
            state="readonly",
            style="Modern.TCombobox",
            width=14,
        ).pack(side="left")

        tarjeta_tabla = self._crear_tarjeta(
            self.contenido,
            fill="both",
            expand=True,
        )
        cabecera_tabla = tk.Frame(tarjeta_tabla, bg=COLORES["superficie"])
        cabecera_tabla.pack(fill="x", padx=20, pady=(17, 10))
        tk.Label(
            cabecera_tabla,
            text="Listado de pedidos",
            bg=COLORES["superficie"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 12, "bold"),
        ).pack(side="left")
        self.etiqueta_cantidad = tk.Label(
            cabecera_tabla,
            text="",
            bg=COLORES["rosa_suave"],
            fg=COLORES["rosa_oscuro"],
            font=(self.familia_fuente, 9, "bold"),
            padx=10,
            pady=4,
        )
        self.etiqueta_cantidad.pack(side="right")

        # La barra de acciones se reserva abajo antes de la tabla.
        barra_acciones = tk.Frame(
            tarjeta_tabla,
            bg=COLORES["superficie_suave"],
            padx=16,
            pady=11,
        )
        barra_acciones.pack(side="bottom", fill="x")
        self.etiqueta_seleccion = tk.Label(
            barra_acciones,
            text="Selecciona un pedido para ver sus acciones",
            bg=COLORES["superficie_suave"],
            fg=COLORES["texto_suave"],
            font=(self.familia_fuente, 9),
            anchor="w",
        )
        self.etiqueta_seleccion.pack(fill="x", pady=(0, 7))

        controles_estado = tk.Frame(
            barra_acciones,
            bg=COLORES["superficie_suave"],
        )
        controles_estado.pack(fill="x")
        self.estado_seleccion_var = tk.StringVar(self, value="Pendiente")
        self.combo_estado = ttk.Combobox(
            controles_estado,
            textvariable=self.estado_seleccion_var,
            values=ESTADOS,
            state="readonly",
            style="Modern.TCombobox",
            width=13,
        )
        self.combo_estado.pack(side="right", padx=(8, 0))
        self.boton_editar = self._crear_boton(
            controles_estado,
            "Editar",
            self._editar_seleccion,
            tipo="contorno",
        )
        self.boton_editar.pack(side="right", padx=(0, 7))
        self.boton_eliminar = self._crear_boton(
            controles_estado,
            "Eliminar",
            self._eliminar_seleccion,
            tipo="peligro",
        )
        self.boton_eliminar.pack(side="right", padx=(0, 7))
        self.boton_actualizar_estado = self._crear_boton(
            controles_estado,
            "Guardar estado",
            self._actualizar_estado_seleccion,
            tipo="primario",
        )
        self.boton_actualizar_estado.pack(side="right")
        self._habilitar_acciones(False)

        marco_tabla = tk.Frame(tarjeta_tabla, bg=COLORES["superficie"])
        marco_tabla.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        marco_tabla.columnconfigure(0, weight=1)
        marco_tabla.rowconfigure(0, weight=1)
        columnas = (
            "id",
            "cliente",
            "producto",
            "total",
            "adelanto",
            "saldo",
            "entrega",
            "estado",
        )
        self.arbol_pedidos = ttk.Treeview(
            marco_tabla,
            columns=columnas,
            show="headings",
            selectmode="browse",
            height=4,
            style="Orders.Treeview",
        )
        titulos = {
            "id": "ID",
            "cliente": "CLIENTE",
            "producto": "PRODUCTO",
            "total": "TOTAL",
            "adelanto": "ADELANTO",
            "saldo": "SALDO",
            "entrega": "ENTREGA",
            "estado": "ESTADO",
        }
        anchos = {
            "id": 48,
            "cliente": 145,
            "producto": 150,
            "total": 88,
            "adelanto": 88,
            "saldo": 88,
            "entrega": 95,
            "estado": 105,
        }
        for columna in columnas:
            self.arbol_pedidos.heading(columna, text=titulos[columna])
            self.arbol_pedidos.column(
                columna,
                width=anchos[columna],
                minwidth=anchos[columna],
                anchor="center" if columna not in ("cliente", "producto") else "w",
                stretch=columna in ("cliente", "producto"),
            )

        scroll_y = ttk.Scrollbar(
            marco_tabla,
            orient="vertical",
            command=self.arbol_pedidos.yview,
            style="Soft.Vertical.TScrollbar",
        )
        scroll_x = ttk.Scrollbar(
            marco_tabla,
            orient="horizontal",
            command=self.arbol_pedidos.xview,
            style="Soft.Horizontal.TScrollbar",
        )
        self.arbol_pedidos.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )
        self.arbol_pedidos.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        scroll_x.grid(row=1, column=0, sticky="ew")

        self.arbol_pedidos.tag_configure(
            "par", background=COLORES["superficie_suave"]
        )
        self.arbol_pedidos.tag_configure(
            "Pendiente",
            background=COLORES["melocoton"],
            foreground=COLORES["melocoton_oscuro"],
        )
        self.arbol_pedidos.tag_configure(
            "En proceso",
            background=COLORES["lavanda"],
            foreground=COLORES["lavanda_oscuro"],
        )
        self.arbol_pedidos.tag_configure(
            "Terminado",
            background=COLORES["menta"],
            foreground=COLORES["menta_oscuro"],
        )
        self.arbol_pedidos.tag_configure(
            "Entregado",
            background=COLORES["rosa_suave"],
            foreground=COLORES["rosa_oscuro"],
        )
        self.arbol_pedidos.bind("<<TreeviewSelect>>", self._al_seleccionar_pedido)
        self._renderizar_pedidos()

    def _al_cambiar_filtro(self, *_):
        self._renderizar_pedidos()

    def _tag_estado(self, estado):
        return {
            "Pendiente": "Pendiente",
            "En proceso": "En proceso",
            "Terminado": "Terminado",
            "Entregado": "Entregado",
        }.get(str(estado), "par")

    def _renderizar_pedidos(self, seleccionar_id=None):
        if self.arbol_pedidos is None:
            return

        self.arbol_pedidos.delete(*self.arbol_pedidos.get_children())
        consulta = self.busqueda_var.get().strip().casefold()
        filtro = self.filtro_var.get()
        filtrados = []
        for pedido in self.todos_los_pedidos:
            coincide_texto = not consulta or any(
                consulta in str(valor).casefold()
                for valor in (pedido[1], pedido[2], pedido[7], pedido[0])
            )
            coincide_estado = filtro == "Todos" or pedido[7] == filtro
            if coincide_texto and coincide_estado:
                filtrados.append(pedido)

        for indice, pedido in enumerate(filtrados):
            tag = self._tag_estado(pedido[7])
            if tag == "par" and indice % 2:
                tag = "par"
            self.arbol_pedidos.insert(
                "",
                "end",
                iid=str(pedido[0]),
                values=(
                    f"#{pedido[0]}",
                    pedido[1],
                    pedido[2],
                    self._dinero(pedido[3]),
                    self._dinero(pedido[4]),
                    self._dinero(pedido[5]),
                    self._fecha_corta(pedido[6]),
                    pedido[7],
                ),
                tags=(tag,),
            )

        self.etiqueta_cantidad.config(
            text=f"{len(filtrados)} pedido" + ("s" if len(filtrados) != 1 else "")
        )
        if seleccionar_id is not None and self.arbol_pedidos.exists(str(seleccionar_id)):
            self.arbol_pedidos.selection_set(str(seleccionar_id))
            self.arbol_pedidos.focus(str(seleccionar_id))
            self._al_seleccionar_pedido()
        else:
            self.seleccion_actual = None
            self.etiqueta_seleccion.config(
                text="Selecciona un pedido para ver sus acciones"
            )
            self._habilitar_acciones(False)

    def _habilitar_acciones(self, habilitado):
        estado = "normal" if habilitado else "disabled"
        for boton in (
            self.boton_editar,
            self.boton_eliminar,
            self.boton_actualizar_estado,
        ):
            boton.configure(state=estado)
        self.combo_estado.configure(
            state="readonly" if habilitado else "disabled"
        )

    def _al_seleccionar_pedido(self, _evento=None):
        if self.arbol_pedidos is None:
            return
        seleccion = self.arbol_pedidos.selection()
        if not seleccion:
            self.seleccion_actual = None
            self.etiqueta_seleccion.config(
                text="Selecciona un pedido para ver sus acciones"
            )
            self._habilitar_acciones(False)
            return

        try:
            pedido_id = int(seleccion[0])
        except (TypeError, ValueError):
            return

        pedido = next(
            (item for item in self.todos_los_pedidos if item[0] == pedido_id),
            None,
        )
        if pedido is None:
            return

        self.seleccion_actual = pedido
        self.estado_seleccion_var.set(pedido[7])
        self.etiqueta_seleccion.config(
            text=f"Pedido #{pedido_id}  ·  {pedido[1]}  ·  {pedido[7]}",
            fg=COLORES["rosa_oscuro"],
        )
        self._habilitar_acciones(True)

    def _actualizar_estado_seleccion(self):
        if self.seleccion_actual is None:
            return
        pedido_id = self.seleccion_actual[0]
        estado = self.estado_seleccion_var.get()
        try:
            actualizar_estado(pedido_id, estado)
        except sqlite3.Error as error:
            messagebox.showerror(
                "No se pudo actualizar",
                f"No se pudo cambiar el estado del pedido:\n{error}",
                parent=self,
            )
            return

        self.todos_los_pedidos = self._leer_pedidos()
        self._renderizar_pedidos(seleccionar_id=pedido_id)
        messagebox.showinfo(
            "Estado actualizado",
            f"El pedido #{pedido_id} ahora está en estado «{estado}».",
            parent=self,
        )

    def _editar_seleccion(self):
        if self.seleccion_actual is None:
            return
        try:
            pedido = obtener_pedido(self.seleccion_actual[0])
        except sqlite3.Error as error:
            messagebox.showerror(
                "No se pudo abrir el pedido",
                str(error),
                parent=self,
            )
            return
        if pedido is not None:
            self.mostrar_formulario(pedido)

    def _eliminar_seleccion(self):
        if self.seleccion_actual is None:
            return
        pedido_id = self.seleccion_actual[0]
        cliente = self.seleccion_actual[1]
        confirmar = messagebox.askyesno(
            "Eliminar pedido",
            f"¿Seguro que deseas eliminar el pedido #{pedido_id} de «{cliente}»?\n\nEsta acción no se puede deshacer.",
            parent=self,
        )
        if not confirmar:
            return
        try:
            eliminar_pedido(pedido_id)
        except sqlite3.Error as error:
            messagebox.showerror(
                "No se pudo eliminar",
                f"No se pudo eliminar el pedido:\n{error}",
                parent=self,
            )
            return

        self.todos_los_pedidos = self._leer_pedidos()
        self._renderizar_pedidos()
        messagebox.showinfo(
            "Pedido eliminado",
            "El pedido se eliminó correctamente.",
            parent=self,
        )

    # ------------------------------------------------------------------
    # Formulario de pedido
    # ------------------------------------------------------------------
    def mostrar_formulario(self, pedido=None):
        self._activar_menu("pedidos" if pedido is not None else "nuevo")
        self._configurar_pagina(
            "Pedidos" if pedido is None else "Edición",
            "Nuevo pedido" if pedido is None else f"Editar pedido #{pedido[0]}",
            "Registra los datos de tu encargo con unos pocos pasos.",
        )
        self._limpiar_contenido()

        tarjeta = self._crear_tarjeta(
            self.contenido,
            fill="both",
            expand=True,
        )
        cabecera = tk.Frame(tarjeta, bg=COLORES["superficie"])
        cabecera.pack(fill="x", padx=28, pady=(22, 0))
        tk.Label(
            cabecera,
            text="✦  Información del encargo",
            bg=COLORES["superficie"],
            fg=COLORES["rosa_oscuro"],
            font=(self.familia_fuente, 13, "bold"),
        ).pack(side="left")
        etiqueta_modo = tk.Label(
            cabecera,
            text="NUEVO REGISTRO" if pedido is None else "EDICIÓN",
            bg=COLORES["lavanda"] if pedido is None else COLORES["menta"],
            fg=COLORES["lavanda_oscuro"] if pedido is None else COLORES["menta_oscuro"],
            font=(self.familia_fuente, 8, "bold"),
            padx=11,
            pady=5,
        )
        etiqueta_modo.pack(side="right")

        cuerpo = tk.Frame(tarjeta, bg=COLORES["superficie"])
        cuerpo.pack(fill="both", expand=True, padx=28, pady=(18, 26))
        self.formulario_cuerpo = cuerpo
        formulario = tk.Frame(cuerpo, bg=COLORES["superficie"])
        formulario.pack(side="left", fill="both", expand=True, padx=(0, 28))
        self.formulario_izquierdo = formulario
        formulario.columnconfigure(0, weight=1)
        formulario.columnconfigure(1, weight=1)
        formulario.rowconfigure(3, weight=1)

        self.cliente_var = tk.StringVar(self)
        self.telefono_var = tk.StringVar(self)
        self.producto_var = tk.StringVar(self)
        self.precio_var = tk.StringVar(self)
        self.adelanto_var = tk.StringVar(self, value="0.00")

        self._campo_formulario(
            formulario,
            0,
            0,
            "Nombre del cliente",
            self.cliente_var,
            obligatorio=True,
        )
        self._campo_formulario(
            formulario,
            0,
            1,
            "Teléfono",
            self.telefono_var,
            obligatorio=False,
        )
        self._campo_formulario(
            formulario,
            1,
            0,
            "Producto a realizar",
            self.producto_var,
            obligatorio=True,
            ancho_columna=2,
        )
        self._campo_formulario(
            formulario,
            2,
            0,
            "Precio total",
            self.precio_var,
            obligatorio=True,
            ayuda="Ejemplo: 85.00",
        )
        self._campo_formulario(
            formulario,
            2,
            1,
            "Adelanto recibido",
            self.adelanto_var,
            obligatorio=True,
            ayuda="Ejemplo: 30.00",
        )

        fecha_marco = tk.Frame(formulario, bg=COLORES["superficie"])
        fecha_marco.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 18),
        )
        tk.Label(
            fecha_marco,
            text="Fecha de entrega",
            bg=COLORES["superficie"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 9, "bold"),
        ).pack(anchor="w", pady=(0, 6))
        self.entrada_fecha = DateEntry(
            fecha_marco,
            width=22,
            date_pattern="yyyy-mm-dd",
            font=(self.familia_fuente, 10),
            background=COLORES["superficie"],
            foreground=COLORES["texto"],
            bordercolor=COLORES["borde_fuerte"],
            arrowcolor=COLORES["rosa"],
        )
        self.entrada_fecha.pack(anchor="w", ipadx=3, ipady=3)
        self.entrada_fecha.configure(style="DateEntry")
        self.style.configure(
            "DateEntry",
            fieldbackground=COLORES["superficie"],
            background=COLORES["superficie"],
            foreground=COLORES["texto"],
            bordercolor=COLORES["borde_fuerte"],
            lightcolor=COLORES["borde_fuerte"],
            darkcolor=COLORES["borde_fuerte"],
            arrowcolor=COLORES["rosa"],
            arrowsize=14,
            padding=(10, 8),
            relief="solid",
            borderwidth=1,
        )
        self.style.map(
            "DateEntry",
            bordercolor=[("focus", COLORES["rosa"])],
            arrowcolor=[("active", COLORES["rosa_oscuro"])],
        )

        # Panel lateral de resumen.
        resumen = self._crear_tarjeta(
            cuerpo,
            fill="y",
            bg=COLORES["rosa_suave"],
            border=COLORES["borde"],
        )
        # El método _crear_tarjeta usa un marco de borde; el panel recibe el
        # color suave para que el formulario tenga un punto de acento visual.
        resumen.configure(bg=COLORES["rosa_suave"])
        resumen.pack_configure(pady=0)
        self.formulario_resumen = resumen.master
        cuerpo.bind("<Configure>", self._adaptar_formulario)
        self.after_idle(self._adaptar_formulario)
        tk.Label(
            resumen,
            text="♡",
            bg=COLORES["rosa_suave"],
            fg=COLORES["rosa"],
            font=(self.familia_fuente, 28, "bold"),
        ).pack(anchor="w", padx=22, pady=(23, 0))
        tk.Label(
            resumen,
            text="Resumen del pedido",
            bg=COLORES["rosa_suave"],
            fg=COLORES["rosa_oscuro"],
            font=(self.familia_fuente, 13, "bold"),
        ).pack(anchor="w", padx=22, pady=(2, 19))
        self.resumen_total_var = tk.StringVar(self, value="S/ 0.00")
        self.resumen_adelanto_var = tk.StringVar(self, value="S/ 0.00")
        self.resumen_saldo_var = tk.StringVar(self, value="S/ 0.00")
        self._linea_resumen(resumen, "Total", self.resumen_total_var)
        self._linea_resumen(resumen, "Adelanto", self.resumen_adelanto_var)
        separador = tk.Frame(resumen, bg="#E8C9DA", height=1)
        separador.pack(fill="x", padx=22, pady=16)
        self._linea_resumen(resumen, "Saldo pendiente", self.resumen_saldo_var, destacado=True)
        tk.Label(
            resumen,
            text="El saldo se calcula automáticamente\nantes de guardar el pedido.",
            justify="left",
            bg=COLORES["rosa_suave"],
            fg=COLORES["rosa_oscuro"],
            font=(self.familia_fuente, 9),
        ).pack(anchor="w", padx=22, pady=(20, 0))
        self.etiqueta_estado_formulario = tk.Label(
            resumen,
            text="Estado: Pendiente",
            bg=COLORES["blanco"],
            fg=COLORES["rosa_oscuro"],
            font=(self.familia_fuente, 9, "bold"),
            padx=10,
            pady=6,
        )
        self.etiqueta_estado_formulario.pack(anchor="w", padx=22, pady=(18, 22))

        # Rellenar datos si estamos editando.
        if pedido is not None:
            self.cliente_var.set(str(pedido[1]))
            self.telefono_var.set(str(pedido[2] or ""))
            self.producto_var.set(str(pedido[3]))
            self.precio_var.set(f"{float(pedido[4]):.2f}")
            self.adelanto_var.set(f"{float(pedido[5]):.2f}")
            try:
                fecha = datetime.strptime(pedido[6], "%Y-%m-%d").date()
                self.entrada_fecha.set_date(fecha)
            except (TypeError, ValueError):
                pass
            self.etiqueta_estado_formulario.config(
                text=f"Estado actual: {pedido[7]}",
                bg=COLORES["menta"],
                fg=COLORES["menta_oscuro"],
            )
        else:
            self.etiqueta_estado_formulario.config(
                text="Estado: Pendiente",
                bg=COLORES["blanco"],
                fg=COLORES["rosa_oscuro"],
            )

        for variable in (
            self.precio_var,
            self.adelanto_var,
        ):
            variable.trace_add("write", self._actualizar_resumen_formulario)
        self._actualizar_resumen_formulario()

        botones = tk.Frame(formulario, bg=COLORES["superficie"])
        botones.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(5, 0),
        )
        self._crear_boton(
            botones,
            "Volver a pedidos",
            self.mostrar_pedidos,
            tipo="contorno",
        ).pack(side="left")
        self._crear_boton(
            botones,
            "Guardar cambios" if pedido is not None else "Guardar pedido",
            lambda: self._guardar_formulario(pedido),
            tipo="primario",
        ).pack(side="right")

    def _adaptar_formulario(self, evento=None):
        if (
            not self.formulario_cuerpo
            or not self.formulario_izquierdo
            or not self.formulario_resumen
        ):
            return
        try:
            if not all(
                widget.winfo_exists()
                for widget in (
                    self.formulario_cuerpo,
                    self.formulario_izquierdo,
                    self.formulario_resumen,
                )
            ):
                return
        except tk.TclError:
            return

        ancho = evento.width if evento is not None else self.formulario_cuerpo.winfo_width()
        if ancho < 720:
            self.formulario_izquierdo.pack_configure(
                side="top",
                fill="x",
                expand=False,
                padx=0,
            )
            self.formulario_resumen.pack_configure(
                side="top",
                fill="x",
                padx=0,
                pady=(18, 0),
            )
        else:
            self.formulario_izquierdo.pack_configure(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 28),
            )
            self.formulario_resumen.pack_configure(
                side="top",
                fill="y",
                padx=0,
                pady=0,
            )

    def _campo_formulario(
        self,
        padre,
        fila,
        columna,
        titulo,
        variable,
        obligatorio=False,
        ayuda=None,
        ancho_columna=1,
    ):
        marco = tk.Frame(padre, bg=COLORES["superficie"])
        marco.grid(
            row=fila,
            column=columna,
            columnspan=ancho_columna,
            sticky="new",
            padx=(0, 22) if columna == 0 else (22, 0),
            pady=(0, 17),
        )
        texto_titulo = f"{titulo} *" if obligatorio else titulo
        tk.Label(
            marco,
            text=texto_titulo,
            bg=COLORES["superficie"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 9, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 6))
        ttk.Entry(
            marco,
            textvariable=variable,
            style="Modern.TEntry",
            width=26,
        ).pack(fill="x")
        if ayuda:
            tk.Label(
                marco,
                text=ayuda,
                bg=COLORES["superficie"],
                fg=COLORES["texto_suave"],
                font=(self.familia_fuente, 8),
                anchor="w",
            ).pack(anchor="w", pady=(4, 0))

    def _linea_resumen(self, padre, titulo, variable, destacado=False):
        fila = tk.Frame(padre, bg=COLORES["rosa_suave"])
        fila.pack(fill="x", padx=22, pady=5)
        tk.Label(
            fila,
            text=titulo,
            bg=COLORES["rosa_suave"],
            fg=COLORES["rosa_oscuro"],
            font=(self.familia_fuente, 9, "bold" if destacado else "normal"),
            anchor="w",
        ).pack(side="left")
        tk.Label(
            fila,
            textvariable=variable,
            bg=COLORES["rosa_suave"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 11 if destacado else 10, "bold"),
            anchor="e",
        ).pack(side="right")

    def _actualizar_resumen_formulario(self, *_):
        try:
            total = float(self.precio_var.get().strip().replace(",", "."))
            adelanto = float(self.adelanto_var.get().strip().replace(",", "."))
        except (AttributeError, ValueError):
            total = 0
            adelanto = 0
        adelanto = 0 if not math.isfinite(adelanto) else adelanto
        total = 0 if not math.isfinite(total) else total
        self.resumen_total_var.set(self._dinero(total))
        self.resumen_adelanto_var.set(self._dinero(adelanto))
        self.resumen_saldo_var.set(self._dinero(max(total - adelanto, 0)))

    def _guardar_formulario(self, pedido):
        cliente = self.cliente_var.get().strip()
        telefono = self.telefono_var.get().strip()
        producto = self.producto_var.get().strip()
        fecha_entrega = str(self.entrada_fecha.get()).strip()

        if not cliente or not producto:
            messagebox.showwarning(
                "Datos incompletos",
                "Ingresa el nombre del cliente y el producto.",
                parent=self,
            )
            return

        try:
            precio_total = float(self.precio_var.get().strip().replace(",", "."))
            adelanto = float(self.adelanto_var.get().strip().replace(",", "."))
            if not math.isfinite(precio_total) or not math.isfinite(adelanto):
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Importes incorrectos",
                "El precio y el adelanto deben ser números válidos.",
                parent=self,
            )
            return

        if precio_total <= 0:
            messagebox.showerror(
                "Precio incorrecto",
                "El precio total debe ser mayor que cero.",
                parent=self,
            )
            return
        if adelanto < 0 or adelanto > precio_total:
            messagebox.showerror(
                "Adelanto incorrecto",
                "El adelanto debe estar entre cero y el precio total.",
                parent=self,
            )
            return
        try:
            fecha = datetime.strptime(fecha_entrega, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Fecha incorrecta",
                "Selecciona una fecha de entrega válida.",
                parent=self,
            )
            return

        try:
            if pedido is None:
                pedido_id = insertar_pedido(
                    cliente,
                    telefono,
                    producto,
                    precio_total,
                    adelanto,
                    fecha_entrega,
                )
                accion = "guardado"
            else:
                pedido_id = pedido[0]
                actualizar_pedido(
                    pedido_id,
                    cliente,
                    telefono,
                    producto,
                    precio_total,
                    adelanto,
                    fecha_entrega,
                )
                accion = "actualizado"
        except sqlite3.Error as error:
            messagebox.showerror(
                "No se pudo guardar",
                f"Ocurrió un error al guardar el pedido:\n{error}",
                parent=self,
            )
            return

        saldo = precio_total - adelanto
        messagebox.showinfo(
            "Pedido guardado" if pedido is None else "Pedido actualizado",
            f"Pedido #{pedido_id} {accion} correctamente.\n"
            f"Saldo pendiente: {self._dinero(saldo)}",
            parent=self,
        )
        self.mostrar_pedidos()

    # ------------------------------------------------------------------
    # Calendario
    # ------------------------------------------------------------------
    def mostrar_calendario(self):
        self._activar_menu("calendario")
        self._configurar_pagina(
            "Planificación",
            "Calendario",
            "Mira tus entregas y encuentra rápido el siguiente compromiso.",
        )
        self._limpiar_contenido()
        self.pedidos_calendario = self._leer_pedidos()

        tarjeta = self._crear_tarjeta(
            self.contenido,
            fill="both",
            expand=True,
        )
        izquierda = tk.Frame(tarjeta, bg=COLORES["superficie"])
        izquierda.pack(side="left", fill="both", expand=True, padx=25, pady=24)
        derecha = tk.Frame(tarjeta, bg=COLORES["superficie"], width=310)
        derecha.pack(side="right", fill="y", padx=(0, 25), pady=24)
        derecha.pack_propagate(False)

        tk.Label(
            izquierda,
            text="Entregas programadas",
            bg=COLORES["superficie"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 13, "bold"),
        ).pack(anchor="w", pady=(0, 14))
        self.calendario = Calendar(
            izquierda,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            background=COLORES["superficie"],
            foreground=COLORES["texto"],
            bordercolor=COLORES["borde"],
            headersbackground=COLORES["encabezado"],
            headersforeground=COLORES["texto_suave"],
            selectbackground=COLORES["rosa"],
            selectforeground=COLORES["blanco"],
            normalbackground=COLORES["superficie"],
            normalforeground=COLORES["texto"],
            weekendbackground=COLORES["rosa_suave"],
            weekendforeground=COLORES["rosa_oscuro"],
            othermonthbackground=COLORES["superficie_suave"],
            othermonthforeground=COLORES["texto_suave"],
            othermonthwebackground=COLORES["superficie_suave"],
            othermonthweforeground=COLORES["texto_suave"],
            titlebackground=COLORES["sidebar"],
            titleforeground=COLORES["blanco"],
            font=(self.familia_fuente, 10),
            headersfont=(self.familia_fuente, 9, "bold"),
            selectfont=(self.familia_fuente, 10, "bold"),
        )
        self.calendario.pack(anchor="n")
        self.calendario.tag_config(
            "pedido",
            background=COLORES["rosa"],
            foreground=COLORES["blanco"],
            font=(self.familia_fuente, 8, "bold"),
        )
        for pedido in self.pedidos_calendario:
            try:
                fecha = datetime.strptime(pedido[6], "%Y-%m-%d").date()
            except (TypeError, ValueError):
                continue
            self.calendario.calevent_create(
                fecha,
                f"#{pedido[0]} · {pedido[1]}",
                "pedido",
            )
        self.calendario.bind("<<CalendarSelected>>", self._al_seleccionar_fecha)

        leyenda = tk.Frame(izquierda, bg=COLORES["superficie"])
        leyenda.pack(anchor="w", pady=(18, 0))
        tk.Label(
            leyenda,
            text="●",
            bg=COLORES["rosa"],
            fg=COLORES["rosa"],
            font=(self.familia_fuente, 10),
        ).pack(side="left", padx=(0, 6))
        tk.Label(
            leyenda,
            text="Pedido con entrega programada",
            bg=COLORES["superficie"],
            fg=COLORES["texto_suave"],
            font=(self.familia_fuente, 9),
        ).pack(side="left")

        tk.Label(
            derecha,
            text="Detalle del día",
            bg=COLORES["superficie"],
            fg=COLORES["texto"],
            font=(self.familia_fuente, 13, "bold"),
        ).pack(anchor="w")
        self.etiqueta_fecha_detalle = tk.Label(
            derecha,
            text="",
            bg=COLORES["superficie"],
            fg=COLORES["rosa_oscuro"],
            font=(self.familia_fuente, 9, "bold"),
        )
        self.etiqueta_fecha_detalle.pack(anchor="w", pady=(4, 15))
        self.detalles_canvas = tk.Canvas(
            derecha,
            bg=COLORES["superficie_suave"],
            highlightthickness=0,
            bd=0,
        )
        self.detalles_canvas.pack(side="left", fill="both", expand=True)
        self.detalles_scroll = ttk.Scrollbar(
            derecha,
            orient="vertical",
            command=self.detalles_canvas.yview,
            style="Soft.Vertical.TScrollbar",
        )
        self.detalles_scroll.pack(side="right", fill="y", padx=(5, 0))
        self.detalles_canvas.configure(yscrollcommand=self.detalles_scroll.set)
        self.marco_detalles = tk.Frame(
            self.detalles_canvas,
            bg=COLORES["superficie_suave"],
        )
        self.detalles_window = self.detalles_canvas.create_window(
            (0, 0),
            window=self.marco_detalles,
            anchor="nw",
        )
        self.marco_detalles.bind(
            "<Configure>",
            self._configurar_scroll_detalles,
        )
        self.detalles_canvas.bind(
            "<Configure>",
            self._ajustar_ancho_detalles,
        )
        self._actualizar_detalle_calendario(datetime.now().strftime("%Y-%m-%d"))

    def _configurar_scroll_detalles(self, _evento):
        if self.detalles_canvas is not None:
            self.detalles_canvas.configure(
                scrollregion=self.detalles_canvas.bbox("all")
            )

    def _ajustar_ancho_detalles(self, evento):
        if self.detalles_canvas is not None:
            self.detalles_canvas.itemconfigure(
                self.detalles_window,
                width=evento.width,
            )

    def _al_seleccionar_fecha(self, _evento=None):
        if self.calendario is not None:
            self._actualizar_detalle_calendario(self.calendario.get_date())

    def _actualizar_detalle_calendario(self, fecha):
        if self.marco_detalles is None:
            return
        try:
            if not self.marco_detalles.winfo_exists():
                return
        except tk.TclError:
            return
        for hijo in self.marco_detalles.winfo_children():
            hijo.destroy()
        fecha_legible = self._fecha_larga(fecha)
        self.etiqueta_fecha_detalle.config(text=fecha_legible.capitalize())

        pedidos_dia = [
            pedido for pedido in self.pedidos_calendario if pedido[6] == fecha
        ]
        if not pedidos_dia:
            marco = tk.Frame(self.marco_detalles, bg=COLORES["superficie_suave"])
            marco.pack(fill="both", expand=True, padx=15, pady=18)
            tk.Label(
                marco,
                text="♡",
                bg=COLORES["superficie_suave"],
                fg=COLORES["rosa"],
                font=(self.familia_fuente, 24, "bold"),
            ).pack(pady=(15, 1))
            tk.Label(
                marco,
                text="Día libre",
                bg=COLORES["superficie_suave"],
                fg=COLORES["texto"],
                font=(self.familia_fuente, 10, "bold"),
            ).pack()
            tk.Label(
                marco,
                text="No hay entregas programadas.",
                bg=COLORES["superficie_suave"],
                fg=COLORES["texto_suave"],
                font=(self.familia_fuente, 8),
            ).pack(pady=(4, 15))
            return

        for pedido in pedidos_dia:
            item = tk.Frame(self.marco_detalles, bg=COLORES["superficie"])
            item.pack(fill="x", padx=10, pady=7)
            tk.Label(
                item,
                text=f"#{pedido[0]}",
                bg=COLORES["rosa_suave"],
                fg=COLORES["rosa_oscuro"],
                font=(self.familia_fuente, 9, "bold"),
                padx=8,
                pady=4,
            ).pack(side="left", anchor="n")
            datos = tk.Frame(item, bg=COLORES["superficie"])
            datos.pack(side="left", fill="x", expand=True, padx=9)
            tk.Label(
                datos,
                text=pedido[1],
                bg=COLORES["superficie"],
                fg=COLORES["texto"],
                font=(self.familia_fuente, 9, "bold"),
                anchor="w",
            ).pack(anchor="w")
            tk.Label(
                datos,
                text=pedido[2],
                bg=COLORES["superficie"],
                fg=COLORES["texto_suave"],
                font=(self.familia_fuente, 8),
                anchor="w",
                wraplength=190,
                justify="left",
            ).pack(anchor="w", pady=(3, 0))
            tk.Label(
                datos,
                text=f"Estado: {pedido[7]}",
                bg=COLORES["superficie"],
                fg=COLORES["rosa_oscuro"],
                font=(self.familia_fuente, 8, "bold"),
                anchor="w",
            ).pack(anchor="w", pady=(4, 0))


def main():
    crear_base_datos()
    aplicacion = CrochetApp()
    aplicacion.mainloop()


if __name__ == "__main__":
    main()
