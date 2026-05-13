import tkinter as tk
from tkinter import ttk, messagebox
from services.enrollment_service import EnrollmentService
from services.student_service import StudentService
from services.course_service import CourseService


class EnrollmentWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Enrollment Management")
        self.root.geometry("950x600")

        self.enrollment_service = EnrollmentService()
        self.student_service = StudentService()
        self.course_service = CourseService()

        self.student_map = {}
        self.course_map = {}

        self.create_widgets()
        self.load_options()
        self.load_enrollments()

    def create_widgets(self):
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Enrollment Management", font=("Arial", 18, "bold")).pack(pady=10)

        form = ttk.LabelFrame(container, text="Enroll Student To Course", padding=15)
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="Student:").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.student_combo = ttk.Combobox(form, width=45, state="readonly")
        self.student_combo.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(form, text="Course:").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        self.course_combo = ttk.Combobox(form, width=45, state="readonly")
        self.course_combo.grid(row=1, column=1, padx=5, pady=8)

        button_frame = ttk.Frame(container)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Add Enrollment", command=self.add_enrollment).grid(row=0, column=0, padx=8)
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).grid(row=0, column=1, padx=8)

        table_frame = ttk.Frame(container)
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = ("Student ID", "Student Name", "Course ID", "Course Name", "Course Code")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=160)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_options(self):
        students = self.student_service.get_all_students()
        courses = self.course_service.get_all_courses()

        self.student_map = {
            f"{student[0]} - {student[1]} {student[2]}": student[0]
            for student in students
        }

        self.course_map = {
            f"{course[0]} - {course[1]} ({course[2]})": course[0]
            for course in courses
        }

        self.student_combo["values"] = list(self.student_map.keys())
        self.course_combo["values"] = list(self.course_map.keys())

    def add_enrollment(self):
        selected_student = self.student_combo.get().strip()
        selected_course = self.course_combo.get().strip()

        if not selected_student or not selected_course:
            messagebox.showwarning("Missing Information", "Please select both a student and a course.")
            return

        student_id = self.student_map[selected_student]
        course_id = self.course_map[selected_course]

        try:
            self.enrollment_service.enroll_student(student_id, course_id)
            messagebox.showinfo("Success", "Enrollment added successfully.")
            self.clear_fields()
            self.load_enrollments()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_enrollments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for enrollment in self.enrollment_service.get_all_enrollments():
            self.tree.insert("", tk.END, values=enrollment)

    def clear_fields(self):
        self.student_combo.set("")
        self.course_combo.set("")