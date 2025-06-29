# Programa que gestiona información básica de un registro estudiantil
# Se almacenan y muestran datos personales y académicos de un estudiante

# Función para crear un registro de estudiante
def registrar_estudiante(nombre, edad, promedio, esta_activo):
    estudiante = {
        'nombre': nombre,               # string
        'edad': edad,                   # int
        'promedio': promedio,           # float
        'activo': esta_activo           # boolean
    }
    return estudiante

# Registro de un estudiante
nombre_estudiante = "Darwin Lopez"
edad_estudiante = 25
promedio_estudiante = 8.7
estado_actividad = True

registro = registrar_estudiante(nombre_estudiante, edad_estudiante, promedio_estudiante, estado_actividad)

# Mostrar información del registro
print("Registro del estudiante:")
print(f"Nombre: {registro['nombre']}")
print(f"Edad: {registro['edad']} años")
print(f"Promedio: {registro['promedio']}")
print(f"¿Activo?: {registro['activo']}")
