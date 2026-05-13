class Instructor:
    def __init__(self, instructor_id, name, surname, branch):
        self.instructor_id = instructor_id
        self.name = name
        self.surname = surname
        self.branch = branch

    def get_full_name(self):
        return f"{self.name} {self.surname}"