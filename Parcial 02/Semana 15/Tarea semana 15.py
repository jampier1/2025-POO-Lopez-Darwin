import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from tkcalendar import DateEntry
from datetime import datetime, date

TASKS_FILE = "tasks.json"

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lista de Tareas - Tkinter")
        self.geometry("900x520")
        self.resizable(True, True)

        self.tasks = []

        # Fuentes
        default_family = "Helvetica"
        default_size = 11
        self.font_normal = tkfont.Font(family=default_family, size=default_size)
        self.font_completed = tkfont.Font(family=default_family, size=default_size, overstrike=True)

        # --- PANEL SUPERIOR ---
        top_frame = tk.Frame(self, pady=8, padx=8)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="Tarea:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_task = tk.Entry(top_frame, font=self.font_normal, width=30)
        self.entry_task.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_task.bind('<Return>', lambda e: self.add_task())

        tk.Label(top_frame, text="Fecha entrega:").pack(side=tk.LEFT, padx=(6, 4))
        self.entry_due_date = DateEntry(
            top_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-MM-dd'
        )
        self.entry_due_date.pack(side=tk.LEFT, padx=(0, 6))

        tk.Label(top_frame, text="Hora entrega:").pack(side=tk.LEFT, padx=(0, 4))
        times = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
        self.entry_due_time = ttk.Combobox(top_frame, values=times, width=6, state="normal")
        self.entry_due_time.set("12:00")
        self.entry_due_time.pack(side=tk.LEFT, padx=(0, 6))

        btn_add = tk.Button(top_frame, text="Añadir Tarea", command=self.add_task)
        btn_add.pack(side=tk.LEFT, padx=(6, 0))

        # --- TREEVIEW ---
        table_frame = tk.Frame(self, pady=4, padx=8)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("task", "added", "due", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("task", text="Tarea")
        self.tree.heading("added", text="Añadida")
        self.tree.heading("due", text="Entrega")
        self.tree.heading("status", text="Estado")

        self.tree.column("task", width=350)
        self.tree.column("added", width=150)
        self.tree.column("due", width=150)
        self.tree.column("status", width=80, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(table_frame, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)

        self.tree.tag_configure('completed', foreground='#6e6e6e')
        self.tree.bind("<Double-1>", lambda e: self.toggle_selected_completed())

        # --- BOTONES INFERIORES ---
        bottom_frame = tk.Frame(self, pady=8, padx=8)
        bottom_frame.pack(fill=tk.X)

        tk.Button(bottom_frame, text="Marcar como Completada", command=self.toggle_selected_completed).pack(side=tk.LEFT)
        tk.Button(bottom_frame, text="Eliminar Tarea", command=self.delete_task).pack(side=tk.LEFT, padx=6)
        tk.Button(bottom_frame, text="Editar Tarea", command=self.edit_task).pack(side=tk.LEFT, padx=6)
        tk.Button(bottom_frame, text="Eliminar Completadas", command=self.clear_completed).pack(side=tk.LEFT, padx=6)
        tk.Button(bottom_frame, text="Guardar", command=self.save_tasks).pack(side=tk.RIGHT)
        tk.Button(bottom_frame, text="Cargar", command=self.load_tasks).pack(side=tk.RIGHT, padx=(6, 0))

        help_label = tk.Label(self, text="Enter = añadir · Doble clic = completar/descompletar · Supr = eliminar seleccionada")
        help_label.pack(pady=(0, 8))

        self.bind("<Delete>", lambda e: self.delete_task())

        try:
            self.entry_due_date.set_date(date.today())
        except Exception:
            pass

        self.load_tasks()

    # ---------- Manejo de errores ----------
    def safe_call(self, func, *args, **kwargs):
        """Ejecuta función con manejo de errores, evita cierre inesperado."""
        try:
            func(*args, **kwargs)
        except Exception as e:
            with open("error.log", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - {repr(e)}\n")
            messagebox.showerror("Error", "Ha ocurrido un error. Revisa error.log para más detalles.")

    # ---------- FUNCIONES PRINCIPALES ----------
    def add_task(self):
        self.safe_call(self._add_task)

    def _add_task(self):
        text = self.entry_task.get().strip()
        if not text:
            messagebox.showwarning("Entrada vacía", "Escribe una tarea antes de añadirla.")
            return

        added_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        due_date_str = self.entry_due_date.get().strip() or date.today().isoformat()
        due_time = self.entry_due_time.get().strip() or "12:00"

        task = {
            "text": text,
            "completed": False,
            "added": added_time,
            "due_date": due_date_str,
            "due_time": due_time
        }
        self.tasks.append(task)
        self.refresh_table(select_index=len(self.tasks)-1)
        self.clear_inputs()
        self.entry_task.focus_set()

    def clear_inputs(self):
        self.safe_call(self._clear_inputs)

    def _clear_inputs(self):
        self.entry_task.delete(0, tk.END)
        self.entry_due_date.set_date(date.today())
        self.entry_due_time.set("12:00")

    def toggle_selected_completed(self):
        self.safe_call(self._toggle_selected_completed)

    def _toggle_selected_completed(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona una tarea", "Selecciona una tarea para marcarla.")
            return
        index = self.tree.index(sel[0])
        self.tasks[index]['completed'] = not self.tasks[index]['completed']
        self.refresh_table(select_index=index)

    def delete_task(self):
        self.safe_call(self._delete_task)

    def _delete_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona una tarea", "Selecciona la tarea que quieres eliminar.")
            return
        index = self.tree.index(sel[0])
        task_text = self.tasks[index]['text']
        if messagebox.askyesno("Confirmar eliminación", f"¿Eliminar la tarea:\n\n{task_text}?"):
            self.tasks.pop(index)
            new_index = index if index < len(self.tasks) else (len(self.tasks)-1 if self.tasks else None)
            self.refresh_table(select_index=new_index)

    def clear_completed(self):
        self.safe_call(self._clear_completed)

    def _clear_completed(self):
        if not any(t['completed'] for t in self.tasks):
            messagebox.showinfo("No hay tareas", "No hay tareas completadas para eliminar.")
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar todas las tareas completadas?"):
            self.tasks = [t for t in self.tasks if not t['completed']]
            self.refresh_table()

    def edit_task(self):
        self.safe_call(self._edit_task)

    def _edit_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona una tarea", "Selecciona la tarea que quieres editar.")
            return
        index = self.tree.index(sel[0])
        task = self.tasks[index]

        self.entry_task.delete(0, tk.END)
        self.entry_task.insert(0, task['text'])

        try:
            self.entry_due_date.set_date(date.fromisoformat(task['due_date']))
        except Exception:
            self.entry_due_date.set_date(date.today())

        self.entry_due_time.set(task.get('due_time', '12:00'))
        self.tasks.pop(index)
        self.refresh_table()
        messagebox.showinfo("Modo Edición", "Edita los campos y presiona 'Añadir Tarea' para guardar cambios.")

    def refresh_table(self, select_index=None):
        self.safe_call(self._refresh_table, select_index)

    def _refresh_table(self, select_index=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for task in self.tasks:
            status = "✔️" if task['completed'] else "Pendiente"
            due_text = f"{task.get('due_date','')} {task.get('due_time','')}"
            tags = ('completed',) if task['completed'] else ()
            self.tree.insert("", tk.END, values=(task['text'], task['added'], due_text, status), tags=tags)

        if select_index is not None and self.tasks:
            children = self.tree.get_children()
            if 0 <= select_index < len(children):
                iid = children[select_index]
                self.tree.selection_set(iid)
                self.tree.focus(iid)

    # ---------- Persistencia ----------
    def save_tasks(self):
        self.safe_call(self._save_tasks)

    def _save_tasks(self):
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Guardado", f"Tareas guardadas en {TASKS_FILE}.")

    def load_tasks(self):
        self.safe_call(self._load_tasks)

    def _load_tasks(self):
        if not os.path.exists(TASKS_FILE):
            return
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        cleaned = []
        for t in loaded:
            text = t.get('text','').strip()
            if not text:
                continue
            cleaned.append({
                'text': text,
                'completed': bool(t.get('completed', False)),
                'added': t.get('added', datetime.now().strftime("%Y-%m-%d %H:%M")),
                'due_date': t.get('due_date', date.today().isoformat()),
                'due_time': t.get('due_time', '12:00')
            })
        self.tasks = cleaned
        self.refresh_table()


if __name__ == '__main__':
    app = TodoApp()
    app.mainloop()
