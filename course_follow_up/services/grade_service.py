from models.grade import Grade

class GradeService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_grades_by_student(self, student_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.course_name, c.course_code, e.grade, e.status
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.student_id = ?
                ORDER BY c.course_id
            """, (student_id,))
            rows = cursor.fetchall()
            grades = []
            for row in rows:
                g = Grade(student_id = student_id, course_id = row[1], grade = row[2], status = row[3])
                grades.append((row[0], row[1], g.grade, g.get_letter_grade(), g.status))
            return grades
    
    def get_grades_by_course(self, course_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, s.surname, e.grade, e.status
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                WHERE e.course_id = ?
                ORDER BY s.student_id
            """, (course_id,))
            return cursor.fetchall()

    def calculate_gpa(self, student_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.grade, c.credit
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.student_id = ? AND e.grade IS NOT NULL
            """, (student_id,))
            rows = cursor.fetchall()
            
            if not rows:
                return 0.0
            
            total_points = 0
            total_credits = 0
            for grade, credit in rows:
                if grade >= 90:
                    letter_points = 4.0
                elif grade >= 85:
                    letter_points = 3.5
                elif grade >= 80:
                    letter_points = 3.0
                elif grade >= 75:
                    letter_points = 2.5
                elif grade >= 70:
                    letter_points = 2.0
                elif grade >= 65:
                    letter_points = 1.5
                elif grade >= 60:
                    letter_points = 1.0
                else:
                    letter_points = 0.0
                total_points += letter_points * credit
                total_credits += credit
            
            return round(total_points / total_credits, 2) if total_credits > 0 else 0.0