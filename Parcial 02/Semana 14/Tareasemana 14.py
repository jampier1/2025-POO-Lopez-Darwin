import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class AgendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agenda Personal")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Frame lista de eventos
        self.frame_lista = ttk.Frame(root, padding=10)
        self.frame_lista.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            self.frame_lista,
            columns=("fecha", "hora", "descripcion"),
            show="headings",
            height=10
        )
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.column("fecha", width=150, anchor=tk.CENTER)
        self.tree.column("hora", width=100, anchor=tk.CENTER)
        self.tree.column("descripcion", width=600, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar corregido
        scrollbar = ttk.Scrollbar(self.frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame de entrada de datos
        self.frame_entrada = ttk.Frame(root, padding=10)
        self.frame_entrada.pack(fill=tk.X)

        ttk.Label(self.frame_entrada, text="Fecha:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)

        # Definición de years, months y days
        current_year = datetime.datetime.now().year
        years = [str(y) for y in range(current_year, current_year + 10)]
        months = [str(m).zfill(2) for m in range(1, 13)]
        days = [str(d).zfill(2) for d in range(1, 32)]

        self.year_cb = ttk.Combobox(self.frame_entrada, values=years, width=6, state="readonly")
        self.year_cb.current(0)
        self.year_cb.grid(row=0, column=1, padx=2, pady=5)

        self.month_cb = ttk.Combobox(self.frame_entrada, values=months, width=4, state="readonly")
        self.month_cb.current(0)
        self.month_cb.grid(row=0, column=2, padx=2, pady=5)

        self.day_cb = ttk.Combobox(self.frame_entrada, values=days, width=4, state="readonly")
        self.day_cb.current(0)
        self.day_cb.grid(row=0, column=3, padx=2, pady=5)

        ttk.Label(self.frame_entrada, text="Hora (HH:MM):").grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        self.entry_hora = ttk.Entry(self.frame_entrada, width=10)
        self.entry_hora.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(self.frame_entrada, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.entry_descripcion = ttk.Entry(self.frame_entrada, width=70)
        self.entry_descripcion.grid(row=1, column=1, columnspan=5, padx=5, pady=5, sticky=tk.W)

        # Frame de botones
        self.frame_botones = ttk.Frame(root, padding=10)
        self.frame_botones.pack(fill=tk.X)

        self.btn_agregar = ttk.Button(self.frame_botones, text="Agregar Evento", command=self.agregar_evento)
        self.btn_agregar.pack(side=tk.LEFT, padx=5)

        self.btn_eliminar = ttk.Button(self.frame_botones, text="Eliminar Evento Seleccionado", command=self.eliminar_evento)
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)

        self.btn_salir = ttk.Button(self.frame_botones, text="Salir", command=root.quit)
        self.btn_salir.pack(side=tk.RIGHT, padx=5)

    def agregar_evento(self):
        year = self.year_cb.get()
        month = self.month_cb.get()
        day = self.day_cb.get()
        try:
            fecha_obj = datetime.date(int(year), int(month), int(day))
            fecha = fecha_obj.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Fecha inválida", "La fecha seleccionada no es válida.")
            return

        hora = self.entry_hora.get().strip()
        descripcion = self.entry_descripcion.get().strip()

        if not hora or not descripcion:
            messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos.")
            return

        try:
            datetime.datetime.strptime(hora, "%H:%M")
        except ValueError:
            messagebox.showerror("Formato de hora inválido", "La hora debe tener el formato HH:MM (24 horas).")
            return

        self.tree.insert("", tk.END, values=(fecha, hora, descripcion))

        self.entry_hora.delete(0, tk.END)
        self.entry_descripcion.delete(0, tk.END)

    def eliminar_evento(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showinfo("Sin selección", "Por favor, seleccione un evento para eliminar.")
            return

        respuesta = messagebox.askyesno("Confirmar eliminación", "¿Está seguro que desea eliminar el evento seleccionado?")
        if respuesta:
            for item in seleccionado:
                self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = AgendaApp(root)
    root.mainloop()
