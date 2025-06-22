from datetime import datetime, timedelta

class Examen:
    """Representa un examen clínico que el laboratorio puede realizar."""

    def __init__(self, tipo, codigo):
        """Inicializa un nuevo examen con tipo y código."""
        self.tipo = tipo
        self.codigo = codigo
        self.realizado = False
        self.fecha_resultado = None

    def realizar(self):
        """Marca el examen como realizado y asigna fecha de entrega de resultados."""
        if not self.realizado:
            self.realizado = True
            self.fecha_resultado = datetime.now() + timedelta(days=2)
            return True
        return False

    def cancelar(self):
        """Cancela el examen (marca como no realizado)."""
        self.realizado = False
        self.fecha_resultado = None

    def __str__(self):
        """Devuelve una representación en cadena del examen."""
        estado = "Realizado" if self.realizado else "Pendiente"
        fecha = f" | Resultados: {self.fecha_resultado.strftime('%d/%m/%Y')}" if self.fecha_resultado else ""
        return f"Examen: {self.tipo} | Código: {self.codigo} | Estado: {estado}{fecha}"


class Tecnologo:
    """Representa un tecnólogo que trabaja en el laboratorio."""

    def __init__(self, nombre):
        """Inicializa al tecnólogo con su nombre."""
        self.nombre = nombre

    def procesar_examen(self, examen, accion):
        """Gestiona la realización o cancelación de un examen."""
        if accion == 'realizar':
            return examen.realizar()
        elif accion == 'cancelar':
            examen.cancelar()


class Paciente:
    """Representa un paciente que solicita exámenes en el laboratorio."""

    def __init__(self, nombre, edad, cedula, correo):
        """Inicializa al paciente con nombre, edad, cédula y correo."""
        self.nombre = nombre
        self.edad = edad
        self.cedula = cedula
        self.correo = correo
        self.examenes = []

    def solicitar_examen(self, examen, tecnologo):
        """Permite al paciente solicitar un examen si está disponible."""
        if tecnologo.procesar_examen(examen, 'realizar'):
            self.examenes.append(examen)
            print(f"{self.nombre} ha realizado el examen: {examen.tipo}")
        else:
            print(f"El examen {examen.tipo} ya fue realizado o no está disponible.")

    def cancelar_examen(self, examen, tecnologo):
        """Permite al paciente cancelar un examen realizado."""
        if examen in self.examenes:
            tecnologo.procesar_examen(examen, 'cancelar')
            self.examenes.remove(examen)
            print(f"{self.nombre} ha cancelado el examen: {examen.tipo}")
        else:
            print(f"{self.nombre} no tiene registrado el examen: {examen.tipo}")


# ---------------- Ejemplo de uso ----------------

# Crear un examen
examen1 = Examen("Hemograma", "LAB-001")

# Crear al tecnólogo de laboratorio
tecnologo = Tecnologo("Dra. Mónica")

# Crear un paciente con nombre, edad, cédula y correo
paciente = Paciente("Carlos Jaramillo", 45, "0102030405", "carlos.jaramil@example.com")

# El paciente solicita un examen
paciente.solicitar_examen(examen1, tecnologo)

# El paciente cancela el examen
paciente.cancelar_examen(examen1, tecnologo)
