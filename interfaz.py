import tkinter as tk
from tkinter import ttk, messagebox
from pedidos import (crear_base_datos, insertar_pedido, obtener_pedidos, actualizar_estado)
from tkcalendar import DateEntry, Calendar
from datetime import datetime

def limpiar_cuerpo():
    for elemento in cuerpo.winfo_children():
        elemento.destroy()
def mostrar_inicio():
    titulo.config(text="INICIO")
    limpiar_cuerpo()
    mensaje = ttk.Label(
        cuerpo,
        text="Bienvenido al gestor de pedidos de crochet"
    )
    mensaje.pack(pady=30)

def mostrar_pedidos():
    titulo.config(text="PEDIDOS")
    limpiar_cuerpo()

    columnas = (
        "id",
        "cliente",
        "producto",
        "total",
        "adelanto",
        "saldo",
        "entrega",
        "estado"
    )

    tabla = ttk.Treeview(
        cuerpo,
        columns=columnas,
        show="headings"
    )

    tabla.heading("id", text="ID")
    tabla.heading("cliente", text="Cliente")
    tabla.heading("producto", text="Producto")
    tabla.heading("total", text="Total")
    tabla.heading("adelanto", text="Adelanto")
    tabla.heading("saldo", text="Saldo")
    tabla.heading("entrega", text="Entrega")
    tabla.heading("estado", text="Estado")

    tabla.column("id", width=50, anchor="center")
    tabla.column("cliente", width=150)
    tabla.column("producto", width=150)
    tabla.column("total", width=80, anchor="center")
    tabla.column("adelanto", width=80, anchor="center")
    tabla.column("saldo", width=80, anchor="center")
    tabla.column("entrega", width=100, anchor="center")
    tabla.column("estado", width=100, anchor="center")

    for pedido in obtener_pedidos():
        tabla.insert("", "end", values=pedido)

    tabla.pack(fill="both", expand=True)  
    def cambiar_estado():
        seleccion = tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Sin selección",
                "Selecciona un pedido de la tabla."
            )
            return

        valores = tabla.item(seleccion[0], "values")
        pedido_id = valores[0]

        actualizar_estado(
            pedido_id,
            estado_var.get()
        )

        mostrar_pedidos()

    marco_estado = ttk.Frame(cuerpo)
    marco_estado.pack(pady=15)

    etiqueta_estado = ttk.Label(
        marco_estado,
        text="Nuevo estado:"
    )
    etiqueta_estado.pack(side="left", padx=5)

    estado_var = tk.StringVar(value="Pendiente")

    selector_estado = ttk.Combobox(
        marco_estado,
        textvariable=estado_var,
        values=(
            "Pendiente",
            "En proceso",
            "Terminado",
            "Entregado"
        ),
        state="readonly",
        width=15
    )
    selector_estado.pack(side="left", padx=5)

    boton_actualizar = ttk.Button(
        marco_estado,
        text="Actualizar estado",
        command=cambiar_estado
    )
    boton_actualizar.pack(side="left", padx=5)

def mostrar_calendario():
    titulo.config(text="CALENDARIO")
    limpiar_cuerpo()

    pedidos = obtener_pedidos()

    calendario = Calendar(
        cuerpo,
        selectmode="day",
        date_pattern="yyyy-mm-dd"
    )
    calendario.pack(pady=40)

    for pedido in pedidos:
        fecha_texto = pedido[6]

        try:
            fecha = datetime.strptime(
                fecha_texto,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            continue

        calendario.calevent_create(
            fecha,
            f"#{pedido[0]} - {pedido[1]}: {pedido[2]}",
            "pedido"
        )

    calendario.tag_config(
        "pedido",
        background="#4f46e5",
        foreground="white"
    )

    detalle = ttk.Label(
        cuerpo,
        text="Selecciona una fecha para ver sus pedidos.",
        justify="left"
    )
    detalle.pack(pady=10)

    def mostrar_pedidos_del_dia(event=None):
        fecha_seleccionada = calendario.get_date()

        pedidos_del_dia = [
            pedido
            for pedido in pedidos
            if pedido[6] == fecha_seleccionada
        ]

        if not pedidos_del_dia:
            detalle.config(
                text="No hay pedidos para esta fecha."
            )
            return

        texto = ""

        for pedido in pedidos_del_dia:
            texto += (
                f"Pedido #{pedido[0]}\n"
                f"Cliente: {pedido[1]}\n"
                f"Producto: {pedido[2]}\n"
                f"Estado: {pedido[7]}\n\n"
            )

        detalle.config(text=texto)

    calendario.bind(
        "<<CalendarSelected>>",
        mostrar_pedidos_del_dia
    )

def mostrar_nuevos_pedidos():
    titulo.config(text="NUEVO PEDIDO")
    limpiar_cuerpo()
    def guardar_pedido():
        cliente = entrada_cliente.get().strip()
        telefono = entrada_telefono.get().strip()
        producto = entrada_producto.get().strip()
        precio_total = entrada_precio_total.get().strip()
        adelanto = entrada_adelanto.get().strip()
        fecha_entrega = entrada_fecha_entrega.get().strip()

        if cliente == "" or producto == "":
            messagebox.showwarning(
                "Datos incompletos",
                "Debes ingresar el cliente y el producto."
            )
            return
        try:
            precio_total = float(precio_total.replace(",", "."))
            adelanto = float(adelanto.replace(",", "."))
        except ValueError:
            messagebox.showerror(
                "Importe incorrecto",
                "El precio total y el adelanto deben ser números."
            )
            return

        if precio_total <= 0:
            messagebox.showerror(
                "Precio incorrecto",
                "El precio total debe ser mayor que cero."
            )
            return

        if adelanto < 0 or adelanto > precio_total:
            messagebox.showerror(
                "Adelanto incorrecto",
                "El adelanto debe estar entre cero y el precio total."
            )
            return

        saldo = precio_total - adelanto
        pedido_id = insertar_pedido(
            cliente,
            telefono,
            producto,
            precio_total,
            adelanto,
            fecha_entrega
        )
        print("Cliente:", cliente)
        print("Teléfono:", telefono)
        print("Producto:", producto)
        print("Precio total:", precio_total)
        print("Adelanto:", adelanto)
        print("Fecha de entrega:", fecha_entrega)
        print("Saldo pendiente:", saldo)

        messagebox.showinfo(
            "Pedido guardado",
            f"Pedido #{pedido_id} guardado correctamente.\n"
            f"Saldo pendiente: S/ {saldo:.2f}"
        )
        mostrar_nuevos_pedidos()    

    etiqueta_cliente = ttk.Label(cuerpo, text="Nombre del cliente:")
    etiqueta_cliente.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )
    entrada_cliente = ttk.Entry(cuerpo, width=40)
    entrada_cliente.grid(row=0, column=1, padx=10, pady=10)

  

    etiqueta_telefono = ttk.Label(cuerpo, text="Teléfono:")
    etiqueta_telefono.grid(
        row=1,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    entrada_telefono = ttk.Entry(cuerpo, width=40)
    entrada_telefono.grid(row=1, column=1, padx=10, pady=10)

    etiqueta_producto = ttk.Label(cuerpo, text="Producto:")
    etiqueta_producto.grid(
        row=2,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    entrada_producto = ttk.Entry(cuerpo, width=40)
    entrada_producto.grid(row=2, column=1, padx=10, pady=10)


    etiqueta_precio_total = ttk.Label(cuerpo, text="Precio total:")
    etiqueta_precio_total.grid(
        row=3,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    entrada_precio_total = ttk.Entry(cuerpo, width=40)
    entrada_precio_total.grid(row=3, column=1, padx=10, pady=10)

    etiqueta_adelanto = ttk.Label(cuerpo, text="Adelanto:")
    etiqueta_adelanto.grid(
        row=4,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    entrada_adelanto = ttk.Entry(cuerpo, width=40)
    entrada_adelanto.grid(row=4, column=1, padx=10, pady=10)

    etiqueta_fecha_entrega = ttk.Label(
        cuerpo,
        text="Fecha de entrega:"
    )
    etiqueta_fecha_entrega.grid(
        row=5,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    entrada_fecha_entrega = DateEntry(
        cuerpo,
        width=37,
        date_pattern="yyyy-mm-dd"
    )
    entrada_fecha_entrega.grid(
        row=5,
        column=1,
        padx=10,
        pady=10
    )
    boton_guardar = ttk.Button(
            cuerpo,
            text="Guardar Pedido",
            command=guardar_pedido
        )
    boton_guardar.grid(
            row=6,  
            column=0,
            columnspan=2,
            pady=20
        )          
                
            
    crear_base_datos()
ventana = tk.Tk()
ventana.title("Gestión de pedidos de crochet")
ventana.geometry("900x600")

menu_lateral = ttk.Frame(ventana, padding=20)
menu_lateral.pack(side="left", fill="y")

contenido = ttk.Frame(ventana, padding=30)
contenido.pack(side="right", fill="both", expand=True)

titulo = ttk.Label(
    contenido,
    text="Gestión de pedidos",
    font=("Arial", 20)
)
titulo.pack(pady=20)

cuerpo = ttk.Frame(contenido)
cuerpo.pack(fill="both", expand=True)

boton_inicio = ttk.Button(
    menu_lateral,
    text="INICIO",
    command=mostrar_inicio
)
boton_inicio.pack(fill="x", pady=5)

boton_pedidos = ttk.Button(
    menu_lateral,
    text="PEDIDOS",
    command=mostrar_pedidos
)
boton_pedidos.pack(fill="x", pady=5)

boton_nuevos_pedidos = ttk.Button(
    menu_lateral,
    text="NUEVOS PEDIDOS",
    command=mostrar_nuevos_pedidos
)
boton_nuevos_pedidos.pack(fill="x", pady=5)

boton_calendario = ttk.Button(
    menu_lateral,
    text="CALENDARIO",
    command=mostrar_calendario
)
boton_calendario.pack(fill="x", pady=5)


ventana.mainloop()
