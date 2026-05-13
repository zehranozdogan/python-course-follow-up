class InstructorService:
    def __init__(self, db_manager):
        self.db = db_manager


    def add_instructor(self, instructor_id, name, surname, branch):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO instructors (instructor_id, name, surname, branch)
                    VALUES (?, ?, ?, ?)
                """, (instructor_id, name, surname, branch))
                conn.commit()
        except Exception as e:
            raise Exception(f"Instructor could not be added: {e}")

    def get_all_instructors(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM instructors ORDER BY instructor_id")
            return cursor.fetchall()
        
    def get_instructor_by_id(self, instructor_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM instructors WHERE instructor_id = ?", (instructor_id,))
            return cursor.fetchone()

    def update_instructor(self, instructor_id, name, surname, branch):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE instructors
                SET name = ?, surname = ?, branch = ?
                WHERE instructor_id = ?
            """, (name, surname, branch, instructor_id))
            conn.commit()

    def delete_instructor(self, instructor_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (instructor_id,))
            conn.commit()