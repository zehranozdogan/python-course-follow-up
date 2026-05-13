class Grade:
    def __init__(self, student_id, course_id, grade=None, status="enrolled"):
        self.student_id = student_id
        self.course_id = course_id
        self.grade = grade        # 0.0 - 100.0 arası sayısal not
        self.status = status      # 'enrolled', 'passed', 'failed'

    def get_letter_grade(self):
        if self.grade is None:
            return "N/A"
        if self.grade >= 90:
            return "AA"
        elif self.grade >= 85:
            return "BA"
        elif self.grade >= 80:
            return "BB"
        elif self.grade >= 75:
            return "CB"
        elif self.grade >= 70:
            return "CC"
        elif self.grade >= 65:
            return "DC"
        elif self.grade >= 60:
            return "DD"
        elif self.grade >= 50:
            return "FD"
        else:
            return "FF"

    def is_passing(self):
        return self.grade is not None and self.grade >= 60

    def __repr__(self):
        return f"Grade(student={self.student_id}, course={self.course_id}, grade={self.grade}, letter={self.get_letter_grade()})"