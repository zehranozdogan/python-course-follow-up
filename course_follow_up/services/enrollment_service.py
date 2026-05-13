import sqlite3

class EnrollmentService:
    def __init__(self, db_manager):
        self.db = db_manager

    def enroll_student(self, student_id, course_id):
        # 1. Kayıt olunmak istenen dersin saatini al
        new_course_schedule = self.get_course_schedule(course_id)
        if not new_course_schedule:
            raise Exception("Bu dersin programı henüz tanımlanmamış.")

        # 2. Öğrencinin hali hazırda kayıtlı olduğu derslerin saatlerini al
        student_current_schedules = self.get_student_full_schedule(student_id)

        # 3. Çakışma Kontrolü (Conflict Check)
        for new_s in new_course_schedule:
            # new_s: (day, start, end)
            for current_s in student_current_schedules:
                # current_s: (day, start, end, course_name)
                if new_s[0] == current_s[0]: # Aynı gün mü?
                    # Saat çakışması mantığı: (StartA < EndB) AND (EndA > StartB)
                    if (new_s[1] < current_s[2]) and (new_s[2] > current_s[1]):
                        raise Exception(f"ÇAKIŞMA: Bu ders '{current_s[3]}' dersi ile çakışıyor!")

        # 4. Çakışma yoksa kaydet
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO enrollments (student_id, course_id, status)
                    VALUES (?, ?, 'enrolled')
                """, (student_id, course_id))
                conn.commit()
        except sqlite3.IntegrityError:
            raise Exception("Öğrenci zaten bu derse/şubeye kayıtlı.")

    def get_course_schedule(self, course_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT day_of_week, start_time, end_time FROM schedules WHERE course_id = ?", (course_id,))
            return cursor.fetchall()

    def get_student_full_schedule(self, student_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.day_of_week, s.start_time, s.end_time, c.course_name
                FROM schedules s
                JOIN courses c ON s.course_id = c.course_id
                JOIN enrollments e ON e.course_id = c.course_id
                WHERE e.student_id = ?
            """, (student_id,))
            return cursor.fetchall()
            
    # Mevcut diğer metodların (get_enrollments_by_course vb.) burada kalmaya devam etmeli
    def get_enrollments_by_course(self, course_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, s.surname, s.department, e.grade, e.status
                FROM students s
                JOIN enrollments e ON s.student_id = e.student_id
                WHERE e.course_id = ?
            """, (course_id,))
            return cursor.fetchall()

    def update_grade(self, student_id, course_id, grade):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE enrollments SET grade = ? 
                WHERE student_id = ? AND course_id = ?
            """, (grade, student_id, course_id))
            conn.commit()
    
    def get_enrollments_by_student(self, student_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.course_id, c.course_name, c.course_code, c.credit, e.grade, e.status
                FROM courses c
                JOIN enrollments e ON c.course_id = e.course_id
                WHERE e.student_id = ?
            """, (student_id,))
            return cursor.fetchall()
        
    def get_all_enrollments(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.student_id, s.name, s.surname, c.course_name, e.grade, e.status
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                JOIN courses c ON e.course_id = c.course_id
            """)
            return cursor.fetchall()