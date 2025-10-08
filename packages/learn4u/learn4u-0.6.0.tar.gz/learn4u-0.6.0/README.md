#Hack4u Academy Courses Library

Una biblioteca Python para consultar cursos de la acedemia Hack4u

##Cursos disponibles:

- Introduccion a linux [15]
- Personalizacion de linux [3]
- Python Ofensivo [35]

##Instalación

Instala el paquete `pip3`

```python3
pip3 install hack4u
```
#Uso basico

### Listar todos los cursos

```python3
from hack4u import list_courses

Course.list_courses():
```

###Obtener un curso por nombre
```python3
from hack4u import search_course_by_name

c = search_course_by_name("Introducion a linux")
print(c)
```

### Calcular duracion total de los cursos

```python3
from hack4u.utils import total_duration

print(f"Duracion total: {total_duration() horas}")
```

