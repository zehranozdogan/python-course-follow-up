class Student:
    def __init__(self, student_id, name, surname, department):
        self.student_id = student_id
        self.name = name
        self.surname = surname
        self.department = department

    def get_full_name(self):
        return f"{self.name} {self.surname}"