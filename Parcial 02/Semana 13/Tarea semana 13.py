import tkinter as tk
from tkinter import messagebox

class GestorDatosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Datos")

        # Etiqueta para instrucción
        self.label = tk.Label(root, text="Ingrese un dato:")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Campo de texto para ingreso de datos
        self.entry = tk.Entry(root, width=40)
        self.entry.grid(row=0, column=1, padx=10, pady=10)

        # Botón Agregar
        self.btn_agregar = tk.Button(root, text="Agregar", command=self.agregar_dato)
        self.btn_agregar.grid(row=0, column=2, padx=10, pady=10)

        # Lista para mostrar datos
        self.lista_datos = tk.Listbox(root, width=60, height=10)
        self.lista_datos.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Botón Limpiar: borra todo (campo y lista)
        self.btn_limpiar = tk.Button(root, text="Limpiar", command=self.limpiar)
        self.btn_limpiar.grid(row=2, column=1, pady=10)

        # Botón Borrar Seleccionado: borra solo el dato seleccionado
        self.btn_borrar = tk.Button(root, text="Borrar Seleccionado", command=self.borrar_seleccionado)
        self.btn_borrar.grid(row=2, column=2, pady=10)

    def agregar_dato(self):
        dato = self.entry.get().strip()
        if dato:
            self.lista_datos.insert(tk.END, dato)
            self.entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Entrada vacía", "Por favor ingrese un dato antes de agregar.")

    def limpiar(self):
        # Limpiar campo de texto
        self.entry.delete(0, tk.END)
        # Limpiar lista de datos
        self.lista_datos.delete(0, tk.END)

    def borrar_seleccionado(self):
        seleccion = self.lista_datos.curselection()
        if seleccion:
            self.lista_datos.delete(seleccion[0])
        else:
            messagebox.showwarning("Ninguna selección", "Por favor seleccione un dato para borrar.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GestorDatosApp(root)
    root.mainloop()
