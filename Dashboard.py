import os


def mostrar_codigo(ruta_script):
    ruta_script_absoluta = os.path.abspath(ruta_script)
    try:
        with open(ruta_script_absoluta, 'r', encoding='utf-8' ) as archivo:
            codigo = archivo.read()
            print(f"\n--- Código de {ruta_script} ---\n")
            print(codigo)
            print("\n--- Resultado de la ejecución ---\n")
            exec(codigo, globals())
    except FileNotFoundError:
        print("El archivo no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")


def mostrar_menu():
    ruta_base = os.path.dirname(__file__)

    opciones = {
        '1': 'Parcial 01/Semana 02/Tarea Semana 02.py',
        '2': 'Parcial 01/Semana 03/Programacion Orientada a Objetos.py',
        '3': 'Parcial 01/Semana 03/Programacion Tradicional.py',
        '4': 'Parcial 01/Semana 04/Tarea Semana 04.py',
        '5': 'Parcial 01/Semana 05/Tarea Semana 05.py',
        '6': 'Parcial 01/Semana 06/Tarea Semana 06.py',
        '7': 'Parcial 01/Semana 07/Tarea Semana 07.py',
    }

    while True:
        print("\nMenu Principal - Dashboard")
        for key in opciones:
            print(f"{key} - {opciones[key]}")
        print("0 - Salir")

        eleccion = input("Elige un script para ver su código o '0' para salir: ")
        if eleccion == '0':
            break
        elif eleccion in opciones:
            ruta_script = os.path.join(ruta_base, opciones[eleccion])
            mostrar_codigo(ruta_script)
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")


if __name__ == "__main__":
    mostrar_menu()