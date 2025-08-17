import json  # Para guardar y cargar los productos en un archivo JSON
import os    # Para verificar si el archivo existe

# ------------------------------
# Clase Producto
# ------------------------------
class Producto:
    """
    Representa un producto con ID, nombre, cantidad y precio.
    """
    def __init__(self, id_producto, nombre, cantidad, precio):
        self.id_producto = id_producto  # Identificador único del producto
        self.nombre = nombre            # Nombre del producto
        self.cantidad = cantidad        # Cantidad disponible en inventario
        self.precio = precio            # Precio unitario

    # --------------------------
    # Métodos para obtener información del producto
    # --------------------------
    def get_id(self):
        return self.id_producto

    def get_nombre(self):
        return self.nombre

    def get_cantidad(self):
        return self.cantidad

    def get_precio(self):
        return self.precio

    # --------------------------
    # Métodos para modificar información del producto
    # --------------------------
    def set_nombre(self, nombre):
        self.nombre = nombre

    def set_cantidad(self, cantidad):
        self.cantidad = cantidad

    def set_precio(self, precio):
        self.precio = precio

    # --------------------------
    # Métodos para guardar/cargar como diccionario (para JSON)
    # --------------------------
    def to_dict(self):
        """Convierte el producto a un diccionario para guardarlo en JSON"""
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "precio": self.precio
        }

    @staticmethod
    def from_dict(data):
        """Crea un objeto Producto a partir de un diccionario"""
        return Producto(data["id_producto"], data["nombre"], data["cantidad"], data["precio"])

    # Representación en texto del producto
    def __str__(self):
        return f"ID: {self.id_producto} | Nombre: {self.nombre} | Cantidad: {self.cantidad} | Precio: ${self.precio:.2f}"


# ------------------------------
# Clase Inventario
# ------------------------------
class Inventario:
    """
    Representa el inventario de productos.
    Utiliza un diccionario donde la clave es el ID del producto.
    """
    def __init__(self, archivo="inventario.json"):
        self.archivo = archivo      # Nombre del archivo donde se guardan los productos
        self.productos = {}         # Diccionario para guardar los productos
        self.cargar()               # Cargar productos existentes del archivo al iniciar

    # --------------------------
    # Guardar todos los productos en un archivo JSON
    # --------------------------
    def guardar(self):
        with open(self.archivo, "w") as f:
            # Convertimos cada producto a diccionario antes de guardar
            json.dump({pid: p.to_dict() for pid, p in self.productos.items()}, f, indent=4)

    # --------------------------
    # Cargar productos desde el archivo JSON al iniciar el programa
    # --------------------------
    def cargar(self):
        if os.path.exists(self.archivo):
            with open(self.archivo, "r") as f:
                data = json.load(f)
                for pid, pdata in data.items():
                    self.productos[pid] = Producto.from_dict(pdata)

    # --------------------------
    # Añadir un nuevo producto
    # --------------------------
    def agregar_producto(self, producto):
        if producto.get_id() in self.productos:
            print("Error: Ya existe un producto con ese ID.")
            return
        self.productos[producto.get_id()] = producto
        self.guardar()  # Guardamos automáticamente
        print("Producto añadido con éxito.")

    # --------------------------
    # Eliminar un producto por su ID
    # --------------------------
    def eliminar_producto(self, id_producto):
        if id_producto in self.productos:
            del self.productos[id_producto]
            self.guardar()  # Guardamos automáticamente
            print("Producto eliminado.")
        else:
            print("No se encontró un producto con ese ID.")

    # --------------------------
    # Actualizar cantidad o precio de un producto
    # --------------------------
    def actualizar_producto(self, id_producto, cantidad=None, precio=None):
        if id_producto in self.productos:
            if cantidad is not None:
                self.productos[id_producto].set_cantidad(cantidad)
            if precio is not None:
                self.productos[id_producto].set_precio(precio)
            self.guardar()  # Guardamos automáticamente
            print("Producto actualizado.")
        else:
            print("No se encontró un producto con ese ID.")

    # --------------------------
    # Buscar productos por nombre (puede haber coincidencias parciales)
    # --------------------------
    def buscar_por_nombre(self, nombre):
        encontrados = [p for p in self.productos.values() if nombre.lower() in p.get_nombre().lower()]
        if encontrados:
            print("Resultados de búsqueda:")
            for p in encontrados:
                print(p)
        else:
            print("No se encontraron productos con ese nombre.")

    # --------------------------
    # Mostrar todos los productos del inventario
    # --------------------------
    def mostrar_todos(self):
        if not self.productos:
            print("No hay productos en el inventario.")
            return
        print("Inventario:")
        for p in self.productos.values():
            print(p)


# ------------------------------
# Menú Interactivo
# ------------------------------
def menu():
    inventario = Inventario()  # Crear inventario y cargar datos guardados

    while True:
        print("\n=== Sistema de Gestión de Inventarios ===")
        print("1. Añadir producto")
        print("2. Eliminar producto")
        print("3. Actualizar producto")
        print("4. Buscar producto por nombre")
        print("5. Mostrar todos los productos")
        print("6. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            id_p = input("ID del producto: ")
            nombre = input("Nombre: ")
            cantidad = int(input("Cantidad: "))
            precio = float(input("Precio: "))
            nuevo_producto = Producto(id_p, nombre, cantidad, precio)
            inventario.agregar_producto(nuevo_producto)

        elif opcion == "2":
            id_p = input("ID del producto a eliminar: ")
            inventario.eliminar_producto(id_p)

        elif opcion == "3":
            id_p = input("ID del producto a actualizar: ")
            cantidad = input("Nueva cantidad (dejar en blanco si no cambia): ")
            precio = input("Nuevo precio (dejar en blanco si no cambia): ")
            inventario.actualizar_producto(
                id_p,
                cantidad=int(cantidad) if cantidad else None,
                precio=float(precio) if precio else None
            )

        elif opcion == "4":
            nombre = input("Nombre del producto a buscar: ")
            inventario.buscar_por_nombre(nombre)

        elif opcion == "5":
            inventario.mostrar_todos()

        elif opcion == "6":
            print("Saliendo del sistema...")
            break

        else:
            print("Opción no válida, intente de nuevo.")


# ------------------------------
# Ejecutar el programa
# ------------------------------
if __name__ == "__main__":
    menu()
