# Hack4u Academy Courses Library

Una biblioteca Python para consultar cursos de la academia Hack4U.

## Cursos disponibles:

- Introducción a Linux [15 horas]
- Personalización de Linux [3 horas]
- Introducción al Hacking [53 horas]


## Instalación
Instala el paquete utilizando 'pip3':

```python3
pip3 install hack4u
```

## Uso básico

### Listar todos los cursos

```python
from hack4u import list_courses

for course in list_courses():
    print(course)
```

### Calcular duración total de los cursos

```python3
from hack4u.utils import total_duration

print(f"Duración total: {total_duration()} horas")
```

