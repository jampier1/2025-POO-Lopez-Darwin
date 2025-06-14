# Programación Orientada a Objetos (POO)


class Clima:
    """Clase que representa la información diaria del clima."""

    def __init__(self):
        """Inicializa una lista para almacenar las temperaturas."""
        self.temperaturas = []

    def ingresar_temperatura(self, dia):
        """Metodo para ingresar la temperatura de un día específico."""
        while True:
            try:
                temp = float(input(f"Ingrese la temperatura del día {dia}: "))
                self.temperaturas.append(temp)
                break  # Salir del bucle si la entrada es válida
            except ValueError:
                print("Por favor, ingrese un número válido.")

    def calcular_promedio(self):
        """Metodo para calcular el promedio de las temperaturas."""
        if len(self.temperaturas) == 0:
            return 0
        return sum(self.temperaturas) / len(self.temperaturas)


def main():
    """Función principal para ejecutar el programa."""
    print("Cálculo del promedio semanal del clima")
    clima = Clima()  # Crear una instancia de la clase Clima

    # Ingresar temperaturas para cada día de la semana
    for dia in range(1, 8):
        clima.ingresar_temperatura(dia)

    promedio = clima.calcular_promedio()
    print(f"El promedio semanal de las temperaturas es: {promedio:.2f}°C")


# Ejecutar el programa
if __name__ == "__main__":
    main()
