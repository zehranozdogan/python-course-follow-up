from models.student import Student

class StudentService:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_student(self, student_id, name, surname, department):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO students (student_id, name, surname, department)
                    VALUES (?, ?, ?, ?)
                """, (student_id, name, surname, department))
                conn.commit()
        except Exception as e:
            raise Exception(f"Student could not be added: {e}")
        
    def get_all_students(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY student_id")
            return cursor.fetchall()
    
    def get_student_by_id(self, student_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            if row:
                return Student(row[0], row[1], row[2], row[3])
            return None
        
    
    def get_students_by_course(self, course_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, s.surname, s.department
                FROM students s
                JOIN enrollments e ON s.student_id = e.student_id
                WHERE e.course_id = ?
                ORDER BY s.student_id
            """, (course_id,))
            return cursor.fetchall()

    def update_student(self, student_id, name, surname, department):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE students
                SET name = ?, surname = ?, department = ?
                WHERE student_id = ?
            """, (name, surname, department, student_id))
            conn.commit()

    def delete_student(self, student_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            conn.commit()