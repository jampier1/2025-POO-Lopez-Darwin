import json
import os
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict

DEFAULT_FILE = "inventario.json"


# -------------------------
# Clase Producto
# -------------------------
class Producto:
    """
    Representa un producto con ID único, nombre, cantidad y precio.
    Provee validaciones en los setters y serialización a dict (para JSON).
    """

    def __init__(self, id: str, nombre: str, cantidad: int, precio: float):
        # Utilizamos los setters para validar
        self.id = id
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    # id
    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("El ID no puede estar vacío.")
        self._id = value.strip()

    # nombre
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = value.strip()

    # cantidad
    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, value: int) -> None:
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("La cantidad debe ser un entero.")
        if value < 0:
            raise ValueError("La cantidad debe ser mayor o igual a 0.")
        self._cantidad = value

    # precio
    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, value: float) -> None:
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser numérico.")
        if value < 0:
            raise ValueError("El precio debe ser mayor o igual a 0.")
        self._precio = value

    # serialización para persistencia
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "precio": self.precio
        }

    @staticmethod
    def from_dict(d: Dict) -> "Producto":
        return Producto(
            id=str(d.get("id", "")),
            nombre=str(d.get("nombre", "")),
            cantidad=int(d.get("cantidad", 0)),
            precio=float(d.get("precio", 0.0))
        )

    def __str__(self) -> str:
        return f"{self.id:<8} | {self.nombre:<25} | Cant: {self.cantidad:<6} | ${self.precio:>8.2f}"


# -------------------------
# Clase Inventario
# -------------------------
class Inventario:
    """Maneja la colección de productos y su persistencia en archivo.

    Estructura:
      - _productos: Dict[id, Producto]  -> acceso rápido por ID (O(1))
      - _indice_nombre: Dict[nombre_normalizado, Set[ids]] -> búsqueda rápida por nombre exacto
    """

    def __init__(self, archivo: str = DEFAULT_FILE):
        self.ARCHIVO = archivo
        self._productos: Dict[str, Producto] = {}
        self._indice_nombre: Dict[str, Set[str]] = defaultdict(set)
        # Intentamos cargar el archivo si existe
        try:
            self.cargar()
        except Exception:
            # Si archivo corrupto o error, iniciamos vacío (no rompemos el programa)
            self._productos = {}
            self._indice_nombre = defaultdict(set)

    # ---------- utilidades internas ----------
    @staticmethod
    def _normalizar(texto: str) -> str:
        return texto.strip().lower()

    def _indexar(self, producto: Producto) -> None:
        clave = self._normalizar(producto.nombre)
        self._indice_nombre[clave].add(producto.id)

    def _desindexar(self, producto: Producto) -> None:
        clave = self._normalizar(producto.nombre)
        ids = self._indice_nombre.get(clave)
        if ids and producto.id in ids:
            ids.remove(producto.id)
            if not ids:
                del self._indice_nombre[clave]

    # ---------- operaciones requeridas ----------
    def añadir_producto(self, producto: Producto) -> None:
        """Añade un nuevo producto; lanza KeyError si el ID ya existe."""
        if producto.id in self._productos:
            raise KeyError(f"ID '{producto.id}' ya existe.")
        self._productos[producto.id] = producto
        self._indexar(producto)
        # se guarda automáticamente para persistencia inmediata
        self.guardar()

    def eliminar_producto(self, id_producto: str) -> None:
        """Elimina un producto por ID; lanza KeyError si no existe."""
        if id_producto not in self._productos:
            raise KeyError(f"Producto con ID '{id_producto}' no encontrado.")
        prod = self._productos[id_producto]
        self._desindexar(prod)
        del self._productos[id_producto]
        self.guardar()

    def actualizar_cantidad(self, id_producto: str, nueva_cantidad: int) -> None:
        """Actualiza cantidad; lanza KeyError si el ID no existe."""
        if id_producto not in self._productos:
            raise KeyError(f"Producto con ID '{id_producto}' no encontrado.")
        self._productos[id_producto].cantidad = nueva_cantidad
        self.guardar()

    def actualizar_precio(self, id_producto: str, nuevo_precio: float) -> None:
        """Actualiza precio; lanza KeyError si el ID no existe."""
        if id_producto not in self._productos:
            raise KeyError(f"Producto con ID '{id_producto}' no encontrado.")
        self._productos[id_producto].precio = nuevo_precio
        self.guardar()

    def actualizar_nombre(self, id_producto: str, nuevo_nombre: str) -> None:
        """Actualiza el nombre y mantiene el índice por nombre."""
        if id_producto not in self._productos:
            raise KeyError(f"Producto con ID '{id_producto}' no encontrado.")
        prod = self._productos[id_producto]
        self._desindexar(prod)
        prod.nombre = nuevo_nombre
        self._indexar(prod)
        self.guardar()

    # ---------- búsquedas y listados ----------
    def buscar_por_nombre(self, texto: str) -> List[Producto]:
        """
        Devuelve lista de Productos cuya nombre contiene texto (case-insensitive).
        Primero intenta coincidencia exacta por índice (palabra completa normalizada).
        Si no hay, hace búsqueda por subcadena (lineal).
        """
        clave = self._normalizar(texto)
        resultados: List[Producto] = []

        # 1) coincidencia exacta por índice
        if clave in self._indice_nombre:
            for pid in sorted(self._indice_nombre[clave]):
                resultados.append(self._productos[pid])
            return resultados

        # 2) fallback: búsqueda por subcadena en cada nombre
        for p in self._productos.values():
            if clave in self._normalizar(p.nombre):
                resultados.append(p)
        # devolvemos ordenado por ID
        return sorted(resultados, key=lambda x: x.id)

    def mostrar_todos(self) -> List[Tuple[str, str, int, float]]:
        """Devuelve una lista de tuplas (id, nombre, cantidad, precio) ordenada por ID."""
        productos = [self._productos[k] for k in sorted(self._productos.keys())]
        return [(p.id, p.nombre, p.cantidad, p.precio) for p in productos]

    def obtener_producto(self, id_producto: str) -> Optional[Producto]:
        return self._productos.get(id_producto)

    def contar(self) -> int:
        return len(self._productos)

    # ---------- persistencia ----------
    def guardar(self, ruta: Optional[str] = None) -> None:
        ruta = ruta or self.ARCHIVO
        data = {pid: prod.to_dict() for pid, prod in self._productos.items()}
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def cargar(self, ruta: Optional[str] = None) -> None:
        ruta = ruta or self.ARCHIVO
        if not os.path.exists(ruta):
            return
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        # reconstruir estructura en memoria
        self._productos.clear()
        self._indice_nombre.clear()
        for pid, d in data.items():
            prod = Producto.from_dict(d)
            self._productos[pid] = prod
            self._indexar(prod)


# -------------------------
# Interfaz de usuario (consola)
# -------------------------
def leer_texto(prompt: str) -> str:
    return input(prompt).strip()


def leer_int(prompt: str) -> int:
    while True:
        s = input(prompt).strip()
        try:
            return int(s)
        except ValueError:
            print("Entrada inválida. Escribe un número entero.")


def leer_float(prompt: str) -> float:
    while True:
        s = input(prompt).strip()
        try:
            return float(s)
        except ValueError:
            print("Entrada inválida. Escribe un número (puede tener decimales).")


def mostrar_producto_console(p: Producto) -> None:
    print(p)


def menu():
    inv = Inventario()
    print("=== Sistema Avanzado de Gestión de Inventario ===")
    print(f"Archivo de datos: {inv.ARCHIVO} (productos cargados: {inv.contar()})")

    while True:
        print("\nMenú:")
        print("1) Añadir producto")
        print("2) Eliminar producto por ID")
        print("3) Actualizar cantidad")
        print("4) Actualizar precio")
        print("5) Actualizar nombre")
        print("6) Buscar por nombre")
        print("7) Mostrar todos")
        print("8) Guardar manualmente")
        print("9) Cargar desde archivo")
        print("0) Salir (guarda automáticamente)")

        opcion = leer_texto("Selecciona una opción (0-9): ")

        try:
            if opcion == "1":
                pid = leer_texto("ID (único): ")
                if inv.obtener_producto(pid) is not None:
                    print("Error: ID ya existe.")
                    continue
                nombre = leer_texto("Nombre: ")
                cantidad = leer_int("Cantidad inicial: ")
                precio = leer_float("Precio: ")
                prod = Producto(pid, nombre, cantidad, precio)
                inv.añadir_producto(prod)
                print("Producto añadido correctamente.")

            elif opcion == "2":
                pid = leer_texto("ID a eliminar: ")
                inv.eliminar_producto(pid)
                print("Producto eliminado.")

            elif opcion == "3":
                pid = leer_texto("ID a actualizar cantidad: ")
                nueva = leer_int("Nueva cantidad: ")
                inv.actualizar_cantidad(pid, nueva)
                print("Cantidad actualizada.")

            elif opcion == "4":
                pid = leer_texto("ID a actualizar precio: ")
                nuevo = leer_float("Nuevo precio: ")
                inv.actualizar_precio(pid, nuevo)
                print("Precio actualizado.")

            elif opcion == "5":
                pid = leer_texto("ID a actualizar nombre: ")
                nuevo = leer_texto("Nuevo nombre: ")
                inv.actualizar_nombre(pid, nuevo)
                print("Nombre actualizado.")

            elif opcion == "6":
                texto = leer_texto("Nombre o parte del nombre: ")
                encontrados = inv.buscar_por_nombre(texto)
                if not encontrados:
                    print("No se encontraron productos.")
                else:
                    print(f"Se encontraron {len(encontrados)} producto(s):")
                    for p in encontrados:
                        mostrar_producto_console(p)

            elif opcion == "7":
                todos = inv.mostrar_todos()
                if not todos:
                    print("Inventario vacío.")
                else:
                    print(f"Inventario ({len(todos)} productos):")
                    print("ID      | Nombre                    | Cant  | Precio")
                    print("-" * 60)
                    for id_, nombre, cant, precio in todos:
                        print(f"{id_:<8} | {nombre:<25} | {cant:<6} | ${precio:>8.2f}")

            elif opcion == "8":
                inv.guardar()
                print("Inventario guardado en archivo.")

            elif opcion == "9":
                inv.cargar()
                print("Inventario recargado desde archivo.")

            elif opcion == "0":
                inv.guardar()
                print("Inventario guardado. Saliendo...")
                break

            else:
                print("Opción inválida. Intenta de nuevo.")

        except KeyError as ke:
            print("Error:", ke)
        except ValueError as ve:
            print("Valor inválido:", ve)
        except Exception as e:
            # mensaje genérico para cualquier otro error inesperado
            print("Ocurrió un error:", e)


# Ejecutar menú si se llama el archivo directamente
if __name__ == "__main__":
    menu()