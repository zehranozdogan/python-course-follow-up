class AttendanceService:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_attendance(self, student_id, course_id, total_hours, absent_hours, attendance_date=None):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO attendance (student_id, course_id, total_hours, absent_hours, attendance_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, course_id, total_hours, absent_hours, attendance_date))
                conn.commit()
        except Exception as e:
            raise Exception(f"Attendance could not be added: {e}")

    def get_attendance_by_student(self, student_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.course_code,
                    c.course_name,
                    a.total_hours,
                    a.absent_hours,
                    CASE 
                        WHEN a.total_hours = 0 THEN 100
                        ELSE ROUND(((a.total_hours - a.absent_hours) * 100.0 / a.total_hours), 2)
                    END AS attendance_percentage
                FROM attendance a
                JOIN courses c ON a.course_id = c.course_id
                WHERE a.student_id = ?
                ORDER BY c.course_id
            """, (student_id,))
            return cursor.fetchall()

    def get_attendance_by_course(self, course_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.student_id,
                    s.name,
                    s.surname,
                    c.course_name,
                    a.total_hours,
                    a.absent_hours,
                    CASE 
                        WHEN a.total_hours = 0 THEN 100
                        ELSE ROUND(((a.total_hours - a.absent_hours) * 100.0 / a.total_hours), 2)
                    END AS attendance_percentage
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN courses c ON a.course_id = c.course_id
                WHERE a.course_id = ?
                ORDER BY s.student_id
            """, (course_id,))
            return cursor.fetchall()

    def update_attendance(self, attendance_id, total_hours, absent_hours, attendance_date=None):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE attendance
                SET total_hours = ?, absent_hours = ?, attendance_date = ?
                WHERE attendance_id = ?
            """, (total_hours, absent_hours, attendance_date, attendance_id))
            conn.commit()

    def delete_attendance(self, attendance_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance WHERE attendance_id = ?", (attendance_id,))
            conn.commit()

    def get_all_attendance(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    a.attendance_id,
                    s.student_id,
                    s.name || ' ' || s.surname AS student_name,
                    c.course_id,
                    c.course_name,
                    a.total_hours,
                    a.absent_hours,
                    CASE 
                        WHEN a.total_hours = 0 THEN 100
                        ELSE ROUND(((a.total_hours - a.absent_hours) * 100.0 / a.total_hours), 2)
                    END AS attendance_percentage,
                    a.attendance_date
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN courses c ON a.course_id = c.course_id
                ORDER BY s.student_id, c.course_id
            """)
            return cursor.fetchall()