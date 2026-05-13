import sqlite3


class DatabaseManager:
    def __init__(self, db_name="course_follow_up.db"):
        self.db_name = db_name
        self.create_tables()
        self.create_default_admin()
        self.seed_data() 

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    department TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    course_id INTEGER PRIMARY KEY,
                    course_name TEXT NOT NULL,
                    course_code TEXT NOT NULL UNIQUE,
                    credit INTEGER NOT NULL,
                    instructor_id INTEGER DEFAULT NULL,
                    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE SET NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS instructors (
                    instructor_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    branch TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enrollments (
                    student_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    grade REAL DEFAULT NULL,
                    status TEXT DEFAULT 'enrolled',      
                    PRIMARY KEY (student_id, course_id),
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    total_hours INTEGER DEFAULT 0,
                    absent_hours INTEGER DEFAULT 0,
                    attendance_date TEXT DEFAULT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            student_id INTEGER DEFAULT NULL,
            instructor_id INTEGER DEFAULT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE CASCADE
            )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    subject TEXT DEFAULT NULL,
                    body TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    sent_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER NOT NULL,
                    day_of_week TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    classroom TEXT DEFAULT NULL,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)

            conn.commit()


    def create_default_admin(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO users(username, password, role)
                           VALUES('admin', 'admin123', 'admin')
                           
            """)
            conn.commit()
    
    def seed_data(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            
            # 1. Örnek Hocaları Ekle (INSERT OR IGNORE ile mükerrer kaydı önleriz)
            instructors = [
                (101, "Ahmet", "Yılmaz", "Computer Engineering"),
                (102, "Ayşe", "Kaya", "Computer Engineering"),
                (103, "Mehmet", "Demir", "Electrical Engineering"),
                (104, "Fatma", "Çelik", "Law"),
                (105, "Can", "Öztürk", "Business")
            ]
            cursor.executemany("INSERT OR IGNORE INTO instructors VALUES (?,?,?,?)", instructors)

            # 2. Hocalar için User hesapları (Şifreleri 'pass123')
            for ins in instructors:
                username = f"hoca.{ins[1].lower()}"
                cursor.execute("""
                    INSERT OR IGNORE INTO users (username, password, role, instructor_id)
                    VALUES (?, 'pass123', 'instructor', ?)
                """, (username, ins[0]))

            # 3. Bölümlere Göre Dersler ve Sectionlar
            # (Adı, Kodu, Kredi, Hocası)
            courses = [
                (1, "Algorithms-A", "CENG201-A", 5, 101),
                (2, "Algorithms-B", "CENG201-B", 5, 102),
                (3, "Database-A", "CENG301-A", 4, 101),
                (4, "Database-B", "CENG301-B", 4, 102),
                (5, "Circuit Theory", "EE101", 5, 103),
                (6, "Criminal Law", "LAW202", 4, 104),
                (7, "Marketing", "BUS105", 3, 105)
            ]
            cursor.executemany("INSERT OR IGNORE INTO courses VALUES (?,?,?,?,?)", courses)

            # 4. Ders Programları (Schedule) - Çakışma Olmayacak Şekilde
            # (CourseID, Day, Start, End, Room)
            schedules = [
                (1, "Monday",    "09:00", "12:00", "Lab 1"),   # Algo-A    → Hoca Ahmet
                (2, "Tuesday",   "09:00", "12:00", "Lab 2"),   # Algo-B    → Hoca Ayşe
                (3, "Wednesday", "09:00", "12:00", "C-101"),   # DB-A      → Hoca Ahmet
                (4, "Thursday",  "09:00", "12:00", "C-102"),   # DB-B      → Hoca Ayşe
                (5, "Monday",    "13:00", "16:00", "EE-Lab"),  # Circuit   → Hoca Mehmet
                (6, "Friday",    "10:00", "13:00", "Law-A"),   # Criminal  → Hoca Fatma
                (7, "Wednesday", "14:00", "17:00", "B-201"),   # Marketing → Hoca Can
            ]
            
            cursor.executemany("INSERT OR IGNORE INTO schedules (course_id, day_of_week, start_time, end_time, classroom) VALUES (?,?,?,?,?)", schedules)

            conn.commit()