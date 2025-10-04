import json
import os
import threading
from datetime import datetime, date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import customtkinter as ctk
from plyer import notification  # Para notificaciones de escritorio

# Archivo de tareas y configuración
TASKS_FILE = "tasks.json"
CONFIG_FILE = "config.json"

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.options_window = None  # Para controlar ventana única
        self.load_config()
        self.title("GaiaNet")
        self.geometry("1000x600")
        self.minsize(850, 500)

        self.tasks = []
        self.font_normal = (self.config.get("font_family","Helvetica"), self.config.get("font_size",11))

        # --- FRAMES ---
        self.top_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.config.get("top_frame_color","#F0F0F0"))
        self.top_frame.pack(fill="x", padx=10, pady=10)

        self.middle_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.config.get("middle_frame_color","#FFFFFF"))
        self.middle_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self.bottom_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.config.get("bottom_frame_color","#F0F0F0"))
        self.bottom_frame.pack(fill="x", padx=10, pady=(0,10))

        # --- ENTRADAS ---
        ctk.CTkLabel(self.top_frame, text="Tarea:", font=self.font_normal).pack(side="left", padx=(0,5))
        self.entry_task = ctk.CTkEntry(self.top_frame, width=250, font=self.font_normal)
        self.entry_task.pack(side="left", padx=(0,10), fill="x", expand=True)
        self.entry_task.bind("<Return>", lambda e: self.add_task())

        ctk.CTkLabel(self.top_frame, text="Fecha:", font=self.font_normal).pack(side="left", padx=(0,5))
        self.entry_due_date = DateEntry(self.top_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-MM-dd')
        self.entry_due_date.pack(side="left", padx=(0,10))

        ctk.CTkLabel(self.top_frame, text="Hora:", font=self.font_normal).pack(side="left", padx=(0,5))
        times = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0,30)]
        self.entry_due_time = ctk.CTkComboBox(self.top_frame, values=times, width=70)
        self.entry_due_time.set("12:00")
        self.entry_due_time.pack(side="left", padx=(0,10))

        ctk.CTkButton(self.top_frame, text="Añadir Tarea", command=self.add_task).pack(side="left", padx=(10,0))
        ctk.CTkButton(self.top_frame, text="Opciones", command=self.open_settings).pack(side="left", padx=10)

        # --- TREEVIEW ---
        scroll_frame = ctk.CTkScrollableFrame(self.middle_frame)
        scroll_frame.pack(fill="both", expand=True)

        columns = ("task","added","due","status")
        self.tree = ttk.Treeview(scroll_frame, columns=columns, show="headings", selectmode="browse", height=18)
        self.tree.heading("task", text="Tarea")
        self.tree.heading("added", text="Agregada")
        self.tree.heading("due", text="Vence")
        self.tree.heading("status", text="Estado")
        self.tree.column("task", width=400)
        self.tree.column("added", width=150)
        self.tree.column("due", width=150)
        self.tree.column("status", width=80, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.tag_configure("completed", foreground="#6e6e6e")
        self.tree.bind("<Double-1>", lambda e: self.toggle_selected_completed())

        # --- BOTONES INFERIORES ---
        self.btn_complete = ctk.CTkButton(self.bottom_frame, text="Marcar Completada", command=self.toggle_selected_completed)
        self.btn_complete.pack(side="left", padx=5)
        self.btn_edit = ctk.CTkButton(self.bottom_frame, text="Editar Tarea", command=self.edit_task)
        self.btn_edit.pack(side="left", padx=5)
        self.btn_delete = ctk.CTkButton(self.bottom_frame, text="Eliminar Tarea", command=self.delete_task)
        self.btn_delete.pack(side="left", padx=5)
        self.btn_clear = ctk.CTkButton(self.bottom_frame, text="Eliminar Completadas", command=self.clear_completed)
        self.btn_clear.pack(side="left", padx=5)
        self.btn_save = ctk.CTkButton(self.bottom_frame, text="Guardar", command=self.save_tasks)
        self.btn_save.pack(side="right", padx=5)
        self.btn_load = ctk.CTkButton(self.bottom_frame, text="Cargar", command=self.load_tasks)
        self.btn_load.pack(side="right", padx=5)

        ctk.CTkLabel(self, text="Enter = añadir · Doble clic = completar/descompletar · Supr = eliminar seleccionada · Flechas = navegar · C = completar · E = editar", font=("Helvetica", 9)).pack(side="bottom", pady=(0,5))

        self.entry_due_date.set_date(date.today())
        self.load_tasks()
        threading.Thread(target=self.notification_loop, daemon=True).start()

        # --- ATALLOS DE TECLADO ---
        self.bind_all("<Delete>", lambda e: self.delete_task())
        self.bind_all("<Return>", lambda e: self.add_task())
        self.bind_all("<c>", lambda e: self.toggle_selected_completed())
        self.bind_all("<C>", lambda e: self.toggle_selected_completed())
        self.bind_all("<e>", lambda e: self.edit_task())
        self.bind_all("<E>", lambda e: self.edit_task())
        self.bind_all("<Escape>", lambda e: self.close_options_or_app())
        self.bind_all("<Up>", lambda e: self.select_prev_task())
        self.bind_all("<Down>", lambda e: self.select_next_task())
        self.bind_all("<Control-s>", lambda e: self.save_tasks())
        self.bind_all("<Control-l>", lambda e: self.load_tasks())
        self.bind_all("<Control-Delete>", lambda e: self.clear_completed())

    # ---------- CONFIG ----------
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE,"r",encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {"theme":"System","font_family":"Helvetica","font_size":11,
                           "top_frame_color":"#F0F0F0","middle_frame_color":"#FFFFFF","bottom_frame_color":"#F0F0F0"}

    def save_config(self):
        with open(CONFIG_FILE,"w",encoding="utf-8") as f:
            json.dump(self.config,f,ensure_ascii=False,indent=2)

    def open_settings(self):
        if self.options_window and tk.Toplevel.winfo_exists(self.options_window):
            self.options_window.lift()
            return

        win = ctk.CTkToplevel(self)
        self.options_window = win
        win.title("Opciones")
        win.geometry("400x400")

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll, text="Tema (Light/Dark/System)").pack(pady=5)
        theme_combo = ctk.CTkComboBox(scroll, values=["Light","Dark","System"])
        theme_combo.set(self.config.get("theme","System"))
        theme_combo.pack(pady=5)

        ctk.CTkLabel(scroll, text="Colores de secciones").pack(pady=5)
        top_color = ctk.CTkEntry(scroll)
        top_color.insert(0,self.config.get("top_frame_color","#F0F0F0"))
        top_color.pack(pady=5)
        mid_color = ctk.CTkEntry(scroll)
        mid_color.insert(0,self.config.get("middle_frame_color","#FFFFFF"))
        mid_color.pack(pady=5)
        bot_color = ctk.CTkEntry(scroll)
        bot_color.insert(0,self.config.get("bottom_frame_color","#F0F0F0"))
        bot_color.pack(pady=5)

        ctk.CTkLabel(scroll, text="Fuente").pack(pady=5)
        font_entry = ctk.CTkEntry(scroll)
        font_entry.insert(0,self.config.get("font_family","Helvetica"))
        font_entry.pack(pady=5)

        ctk.CTkLabel(scroll, text="Tamaño Fuente").pack(pady=5)
        size_entry = ctk.CTkEntry(scroll)
        size_entry.insert(0,str(self.config.get("font_size",11)))
        size_entry.pack(pady=5)

        def apply_settings():
            self.config["theme"] = theme_combo.get()
            ctk.set_appearance_mode(self.config["theme"])
            self.config["top_frame_color"] = top_color.get()
            self.config["middle_frame_color"] = mid_color.get()
            self.config["bottom_frame_color"] = bot_color.get()
            self.config["font_family"] = font_entry.get()
            self.config["font_size"] = int(size_entry.get())
            self.apply_colors_and_fonts()
            self.save_config()
            win.destroy()
            self.options_window = None

        ctk.CTkButton(scroll, text="Aplicar", command=apply_settings).pack(pady=10)

        win.protocol("WM_DELETE_WINDOW", lambda: self.close_options())

    def close_options_or_app(self):
        if self.options_window and tk.Toplevel.winfo_exists(self.options_window):
            self.close_options()
        else:
            self.destroy()

    def close_options(self):
        if self.options_window:
            self.options_window.destroy()
            self.options_window = None

    def apply_colors_and_fonts(self):
        self.top_frame.configure(fg_color=self.config.get("top_frame_color","#F0F0F0"))
        self.middle_frame.configure(fg_color=self.config.get("middle_frame_color","#FFFFFF"))
        self.bottom_frame.configure(fg_color=self.config.get("bottom_frame_color","#F0F0F0"))
        self.font_normal = (self.config.get("font_family","Helvetica"), self.config.get("font_size",11))
        for widget in [self.entry_task, self.entry_due_date, self.entry_due_time,
                       self.btn_complete, self.btn_edit, self.btn_delete, self.btn_clear, self.btn_save, self.btn_load]:
            widget.configure(font=self.font_normal)
        self.refresh_table()

    # ---------- NOTIFICACIONES ----------
    def notification_loop(self):
        while True:
            for task in self.tasks:
                if not task["completed"]:
                    due_dt = datetime.strptime(f"{task['due_date']} {task['due_time']}", "%Y-%m-%d %H:%M")
                    now = datetime.now()
                    if now <= due_dt <= now + timedelta(minutes=1):
                        notification.notify(
                            title="GaiaNet",
                            message=f"Tarea próxima: {task['text']}",
                            timeout=10
                        )
            threading.Event().wait(60)

    # ---------- FUNCIONES DE GESTIÓN DE TAREAS ----------
    def safe_call(self, func,*args,**kwargs):
        try: func(*args,**kwargs)
        except Exception as e:
            with open("error.log","a",encoding="utf-8") as f:
                f.write(f"{datetime.now()} - {repr(e)}\n")
            messagebox.showerror("Error","Ha ocurrido un error. Revisa error.log")

    def add_task(self): self.safe_call(self._add_task)
    def _add_task(self):
        text = self.entry_task.get().strip()
        if not text: return
        added_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        due_date = self.entry_due_date.get()
        due_time = self.entry_due_time.get()
        task = {"text": text,"completed":False,"added":added_time,"due_date":due_date,"due_time":due_time}
        self.tasks.append(task)
        self.entry_task.delete(0,tk.END)
        self.refresh_table(select_index=len(self.tasks)-1)

    def toggle_selected_completed(self): self.safe_call(self._toggle_selected_completed)
    def _toggle_selected_completed(self):
        sel = self.tree.selection()
        if not sel: return
        index = self.tree.index(sel[0])
        self.tasks[index]["completed"] = not self.tasks[index]["completed"]
        self.refresh_table(select_index=index)

    def delete_task(self): self.safe_call(self._delete_task)
    def _delete_task(self):
        sel = self.tree.selection()
        if not sel: return
        index = self.tree.index(sel[0])
        self.tasks.pop(index)
        self.refresh_table()

    def clear_completed(self): self.safe_call(self._clear_completed)
    def _clear_completed(self):
        self.tasks = [t for t in self.tasks if not t["completed"]]
        self.refresh_table()

    def edit_task(self): self.safe_call(self._edit_task)
    def _edit_task(self):
        sel = self.tree.selection()
        if not sel: return
        index = self.tree.index(sel[0])
        task = self.tasks.pop(index)
        self.entry_task.delete(0,tk.END)
        self.entry_task.insert(0, task["text"])
        self.entry_due_date.set_date(date.fromisoformat(task["due_date"]))
        self.entry_due_time.set(task.get("due_time","12:00"))
        self.refresh_table()

    def refresh_table(self, select_index=None):
        for row in self.tree.get_children(): self.tree.delete(row)
        for t in self.tasks:
            status = "✔️" if t["completed"] else "Pendiente"
            due_text = f"{t['due_date']} {t['due_time']}"
            tags = ("completed",) if t["completed"] else ()
            self.tree.insert("",tk.END,values=(t["text"],t["added"],due_text,status),tags=tags)
        if select_index is not None and self.tasks:
            children = self.tree.get_children()
            if 0<=select_index<len(children):
                iid = children[select_index]
                self.tree.selection_set(iid)
                self.tree.focus(iid)

    def save_tasks(self): self.safe_call(self._save_tasks)
    def _save_tasks(self):
        with open(TASKS_FILE,"w",encoding="utf-8") as f: json.dump(self.tasks,f,ensure_ascii=False,indent=2)

    def load_tasks(self): self.safe_call(self._load_tasks)
    def _load_tasks(self):
        if not os.path.exists(TASKS_FILE): return
        with open(TASKS_FILE,"r",encoding="utf-8") as f: loaded=json.load(f)
        self.tasks=[t for t in loaded if t.get("text","").strip()]
        self.refresh_table()

    # ---------- NAVEGACIÓN CON TECLADO ----------
    def select_prev_task(self):
        sel = self.tree.selection()
        children = self.tree.get_children()
        if sel and children:
            index = self.tree.index(sel[0])
            if index > 0:
                self.tree.selection_set(children[index-1])
                self.tree.focus(children[index-1])

    def select_next_task(self):
        sel = self.tree.selection()
        children = self.tree.get_children()
        if sel and children:
            index = self.tree.index(sel[0])
            if index < len(children)-1:
                self.tree.selection_set(children[index+1])
                self.tree.focus(children[index+1])

if __name__=="__main__":
    app = TodoApp()
    app.mainloop()
