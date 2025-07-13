class Personaje:
    def __init__(self, nombre, fuerza, vida):
        # Inicializa nombre, fuerza y vida al crear el objeto
        self.nombre = nombre
        self.fuerza = fuerza
        self.vida = vida
        print(f"Se ha creado el personaje: {self.nombre}, fuerza {self.fuerza} puntos, vida {self.vida} puntos.")

    def saludar(self):
        print(f"Hola, mi nombre es {self.nombre}.")

    def mostrar_fuerza(self):
        print(f"La fuerza del personaje es {self.fuerza}.")

    def mostrar_vida(self):
        print(f"La vitalidad del personaje es {self.vida}.")

    # Uso del metodo __del__
    def __del__(self):
        print(f"El objeto Personaje '{self.nombre}' ha sido eliminado.")


# Crear y usar un objeto Personaje
personaje1 = Personaje("El maldito", 8, 6)
personaje1.saludar()
personaje1.mostrar_fuerza()
personaje1.mostrar_vida()

print("Fin del programa.")