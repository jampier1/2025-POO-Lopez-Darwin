# Programación Tradicional


def ingresar_temperaturas():
    """Función para ingresar las temperaturas diarias de la semana."""
    temperaturas = []
    for i in range(7):
        while True:
            try:
                temp = float(input(f"Ingrese la temperatura del día {i + 1}: "))
                temperaturas.append(temp)
                break  # Salir del bucle si la entrada es válida
            except ValueError:
                print("Por favor, ingrese un número válido.")
    return temperaturas

def calcular_promedio(temperaturas):
    """Función para calcular el promedio de las temperaturas."""
    return sum(temperaturas) / len(temperaturas)

def main():
    """Función principal para ejecutar el programa."""
    print("Cálculo del promedio semanal del clima")
    temperaturas = ingresar_temperaturas()
    promedio = calcular_promedio(temperaturas)
    print(f"El promedio semanal de las temperaturas es: {promedio:.2f}°C")

# Ejecutar el programa
if __name__ == "__main__":
    main()
