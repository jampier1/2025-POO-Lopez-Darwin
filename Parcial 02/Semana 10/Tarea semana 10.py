import os
import json

class Producto:
    def __init__(self, id_producto, nombre, cantidad, precio):
        self.id = id_producto
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "precio": self.precio
        }

    @staticmethod
    def from_dict(data):
        return Producto(data["id"], data["nombre"], data["cantidad"], data["precio"])

class Inventario:
    def __init__(self, archivo="inventario.json"):
        self.productos = []
        self.archivo = archivo
        self.cargar_desde_archivo()

    def cargar_desde_archivo(self):
        if not os.path.exists(self.archivo):
            open(self.archivo, 'w').write("[]")  # crea el archivo vacío si no existe
        try:
            with open(self.archivo, 'r') as f:
                data = json.load(f)
                for item in data:
                    self.productos.append(Producto.from_dict(item))
        except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
            print(f"Error al leer el archivo: {e}")

    def guardar_en_archivo(self):
        try:
            with open(self.archivo, 'w') as f:
                json.dump([p.to_dict() for p in self.productos], f, indent=4)
        except PermissionError:
            print("Error: no se puede escribir en el archivo.")

    def agregar_producto(self, producto):
        if any(p.id == producto.id for p in self.productos):
            print("ID ya existe.")
        else:
            self.productos.append(producto)
            self.guardar_en_archivo()
            print("Producto agregado y guardado en el archivo.")

    def eliminar_producto(self, id_producto):
        for p in self.productos:
            if p.id == id_producto:
                self.productos.remove(p)
                self.guardar_en_archivo()
                print("Producto eliminado y cambios guardados.")
                return
        print("Producto no encontrado.")

    def actualizar_producto(self, id_producto, cantidad=None, precio=None):
        for p in self.productos:
            if p.id == id_producto:
                if cantidad is not None:
                    p.cantidad = cantidad
                if precio is not None:
                    p.precio = precio
                self.guardar_en_archivo()
                print("Producto actualizado y cambios guardados.")
                return
        print("Producto no encontrado.")

    def buscar_producto(self, nombre):
        resultados = [p for p in self.productos if nombre.lower() in p.nombre.lower()]
        if resultados:
            for p in resultados:
                print(f"ID:{p.id} | Nombre:{p.nombre} | Cantidad:{p.cantidad} | Precio:{p.precio}")
        else:
            print("No se encontraron productos.")

    def mostrar_todos(self):
        if not self.productos:
            print("Inventario vacío.")
        else:
            for p in self.productos:
                print(f"ID:{p.id} | Nombre:{p.nombre} | Cantidad:{p.cantidad} | Precio:{p.precio}")

def menu():
    inventario = Inventario()
    while True:
        print("\n1. Agregar producto\n2. Eliminar producto\n3. Actualizar producto\n4. Buscar producto\n5. Mostrar productos\n6. Salir")
        opcion = input("Elige una opción: ")
        if opcion == '1':
            try:
                id_p = input("ID: ")
                nombre = input("Nombre: ")
                cantidad = int(input("Cantidad: "))
                precio = float(input("Precio: "))
                inventario.agregar_producto(Producto(id_p, nombre, cantidad, precio))
            except ValueError:
                print("Error: valores inválidos para cantidad o precio.")
        elif opcion == '2':
            id_p = input("ID a eliminar: ")
            inventario.eliminar_producto(id_p)
        elif opcion == '3':
            id_p = input("ID a actualizar: ")
            cantidad = input("Nueva cantidad (enter para no cambiar): ")
            precio = input("Nuevo precio (enter para no cambiar): ")
            try:
                cantidad = int(cantidad) if cantidad else None
                precio = float(precio) if precio else None
                inventario.actualizar_producto(id_p, cantidad, precio)
            except ValueError:
                print("Error: valores inválidos para cantidad o precio.")
        elif opcion == '4':
            nombre = input("Nombre a buscar: ")
            inventario.buscar_producto(nombre)
        elif opcion == '5':
            inventario.mostrar_todos()
        elif opcion == '6':
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()
