class User:
    def __init__(self, user_id, username, password, role, student_id=None, instructor_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role  # 'admin', 'teacher', 'student'
        self.student_id = student_id
        self.instructor_id = instructor_id

    def __repr__(self):
        return f"[{self.user_id}] {self.username} - {self.role}"