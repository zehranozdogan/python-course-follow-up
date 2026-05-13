class CourseService:
    def __init__(self, db_manager):
        self.db = db_manager


    def add_course(self, course_id, course_name, course_code, credit, instructor_id = None):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO courses (course_id, course_name, course_code, credit, instructor_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (course_id, course_name, course_code, credit, instructor_id))
                conn.commit()
        except Exception as e:
            raise Exception(f"Course could not be added: {e}")


    def get_all_courses(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses ORDER BY course_id")
            return cursor.fetchall()
        
    def get_course_by_id(self, course_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses WHERE course_id=?", (course_id,))
            return cursor.fetchone()
        
    
    def get_courses_by_instructor(self, instructor_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM courses
                WHERE instructor_id = ?
                ORDER BY course_id
            """, (instructor_id,))
            return cursor.fetchall()
        

    def update_course(self, course_id, course_name, course_code, credit, instructor_id = None):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE courses
                    SET course_name = ?, course_code = ?, credit = ?, instructor_id = ?
                    WHERE course_id = ?
                """, (course_name, course_code, credit, instructor_id, course_id))
                conn.commit()
        except Exception as e:
            raise Exception(f"Course could not be updated: {e}")

    def delete_course(self, course_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
            conn.commit()
    
    def assign_instructor(self, course_id, instructor_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE courses SET instructor_id = ?
                WHERE course_id = ?
            """, (instructor_id, course_id))
            conn.commit()