from models.schedule import Schedule


class ScheduleService:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_schedule(self, course_id, day_of_week, start_time, end_time, classroom=None):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO schedules (course_id, day_of_week, start_time, end_time, classroom)
                    VALUES (?, ?, ?, ?, ?)
                """, (course_id, day_of_week, start_time, end_time, classroom))
                conn.commit()
        except Exception as e:
            raise Exception(f"Schedule could not be added: {e}")

    def get_schedule_by_course(self, course_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.schedule_id, s.course_id, c.course_name, s.day_of_week,
                       s.start_time, s.end_time, s.classroom
                FROM schedules s
                JOIN courses c ON s.course_id = c.course_id
                WHERE s.course_id = ?
                ORDER BY s.day_of_week, s.start_time
            """, (course_id,))
            return cursor.fetchall()

    def get_schedule_by_student(self, student_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.schedule_id, c.course_name, c.course_code, s.day_of_week,
                       s.start_time, s.end_time, s.classroom
                FROM schedules s
                JOIN courses c ON s.course_id = c.course_id
                JOIN enrollments e ON e.course_id = c.course_id
                WHERE e.student_id = ?
                ORDER BY s.day_of_week, s.start_time
            """, (student_id,))
            return cursor.fetchall()

    def get_schedule_by_instructor(self, instructor_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.schedule_id, c.course_name, c.course_code, s.day_of_week,
                       s.start_time, s.end_time, s.classroom
                FROM schedules s
                JOIN courses c ON s.course_id = c.course_id
                WHERE c.instructor_id = ?
                ORDER BY s.day_of_week, s.start_time
            """, (instructor_id,))
            return cursor.fetchall()

    def update_schedule(self, schedule_id, day_of_week, start_time, end_time, classroom=None):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE schedules
                SET day_of_week = ?, start_time = ?, end_time = ?, classroom = ?
                WHERE schedule_id = ?
            """, (day_of_week, start_time, end_time, classroom, schedule_id))
            conn.commit()

    def delete_schedule(self, schedule_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM schedules WHERE schedule_id = ?", (schedule_id,))
            conn.commit()