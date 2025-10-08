class Course:
	def __init__(self, names, duration, link):
		self.names = names
		self.duration = duration
		self.link = link

	def __repr__(self):
		return f'''\n Nombre: {self.names}, [Duracion: {self.duration}], (Link: {self.link})\n'''

	def list_courses():
		for course in courses:
			print(course)

	def search_course_by_name(names):
		encontrado = False
		for course in courses:
			if course.names == names:
				print(course)
				encontrado = True
		if not encontrado:
			print("[!] Curso no encontrado")

c1 = Course("Introduccion a linux", 15, "https://hack4u.io/cursos/introduccion-a-linux/")
c2 = Course("Personalizacion de linux", 3, "https://hack4u.io/cursos/personalizacion-de-entorno-en-linux/")
c3 = Course("Python Ofensivo", 35, "https://hack4u.io/cursos/python-ofensivo/")

courses = []
courses.append(c1)
courses.append(c2)
courses.append(c3)


print("---repr---")
print(courses)
print("----Search By name----")
Course.search_course_by_name("Introduccion a linux")
print("----List all Courses----")
Course.list_courses()

