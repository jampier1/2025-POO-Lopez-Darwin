# Tarea semana 06

# Clase base: aplica encapsulamiento y abstracción
class Animal:
    def __init__(self, especie, taxonomia, caracteristica):
        # Encapsulamiento: atributos con _
        self._especie = especie
        self._taxonomia = taxonomia
        self._caracteristica = caracteristica

    def describir(self):  # Abstracción: método que describe al animal
        return f"{self._especie} pertenece a la clase {self._taxonomia} y es {self._caracteristica}."

    def tipo_de_animal(self):  # Se sobrescribe (polimorfismo)
        return "Sistemática a la que pertenece el animal."

    def get_especie(self):  # Encapsulamiento con método de acceso
        return self._especie

    def set_especie(self, nueva_especie):  # Encapsulamiento con método modificador
        self._especie = nueva_especie


# Clase hija: Serpiente - Herencia, polimorfismo
class Serpiente(Animal):  # Herencia
    def __init__(self, especie, taxonomia, fisiologia):
        super().__init__(especie, taxonomia, fisiologia)
        self._fisiologia = fisiologia

    def tipo_de_animal(self):  # Polimorfismo: sobrescribe método
        return f"{self.get_especie()} es un reptil."

    def obtener_fisiologia(self):
        return self._fisiologia


# Clase hija: Perro - Herencia, polimorfismo
class Perro(Animal):  # Herencia
    def __init__(self, especie, taxonomia, domestico):
        super().__init__(especie, taxonomia, domestico)
        self._domestico = domestico

    def tipo_de_animal(self):  # Polimorfismo
        return f"{self.get_especie()} es un mamífero."

    def get_domestico(self):
        return self._domestico


# Polimorfismo: la función puede actuar sobre cualquier clase hija de Animal
def clase_de_taxonomia(animal):
    print(animal.tipo_de_animal())


# Instancias (demostración de uso de objetos y métodos)
animal = Animal("Corvus corax", "Aves", "ovíparo")
serpiente = Serpiente("Boa constrictor", "Reptilia", "Vertebrado")
perro = Perro("Canis lupus familiaris", "Mammalia", "Doméstico")

# Abstracción: uso de métodos que ocultan la implementación interna
print(animal.describir())
print(serpiente.describir())
print(perro.describir())

# Polimorfismo: misma función se comporta diferente según el objeto
clase_de_taxonomia(serpiente)
clase_de_taxonomia(perro)
