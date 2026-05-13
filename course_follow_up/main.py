import tkinter as tk
from database.db_manager import DatabaseManager
from services.auth_manager import AuthManager
from services.student_service import StudentService
from services.instructor_service import InstructorService
from services.course_service import CourseService
from services.enrollment_service import EnrollmentService
from services.grade_service import GradeService
from services.report_service import ReportService
from services.attendance_service import AttendanceService
from ui.LoginWindow import LoginWindow
from services.message_service import MessageService
from services.schedule_service import ScheduleService
from services.notification_service import NotificationService

def main():
    # Database'i başlatıyoruz
    db = DatabaseManager()

    auth = AuthManager(db)
    student_service = StudentService(db)
    instructor_service = InstructorService(db)
    course_service = CourseService(db)
    enrollment_service = EnrollmentService(db)
    grade_service = GradeService(db)
    report_service = ReportService(db)
    attendance_service = AttendanceService(db)
    message_service = MessageService(db)
    schedule_service = ScheduleService(db)
    notification_service = NotificationService(db)
    
    root = tk.Tk()
    root.title("COURSE FOLLOW UP")
    root.geometry("1240x850")
    root.resizable(False, False)


    services = {
        "db":  db,
        "auth": auth,
        "student": student_service,
        "instructor": instructor_service,
        "course": course_service,
        "enrollment": enrollment_service,
        "grade": grade_service,
        "attendance": attendance_service,
        "report": report_service,
        "message": message_service,
        "schedule": schedule_service,
        "notification": notification_service,
    }

    def on_login_success(user_info):
        root.on_login_success_callback = on_login_success
        for widget in root.winfo_children():
            widget.destroy()


        role = user_info.get("role")

        if role == "admin":
            from ui.AdminWindow import AdminWindow
            AdminWindow(root, user_info, services)
        elif role == "teacher":
            from ui.TeacherWindow import TeacherWindow
            TeacherWindow(root, user_info, services)
        else:
            from ui.StudentWindow import StudentWindow
            StudentWindow(root, user_info, services)
    
    root.on_login_success_callback = on_login_success
    LoginWindow(root,on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main()