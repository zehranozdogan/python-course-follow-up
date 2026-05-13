class ReportService:
    def __init__(self,db_manager):
        self.db = db_manager

    def get_student_report(self, student_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, s.surname, s.department, c.course_name, c.course_code, c.credit, e.grade, e.status
                FROM students s
                JOIN enrollments e ON s.student_id = e.student_id
                JOIN courses c ON e.course_id = c.course_id
                WHERE s.student_id = ?
            """, (student_id,))
            return cursor.fetchall()

    def get_course_report(self, course_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.course_name, c.course_code,
                        s.student_id, s.name, s.surname,
                        e.grade, e.status
                FROM courses c
                JOIN enrollments e ON c.course_id = e.course_id
                JOIN students s ON e.student_id = s.student_id
                WHERE c.course_id = ?
                ORDER BY s.student_id
            """, (course_id,))
            return cursor.fetchall()

    def get_summary(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM instructors")
            total_instructors = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM courses")
            total_courses = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM enrollments")
            total_enrollments = cursor.fetchone()[0]
            return{
                "total_students": total_students,
                "total_instructors": total_instructors,
                "total_courses": total_courses,
                "total_enrollments": total_enrollments
            }
