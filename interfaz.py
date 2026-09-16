import tkinter as tk
from tkinter import ttk, messagebox
from pedidos import crear_base_datos, insertar_pedido

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

def mostrar_calendario():
    titulo.config(text="CALENDARIO")
    limpiar_cuerpo()

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

    entrada_fecha_entrega = ttk.Entry(cuerpo, width=40)
    entrada_fecha_entrega.grid(row=5, column=1, padx=10, pady=10)

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
