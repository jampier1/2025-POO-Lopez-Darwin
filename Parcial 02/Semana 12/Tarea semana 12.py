import json
import os

# --- CLASES --- #
class Libro:
    def __init__(self, titulo, autor, categoria, isbn):
        # titulo y autor como tuplas inmutables
        if not isinstance(titulo, tuple) or not isinstance(autor, tuple):
            raise TypeError("Título y autor deben ser tuplas")
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.isbn = isbn

    def __str__(self):
        titulo_str = " ".join(self.titulo)
        autor_str = " ".join(self.autor)
        return f"{titulo_str} de {autor_str} (Categoría: {self.categoria}, ISBN: {self.isbn})"

    def to_dict(self):
        return {
            "titulo": list(self.titulo),
            "autor": list(self.autor),
            "categoria": self.categoria,
            "isbn": self.isbn
        }

    @staticmethod
    def from_dict(data):
        return Libro(tuple(data["titulo"]), tuple(data["autor"]), data["categoria"], data["isbn"])


class Usuario:
    def __init__(self, nombre, id_usuario):
        self.nombre = nombre
        self.id_usuario = id_usuario
        self.libros_prestados = []  # lista de objetos Libro

    def __str__(self):
        return f"{self.nombre} (ID: {self.id_usuario})"

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "id_usuario": self.id_usuario,
            "libros_prestados": [libro.to_dict() for libro in self.libros_prestados]
        }

    @staticmethod
    def from_dict(data):
        usuario = Usuario(data["nombre"], data["id_usuario"])
        usuario.libros_prestados = [Libro.from_dict(l) for l in data.get("libros_prestados", [])]
        return usuario


# --- BIBLIOTECA --- #
class Biblioteca:
    LIBROS_FILE = "libros.json"
    USUARIOS_FILE = "usuarios.json"
    PRESTAMOS_FILE = "prestamos.json"

    def __init__(self):
        self.libros = {}  # isbn -> Libro
        self.usuarios = set()  # conjunto de id_usuario
        self.usuarios_data = {}  # id_usuario -> Usuario (para datos completos)
        self.cargar_datos()

    # --- GUARDAR DATOS --- #
    def guardar_libros(self):
        with open(self.LIBROS_FILE, "w", encoding="utf-8") as f:
            json.dump([libro.to_dict() for libro in self.libros.values()], f, indent=4, ensure_ascii=False)

    def guardar_usuarios(self):
        with open(self.USUARIOS_FILE, "w", encoding="utf-8") as f:
            json.dump([usuario.to_dict() for usuario in self.usuarios_data.values()], f, indent=4, ensure_ascii=False)

    def guardar_prestamos(self):
        # Guardar solo los libros prestados por usuario
        prestamos = {}
        for uid, usuario in self.usuarios_data.items():
            prestamos[uid] = [libro.to_dict() for libro in usuario.libros_prestados]
        with open(self.PRESTAMOS_FILE, "w", encoding="utf-8") as f:
            json.dump(prestamos, f, indent=4, ensure_ascii=False)

    # --- CARGAR DATOS --- #
    def cargar_datos(self):
        # Cargar libros
        if os.path.exists(self.LIBROS_FILE):
            try:
                with open(self.LIBROS_FILE, "r", encoding="utf-8") as f:
                    libros_data = json.load(f)
                    for l in libros_data:
                        libro = Libro.from_dict(l)
                        self.libros[libro.isbn] = libro
            except (json.JSONDecodeError, FileNotFoundError):
                self.libros = {}

        # Cargar usuarios
        if os.path.exists(self.USUARIOS_FILE):
            try:
                with open(self.USUARIOS_FILE, "r", encoding="utf-8") as f:
                    usuarios_data = json.load(f)
                    for u in usuarios_data:
                        usuario = Usuario.from_dict(u)
                        self.usuarios.add(usuario.id_usuario)
                        self.usuarios_data[usuario.id_usuario] = usuario
            except (json.JSONDecodeError, FileNotFoundError):
                self.usuarios = set()
                self.usuarios_data = {}

        # Cargar préstamos (libros prestados)
        if os.path.exists(self.PRESTAMOS_FILE):
            try:
                with open(self.PRESTAMOS_FILE, "r", encoding="utf-8") as f:
                    prestamos_data = json.load(f)
                    for uid, libros in prestamos_data.items():
                        if uid in self.usuarios_data:
                            self.usuarios_data[uid].libros_prestados = [Libro.from_dict(l) for l in libros]
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    # --- LIBROS --- #
    def agregar_libro(self, libro):
        if libro.isbn in self.libros:
            print("El libro ya existe en la biblioteca.")
            return
        self.libros[libro.isbn] = libro
        self.guardar_libros()
        print(f"Libro agregado: {libro}")

    def quitar_libro(self, isbn):
        # Validar que el libro no esté prestado
        for usuario in self.usuarios_data.values():
            if any(libro.isbn == isbn for libro in usuario.libros_prestados):
                print("No se puede eliminar el libro porque está prestado.")
                return
        if isbn not in self.libros:
            print("El libro no existe en la biblioteca.")
            return
        eliminado = self.libros.pop(isbn)
        self.guardar_libros()
        print(f"Libro eliminado: {eliminado}")

    # --- USUARIOS --- #
    def registrar_usuario(self, usuario):
        if usuario.id_usuario in self.usuarios:
            print("El ID de usuario ya está registrado.")
            return
        self.usuarios.add(usuario.id_usuario)
        self.usuarios_data[usuario.id_usuario] = usuario
        self.guardar_usuarios()
        self.guardar_prestamos()
        print(f"Usuario registrado: {usuario}")

    def dar_baja_usuario(self, id_usuario):
        if id_usuario not in self.usuarios:
            print("El usuario no existe.")
            return
        # Devolver todos los libros prestados antes de eliminar usuario
        usuario = self.usuarios_data[id_usuario]
        for libro in usuario.libros_prestados[:]:  # copia para evitar modificar mientras iteramos
            self.devolver_libro(id_usuario, libro.isbn)
        self.usuarios.remove(id_usuario)
        self.usuarios_data.pop(id_usuario)
        self.guardar_usuarios()
        self.guardar_prestamos()
        print(f"Usuario dado de baja: {id_usuario}")

    # --- PRÉSTAMOS --- #
    def prestar_libro(self, id_usuario, isbn):
        if id_usuario not in self.usuarios:
            print("Usuario no registrado.")
            return
        if isbn not in self.libros:
            print("Libro no disponible para préstamo.")
            return
        usuario = self.usuarios_data[id_usuario]
        # Verificar que el usuario no tenga ya el libro prestado
        if any(libro.isbn == isbn for libro in usuario.libros_prestados):
            print("El usuario ya tiene prestado este libro.")
            return
        libro = self.libros.pop(isbn)
        usuario.libros_prestados.append(libro)
        self.guardar_libros()
        self.guardar_prestamos()
        print(f"Libro prestado: {libro} a {usuario.nombre}")

    def devolver_libro(self, id_usuario, isbn):
        if id_usuario not in self.usuarios:
            print("Usuario no registrado.")
            return
        usuario = self.usuarios_data[id_usuario]
        libro = next((l for l in usuario.libros_prestados if l.isbn == isbn), None)
        if libro is None:
            print("El usuario no tiene ese libro prestado.")
            return
        usuario.libros_prestados.remove(libro)
        self.libros[isbn] = libro
        self.guardar_libros()
        self.guardar_prestamos()
        print(f"Libro devuelto: {libro}")

    # --- BÚSQUEDA --- #
    def buscar_libros(self, valor):
        valor = valor.lower()
        resultados = []
        for libro in self.libros.values():
            titulo_str = " ".join(libro.titulo).lower()
            autor_str = " ".join(libro.autor).lower()
            categoria_str = libro.categoria.lower()
            if valor in titulo_str or valor in autor_str or valor in categoria_str:
                resultados.append(libro)
        return resultados

    # --- LISTADOS --- #
    def listar_catalogo(self):
        if not self.libros:
            print("No hay libros disponibles.")
            return
        print("Catálogo de libros disponibles:")
        for libro in self.libros.values():
            print(f"- {libro}")

    def listar_usuarios(self):
        if not self.usuarios:
            print("No hay usuarios registrados.")
            return
        print("Usuarios registrados:")
        for usuario in self.usuarios_data.values():
            print(f"- {usuario}")

    def listar_todos_los_prestamos(self):
        any_prestamos = False
        for usuario in self.usuarios_data.values():
            if usuario.libros_prestados:
                any_prestamos = True
                print(f"\nUsuario: {usuario.nombre} (ID: {usuario.id_usuario})")
                for libro in usuario.libros_prestados:
                    print(f"  - {libro}")
        if not any_prestamos:
            print("No hay libros prestados actualmente.")

    def listar_libros_prestados_usuario(self, id_usuario):
        if id_usuario not in self.usuarios:
            print("Usuario no registrado.")
            return
        usuario = self.usuarios_data[id_usuario]
        if not usuario.libros_prestados:
            print(f"El usuario {usuario.nombre} no tiene libros prestados.")
            return
        print(f"Libros prestados de {usuario.nombre}:")
        for libro in usuario.libros_prestados:
            print(f"- {libro}")


# --- MENÚ INTERACTIVO --- #
def menu():
    biblioteca = Biblioteca()

    while True:
        print("\n===== BIBLIOTECA DIGITAL PROFESIONAL =====")
        print("1. Agregar libro")
        print("2. Quitar libro")
        print("3. Registrar usuario")
        print("4. Dar de baja usuario")
        print("5. Prestar libro")
        print("6. Devolver libro")
        print("7. Buscar libros (título, autor o categoría)")
        print("8. Ver libros prestados de un usuario")
        print("9. Ver catálogo completo")
        print("10. Mostrar todos los libros prestados")
        print("11. Mostrar todos los usuarios")
        print("0. Salir")

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            titulo = input("Título: ").strip()
            autor = input("Autor: ").strip()
            categoria = input("Categoría: ").strip()
            isbn = input("ISBN: ").strip()
            if not titulo or not autor or not categoria or not isbn:
                print("Todos los campos son obligatorios.")
                continue
            libro = Libro(tuple(titulo.split()), tuple(autor.split()), categoria, isbn)
            biblioteca.agregar_libro(libro)

        elif opcion == "2":
            isbn = input("ISBN del libro a quitar: ").strip()
            if not isbn:
                print("ISBN es obligatorio.")
                continue
            biblioteca.quitar_libro(isbn)

        elif opcion == "3":
            nombre = input("Nombre del usuario: ").strip()
            id_usuario = input("ID único del usuario: ").strip()
            if not nombre or not id_usuario:
                print("Nombre e ID son obligatorios.")
                continue
            usuario = Usuario(nombre, id_usuario)
            biblioteca.registrar_usuario(usuario)

        elif opcion == "4":
            id_usuario = input("ID del usuario a dar de baja: ").strip()
            if not id_usuario:
                print("ID es obligatorio.")
                continue
            biblioteca.dar_baja_usuario(id_usuario)

        elif opcion == "5":
            id_usuario = input("ID del usuario: ").strip()
            isbn = input("ISBN del libro a prestar: ").strip()
            if not id_usuario or not isbn:
                print("ID y ISBN son obligatorios.")
                continue
            biblioteca.prestar_libro(id_usuario, isbn)

        elif opcion == "6":
            id_usuario = input("ID del usuario: ").strip()
            isbn = input("ISBN del libro a devolver: ").strip()
            if not id_usuario or not isbn:
                print("ID y ISBN son obligatorios.")
                continue
            biblioteca.devolver_libro(id_usuario, isbn)

        elif opcion == "7":
            valor = input("Buscar libro por título, autor o categoría: ").strip()
            if not valor:
                print("Debe ingresar un valor para buscar.")
                continue
            resultados = biblioteca.buscar_libros(valor)
            if resultados:
                print("Resultados encontrados:")
                for libro in resultados:
                    print(f"- {libro}")
            else:
                print("No se encontraron libros que coincidan.")

        elif opcion == "8":
            id_usuario = input("ID del usuario: ").strip()
            if not id_usuario:
                print("ID es obligatorio.")
                continue
            biblioteca.listar_libros_prestados_usuario(id_usuario)

        elif opcion == "9":
            biblioteca.listar_catalogo()

        elif opcion == "10":
            biblioteca.listar_todos_los_prestamos()

        elif opcion == "11":
            biblioteca.listar_usuarios()

        elif opcion == "0":
            print("Saliendo del sistema...")
            break

        else:
            print("Opción inválida. Intenta de nuevo.")


if __name__ == "__main__":
    menu()
