from database.db_manager import DatabaseManager
from models.user import User

class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager

    
    def login(self, username, password):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, username, role, student_id, instructor_id
                FROM users
                WHERE username = ? AND password = ?
            """, (username, password))
            user_data = cursor.fetchone()

            if user_data:
                user = User(
                    user_id=user_data[0],
                    username=user_data[1],
                    password=password,
                    role=user_data[2],
                    student_id=user_data[3],
                    instructor_id=user_data[4]
                )
                return {
                    "user_id": user.user_id,
                    "username": user.username,
                    "role": user.role,
                    "student_id": user.student_id,
                    "instructor_id": user.instructor_id
                }
            return None

        
    def create_user(self, username, password, role, student_id=None, instructor_id=None):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password, role, student_id,instructor_id)
                    VALUES(?, ?, ?, ?, ?)
            """, (username, password, role, student_id, instructor_id))
                conn.commit()
        except Exception as e:
            raise Exception(f"User could not be created: {e}")
        
    def delete_user(self, username):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
        
    def get_all_users(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, role, student_id, instructor_id FROM users")
            return cursor.fetchall()