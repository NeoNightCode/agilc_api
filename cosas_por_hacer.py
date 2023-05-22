def mostrar_lista_tareas(lista_tareas):
    print("Lista de tareas por hacer:")
    print("--------------------------")
    for tarea in lista_tareas:
        print("- " + tarea + '\n')
    print("--------------------------")

# Lista de tareas por hacer
lista_tareas = [
    "Crear nueva colección resultados (Equipo V, Equipo L, Puntuación V, Puntuación L, Competición, Jornada, Fecha)",
    "Generar calendario al crear competición",
    "Crear script crear competiciones",
    "Crear rutas API"
]

# Mostrar la lista de tareas por hacer
mostrar_lista_tareas(lista_tareas)
