class Course:

    def __init__(self, name, duration, link):
        self.name = name 
        self.duration = duration 
        self.link = link

    def __repr__(self):
        return f"{self.name} [{self.duration} horas] ({self.link})"

courses = [
    Course("Introduccion a Lunix", 15, "https://hack4u.io/cursos/introduccion-a-linux/"),
    Course("Personalizacion de Lunix", 3, "https://hack4u.io/cursos/configuracion-de-entorno-en-linux/"),
    Course("Introduccion al Hacking", 53, "https://hack4u.io/cursos/introduccion-al-hacking/")
]

def list_courses():
    for course in courses:
        print(course)

def search_course_by_name(name):
    for course in courses:
        if course.name == name:
            return course

    return None
