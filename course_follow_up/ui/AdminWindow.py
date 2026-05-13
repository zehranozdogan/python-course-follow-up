import tkinter as tk
from tkinter import ttk, messagebox
try:
    from ui.SharedComponents import StudentProfileView
except ImportError:
    from SharedComponents import StudentProfileView


class AdminWindow:
    def __init__(self, root, user_info, services):
        self.root = root
        self.user_info = user_info
        self.services = services
        self.student_service = services["student"]
        self.instructor_service = services["instructor"]
        self.course_service = services["course"]
        self.enrollment_service = services["enrollment"]
        self.report_service = services["report"]
        self.display_name = user_info.get('username', 'Admin').upper()
        self.ready_schedule = []
        self.all_classrooms = [
            {"id": "A-101", "type": "Classroom", "capacity": "40"},
            {"id": "LAB-2", "type": "Computer Lab", "capacity": "30"}
        ]
        self.colors = {
            "bg": "#F8FAFC", "sidebar": "#1E293B", "accent": "#3B82F6",
            "card": "#FFFFFF", "text_dark": "#0F172A", "text_light": "#64748B",
            "success": "#10B981", "danger": "#EF4444"
        }
        self.root.configure(bg=self.colors["bg"])
        self.setup_sidebar()
        self.main_content = tk.Frame(self.root, bg=self.colors["bg"], padx=30, pady=20)
        self.main_content.pack(side="left", fill="both", expand=True)
        self.show_dashboard()

    def create_btn(self, parent, text, color, command, px=20):
        btn = tk.Label(parent, text=text, bg=color, fg="white", font=("Arial", 9, "bold"), pady=10, padx=px, cursor="hand2")
        btn.bind("<Button-1>", lambda e: command())
        return btn

    def create_quick_btn(self, parent, text, color, command):
        btn = tk.Label(parent, text=text, bg=color, fg="white", font=("Arial", 9, "bold"), pady=12, cursor="hand2")
        btn.bind("<Button-1>", lambda e: command())
        return btn

    def setup_sidebar(self):
        sidebar = tk.Frame(self.root, bg=self.colors["sidebar"], width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text=f"SYSTEM ADMIN\n{self.display_name}", font=("Arial", 11, "bold"),
                 bg=self.colors["sidebar"], fg="white", pady=40).pack()
        menu = [
            ("Dashboard", self.show_dashboard),
            ("Student Management", self.show_students),
            ("Teacher Management", self.show_teachers),
            ("Course Management", self.show_courses),
            ("Enrollments", self.show_enrollments),
            ("Broadcast Messages", self.show_announcements),
            ("Logout", self.logout)
        ]
        for text, cmd in menu:
            btn = tk.Label(sidebar, text=text, font=("Arial", 10), bg=self.colors["sidebar"],
                           fg="#94A3B8", pady=15, padx=30, anchor="w")
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#334155", fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors["sidebar"], fg="#94A3B8"))

    def clear_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    # --- DASHBOARD ---
    def show_dashboard(self):
        self.clear_content()
        summary = self.report_service.get_summary()

        header = tk.Frame(self.main_content, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="SYSTEM OVERVIEW", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text_dark"]).pack(side="left")

        stats_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        stats_frame.pack(fill="x", pady=10)
        stats = [
            ("TOTAL STUDENTS", str(summary["total_students"]), self.colors["accent"]),
            ("TOTAL TEACHERS", str(summary["total_instructors"]), self.colors["success"]),
            ("ACTIVE COURSES", str(summary["total_courses"]), "#8B5CF6"),
            ("SYSTEM STATUS", "ONLINE", self.colors["success"])
        ]
        for title, val, color in stats:
            card = tk.Frame(stats_frame, bg="white", padx=25, pady=20,
                            highlightthickness=1, highlightbackground="#E2E8F0")
            card.pack(side="left", expand=True, fill="both", padx=5)
            tk.Label(card, text=title, font=("Arial", 8, "bold"), bg="white", fg=self.colors["text_light"]).pack()
            tk.Label(card, text=val, font=("Arial", 18, "bold"), bg="white", fg=color).pack(pady=(5, 0))

        bottom_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        bottom_frame.pack(fill="both", expand=True, pady=20)

        log_frame = tk.Frame(bottom_frame, bg="white", padx=20, pady=20,
                             highlightthickness=1, highlightbackground="#E2E8F0")
        log_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(log_frame, text="RECENT ACTIVITIES", font=("Arial", 10, "bold"),
                 bg="white", fg=self.colors["text_dark"]).pack(anchor="w", pady=(0, 15))
        logs = [
            "• System is running.",
            f"• Total {summary['total_students']} students registered.",
            f"• Total {summary['total_courses']} courses available.",
            f"• Total {summary['total_enrollments']} enrollments made."
        ]
        for log in logs:
            tk.Label(log_frame, text=log, font=("Arial", 9), bg="white",
                     fg=self.colors["text_light"], pady=8).pack(anchor="w")

        action_frame = tk.Frame(bottom_frame, bg="white", padx=20, pady=20,
                                highlightthickness=1, highlightbackground="#E2E8F0", width=300)
        action_frame.pack(side="right", fill="y", expand=False)
        action_frame.pack_propagate(False)
        tk.Label(action_frame, text="QUICK ACTIONS", font=("Arial", 10, "bold"),
                 bg="white", fg=self.colors["text_dark"]).pack(anchor="w", pady=(0, 15))
        self.create_quick_btn(action_frame, "+ Add New Student", self.colors["accent"], self.show_add_student_form).pack(fill="x", pady=8)
        self.create_quick_btn(action_frame, "+ Add New Teacher", self.colors["success"], self.show_add_teacher_form).pack(fill="x", pady=8)
        self.create_quick_btn(action_frame, "Assign Teacher", self.colors["success"], self.show_teacher_assignment).pack(fill="x", pady=8)
        self.create_quick_btn(action_frame, "Enroll Student", self.colors["accent"], self.show_student_enrollment).pack(fill="x", pady=8)
        self.create_quick_btn(action_frame, "Send Announcement", self.colors["sidebar"], self.show_announcements).pack(fill="x", pady=8)

    # --- STUDENT MANAGEMENT ---
    def show_students(self):
        self.clear_content()
        tk.Label(self.main_content, text="STUDENT MANAGEMENT", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        cols = ("ID", "Name", "Surname", "Department", "Action")
        self.tree = ttk.Treeview(self.main_content, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=False)

        students = self.student_service.get_all_students()
        for s in students:
            self.tree.insert("", "end", values=(s[0], s[1], s[2], s[3], "View More →"))

        self.tree.bind("<ButtonRelease-1>", self.handle_table_click)

        btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text="+ ADD STUDENT", bg=self.colors["success"], fg="white",
                  font=("Arial", 9, "bold"), command=self.show_add_student_form,
                  padx=15, pady=8).pack(side="left", padx=5)
        tk.Button(btn_f, text="ENROLL TO COURSE", bg=self.colors["accent"], fg="white",
                  font=("Arial", 9, "bold"), command=self.show_student_enrollment,
                  padx=15, pady=8).pack(side="left", padx=5)
        tk.Button(btn_f, text="REMOVE SELECTED", bg=self.colors["danger"], fg="white",
                  font=("Arial", 9, "bold"), command=self.remove_student_logic,
                  padx=15, pady=8).pack(side="right", padx=5)

    def handle_table_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        if self.tree.identify_column(event.x) == "#5":
            s_id = self.tree.item(item[0], "values")[0]
            self.show_student_profile(s_id)

  
    def export_student_pdf(self, student, gpa, enrollments):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas as pdf_canvas
            from tkinter import filedialog

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"transcript_{student.name}_{student.surname}.pdf"
            )
            if not file_path:
                return

            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(width / 2, height - 60, "ACADEMIC TRANSCRIPT")
            c.setFont("Helvetica", 12)
            c.drawCentredString(width / 2, height - 85, "University Course Follow-Up System")
            c.line(50, height - 100, width - 50, height - 100)

            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, height - 130, f"Name: {student.name} {student.surname}")
            c.drawString(50, height - 150, f"Student ID: {student.student_id}")
            c.drawString(50, height - 170, f"Department: {student.department}")
            c.drawString(50, height - 190, f"Cumulative GPA: {gpa}")
            c.line(50, height - 205, width - 50, height - 205)

            y = height - 230
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "Course Code")
            c.drawString(160, y, "Course Name")
            c.drawString(370, y, "Credit")
            c.drawString(430, y, "Grade")
            c.drawString(490, y, "Status")
            c.line(50, y - 5, width - 50, y - 5)

            c.setFont("Helvetica", 10)
            y -= 25
            for e in enrollments:
                c.drawString(50, y, str(e[2]))
                c.drawString(160, y, str(e[1])[:25])
                c.drawString(370, y, str(e[3]))
                c.drawString(430, y, str(e[4]) if e[4] else "N/A")
                c.drawString(490, y, str(e[5]))
                y -= 20
                if y < 80:
                    c.showPage()
                    y = height - 60

            c.line(50, y - 5, width - 50, y - 5)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y - 25, f"Cumulative GPA: {gpa}")
            c.save()
            messagebox.showinfo("Success", f"Transcript saved!")

        except ImportError:
            messagebox.showerror("Error", "pip install reportlab")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def show_student_profile(self, student_id):
        from ui.SharedComponents import StudentDetailView
        StudentDetailView.show(
            self.main_content, student_id, self.services,
            {"bg": self.colors["bg"], "sidebar": self.colors["sidebar"]},
            self.show_students
        )


    def show_add_student_form(self):
        self.clear_content()
        tk.Label(self.main_content, text="REGISTER NEW STUDENT", font=("Arial", 18, "bold"),
             bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        form_f = tk.Frame(self.main_content, bg="white", padx=30, pady=30,
                      highlightthickness=1, highlightbackground="#E2E8F0")
        form_f.pack(fill="x")

        depts = ["Computer Engineering", "Electrical Engineering", "Mechanical Engineering", "Law", "Architecture", "Business"]
        self.entries = {}
        fields = [("First Name:", "entry"), ("Last Name:", "entry"), ("TC Number:", "entry"), ("Department:", "combo"), ("Address:", "entry")]

        for i, (text, f_type) in enumerate(fields):
            tk.Label(form_f, text=text, bg="white", font=("Arial", 9, "bold")).grid(row=i, column=0, sticky="w", pady=10)
            if f_type == "combo":
                ent = ttk.Combobox(form_f, values=depts, state="readonly", width=37)
                ent.set("Select Department")
            else:
                ent = tk.Entry(form_f, width=40)
            ent.grid(row=i, column=1, padx=20, pady=10)
            self.entries[text] = ent

        btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text="SAVE STUDENT", bg=self.colors["success"], fg="white",
              font=("Arial", 9, "bold"), command=self.save_student_logic, padx=20, pady=10).pack(side="left")
        tk.Button(btn_f, text="CANCEL", bg=self.colors["danger"], fg="white",
              font=("Arial", 9, "bold"), command=self.show_students, padx=20, pady=10).pack(side="right")
  

    def save_student_logic(self):
        first = self.entries["First Name:"].get().strip()
        last = self.entries["Last Name:"].get().strip()
        tc = self.entries["TC Number:"].get().strip()
        dept = self.entries["Department:"].get()

        if not first or not last or not tc or dept == "Select Department":
            messagebox.showwarning("Missing Data", "Please fill all fields and select a department!")
            return

        # TC'nin şifre olması için şifreyi burada belirliyoruz
        password = tc 

        # Sistem otomatik unique bir ID atıyor (Öğrenci Numarası gibi)
        import random
        while True:
            student_id = random.randint(2421000, 2421999)
            if not self.student_service.get_student_by_id(student_id):
                break

        try:
            # Öğrenciyi veritabanına ekle
            self.student_service.add_student(student_id, first, last, dept)

            # Kullanıcı adı oluştur (boşluksuz ve küçük harf)
            username = f"{first.lower().replace(' ', '')}.{last.lower().replace(' ', '')}"
            
            # Auth servisine ekle (Şifre TC olarak gidiyor)
            self.services["auth"].create_user(username, password, "student", student_id=student_id)

            messagebox.showinfo("Success", f"{first} {last} has been registered!\nUsername: {username}\nPassword: {password}")
            self.show_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_student_logic(self):
        selected = self.tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Confirm", "Delete selected student(s)?"):
            for item in selected:
                s_id = self.tree.item(item, "values")[0]
                try:
                    self.student_service.delete_student(s_id)
                    self.tree.delete(item)
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    # --- TEACHER MANAGEMENT ---
    def show_teachers(self):
        self.clear_content()
        tk.Label(self.main_content, text="TEACHER MANAGEMENT", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        cols = ("ID", "Name", "Surname", "Branch", "Action")
        self.t_tree = ttk.Treeview(self.main_content, columns=cols, show="headings", height=10)
        for col in cols:
            self.t_tree.heading(col, text=col)
            self.t_tree.column(col, anchor="center")
        self.t_tree.pack(fill="both", expand=False)

        instructors = self.instructor_service.get_all_instructors()
        for t in instructors:
            self.t_tree.insert("", "end", values=(t[0], t[1], t[2], t[3], "View More →"))

        self.t_tree.bind("<ButtonRelease-1>", self.handle_teacher_click)

        t_btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        t_btn_f.pack(fill="x", pady=20)
        tk.Button(t_btn_f, text="+ ADD TEACHER", bg=self.colors["success"], fg="white",
                  command=self.show_add_teacher_form, padx=15, pady=8).pack(side="left", padx=5)
        tk.Button(t_btn_f, text="ASSIGN TO COURSE", bg=self.colors["accent"], fg="white",
                  command=self.show_teacher_assignment, padx=15, pady=8).pack(side="left", padx=5)
        tk.Button(t_btn_f, text="DELETE", bg=self.colors["danger"], fg="white",
                  command=self.remove_teacher_logic, padx=15, pady=8).pack(side="right", padx=5)

    def handle_teacher_click(self, event):
        item = self.t_tree.selection()
        if not item:
            return
        if self.t_tree.identify_column(event.x) == "#5":
            t_id = self.t_tree.item(item[0], "values")[0]
            self.show_teacher_detail(t_id)

    def show_teacher_detail(self, t_id):
        self.clear_content()
        teacher = self.instructor_service.get_instructor_by_id(t_id)
        if not teacher:
            return

        card = tk.Frame(self.main_content, bg="white", padx=30, pady=30,
                        highlightthickness=1, highlightbackground="#E2E8F0")
        card.pack(fill="x")
        tk.Label(card, text=f"{teacher[1]} {teacher[2]}".upper(), font=("Arial", 16, "bold"),
                 bg="white", fg=self.colors["text_dark"]).pack(anchor="w")
        tk.Label(card, text=f"ID: {teacher[0]} | Branch: {teacher[3]}",
                 font=("Arial", 10), bg="white", fg=self.colors["text_light"]).pack(anchor="w", pady=5)

        btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text="BACK TO LIST", bg=self.colors["danger"], fg="white",
                  font=("Arial", 9, "bold"), command=self.show_teachers, padx=20, pady=10).pack(side="left")

    def show_add_teacher_form(self):
        self.clear_content()
        tk.Label(self.main_content, text="REGISTER NEW TEACHER", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        form_f = tk.Frame(self.main_content, bg="white", padx=30, pady=30,
                          highlightthickness=1, highlightbackground="#CBD5E1")
        form_f.pack(fill="x")

        self.teacher_entries = {}
        fields = [("Teacher ID:", "entry"), ("First Name:", "entry"), ("Last Name:", "entry"), ("Branch:", "entry")]

        for i, (text, f_type) in enumerate(fields):
            tk.Label(form_f, text=text, bg="white", font=("Arial", 9, "bold")).grid(row=i, column=0, sticky="w", pady=10)
            ent = tk.Entry(form_f, width=40)
            ent.grid(row=i, column=1, padx=20, pady=10)
            self.teacher_entries[text] = ent

        btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text="SAVE TEACHER", bg=self.colors["success"], fg="white",
                  font=("Arial", 9, "bold"), command=self.save_teacher_logic, padx=20, pady=10).pack(side="left")
        tk.Button(btn_f, text="CANCEL", bg=self.colors["danger"], fg="white",
                  font=("Arial", 9, "bold"), command=self.show_teachers, padx=20, pady=10).pack(side="right")

    def save_teacher_logic(self):
        t_id = self.teacher_entries["Teacher ID:"].get().strip()
        first = self.teacher_entries["First Name:"].get().strip()
        last = self.teacher_entries["Last Name:"].get().strip()
        branch = self.teacher_entries["Branch:"].get().strip()

        if not t_id or not first or not last or not branch:
            messagebox.showwarning("Warning", "Please fill all fields!")
            return

        if not t_id.isdigit():
            messagebox.showwarning("Warning", "Teacher ID must be a number!")
            return

        try:
            self.instructor_service.add_instructor(int(t_id), first, last, branch)

            username = f"{first.lower()}.{last.lower()}"
            password = str(t_id)
            self.services["auth"].create_user(username, password, "teacher", instructor_id = int(t_id))

            messagebox.showinfo("Success", f"Teacher {first} {last} registered successfully!")
            self.show_teachers()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_teacher_logic(self):
        selected = self.t_tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Confirm", "Delete selected teacher?"):
            for item in selected:
                t_id = self.t_tree.item(item, "values")[0]
                try:
                    self.instructor_service.delete_instructor(t_id)
                    self.t_tree.delete(item)
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    # --- COURSE MANAGEMENT ---
    def show_courses(self):
        self.clear_content()
        tk.Label(self.main_content, text="COURSE MANAGEMENT", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        t_frame = tk.Frame(self.main_content, bg="white", padx=10, pady=10, highlightthickness=1)
        t_frame.pack(fill="both", expand=True)

        cols = ("Course ID", "Course Name", "Course Code", "Credit")
        self.c_tree = ttk.Treeview(t_frame, columns=cols, show="headings", height=10)
        for col in cols:
            self.c_tree.heading(col, text=col)
            self.c_tree.column(col, anchor="center")
        self.c_tree.pack(fill="both", expand=False)

        courses = self.course_service.get_all_courses()
        for c in courses:
            self.c_tree.insert("", "end", values=(c[0], c[1], c[2], c[3]))
        
        btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text = "+ ADD COURSE", bg=self.colors["success"], fg = "white",
                  font = ("Arial", 9, "bold"), command = self.show_add_course_form,
                  padx = 15, pady=8).pack(side="left", padx=5)
        tk.Button(btn_f, text="DELETE SELECTED", bg=self.colors["danger"], fg="white",
                font=("Arial", 9, "bold"), command=self.remove_course_logic,
                padx=15, pady=8).pack(side="right", padx=5)

    # --- ENROLLMENT ---
    def show_enrollments(self):
        self.clear_content()
        tk.Label(self.main_content, text="ENROLLMENT MANAGEMENT", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        cols = ("Student ID", "Student Name", "Course ID", "Course Name", "Grade", "Status")
        e_tree = ttk.Treeview(self.main_content, columns=cols, show="headings", height=10)
        for col in cols:
            e_tree.heading(col, text=col)
            e_tree.column(col, anchor="center")
        e_tree.pack(fill="both", expand=False)

        enrollments = self.enrollment_service.get_all_enrollments()
        for e in enrollments:
            e_tree.insert("", "end", values=e)

        btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text="+ ENROLL STUDENT", bg=self.colors["accent"], fg="white",
                  font=("Arial", 9, "bold"), command=self.show_student_enrollment,
                  padx=15, pady=8).pack(side="left", padx=5)

    def show_student_enrollment(self):
        self.clear_content()
        tk.Label(self.main_content, text="ENROLL STUDENT IN COURSE", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        form_f = tk.Frame(self.main_content, bg="white", padx=30, pady=30,
                          highlightthickness=1, highlightbackground="#E2E8F0")
        form_f.pack(fill="x")

        students = self.student_service.get_all_students()
        self.student_map = {f"{s[0]} - {s[1]} {s[2]}": s[0] for s in students}
        courses = self.course_service.get_all_courses()
        self.course_map = {f"{c[0]} - {c[1]}": c[0] for c in courses}

        tk.Label(form_f, text="Select Student:", bg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=10)
        self.enroll_student_cb = ttk.Combobox(form_f, values=list(self.student_map.keys()), state="readonly", width=40)
        self.enroll_student_cb.grid(row=0, column=1, padx=20)

        tk.Label(form_f, text="Select Course:", bg="white", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        self.enroll_course_cb = ttk.Combobox(form_f, values=list(self.course_map.keys()), state="readonly", width=40)
        self.enroll_course_cb.grid(row=1, column=1, padx=20)

        btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text="CONFIRM ENROLLMENT", bg=self.colors["accent"], fg="white",
                  command=self.confirm_enrollment_logic, padx=20, pady=10).pack(side="left")
        tk.Button(btn_f, text="CANCEL", bg=self.colors["danger"], fg="white",
                  command=self.show_students, padx=20, pady=10).pack(side="right")

    def confirm_enrollment_logic(self):
        student_key = self.enroll_student_cb.get()
        course_key = self.enroll_course_cb.get()

        if not student_key or not course_key:
            messagebox.showwarning("Warning", "Please select both student and course!")
            return

        student_id = self.student_map[student_key]
        course_id = self.course_map[course_key]

        try:
            self.enrollment_service.enroll_student(student_id, course_id)
            messagebox.showinfo("Success", "Student enrolled successfully!")
            self.show_enrollments()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- TEACHER ASSIGNMENT ---
    def show_teacher_assignment(self):
        self.clear_content()
        tk.Label(self.main_content, text="ASSIGN TEACHER TO COURSE", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        form_f = tk.Frame(self.main_content, bg="white", padx=30, pady=30,
                          highlightthickness=1, highlightbackground="#E2E8F0")
        form_f.pack(fill="x")

        instructors = self.instructor_service.get_all_instructors()
        self.instructor_map = {f"{t[0]} - {t[1]} {t[2]}": t[0] for t in instructors}
        courses = self.course_service.get_all_courses()
        self.assign_course_map = {f"{c[0]} - {c[1]}": c[0] for c in courses}

        tk.Label(form_f, text="Select Teacher:", bg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=10)
        self.assign_hoca_cb = ttk.Combobox(form_f, values=list(self.instructor_map.keys()), state="readonly", width=40)
        self.assign_hoca_cb.grid(row=0, column=1, padx=20)

        tk.Label(form_f, text="Select Course:", bg="white", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        self.assign_ders_cb = ttk.Combobox(form_f, values=list(self.assign_course_map.keys()), state="readonly", width=40)
        self.assign_ders_cb.grid(row=1, column=1, padx=20)

        btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text="CONFIRM ASSIGNMENT", bg=self.colors["success"], fg="white",
                  command=self.confirm_assignment_logic, padx=20, pady=10).pack(side="left")
        tk.Button(btn_f, text="CANCEL", bg=self.colors["danger"], fg="white",
                  command=self.show_teachers, padx=20, pady=10).pack(side="right")

    def confirm_assignment_logic(self):
        hoca_key = self.assign_hoca_cb.get()
        ders_key = self.assign_ders_cb.get()

        if not hoca_key or not ders_key:
            messagebox.showwarning("Warning", "Please select both teacher and course!")
            return

        instructor_id = self.instructor_map[hoca_key]
        course_id = self.assign_course_map[ders_key]

        try:
            self.course_service.assign_instructor(course_id, instructor_id)
            messagebox.showinfo("Success", "Teacher assigned to course successfully!")
            self.show_teachers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- ANNOUNCEMENTS ---
    def show_announcements(self):
        self.clear_content()
        tk.Label(self.main_content, text="BROADCAST MESSAGES", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))
        tk.Label(self.main_content, text="Announcement feature coming soon.",
                 font=("Arial", 11), bg=self.colors["bg"], fg=self.colors["text_light"]).pack()

    # --- LOGOUT ---
    def logout(self):
        if messagebox.askyesno("Logout", "Exit Admin Panel?"):
            for w in self.root.winfo_children():
                w.destroy()
            from ui.LoginWindow import LoginWindow
            LoginWindow(self.root, self.root.on_login_success_callback)

    def show_add_course_form(self):
        self.clear_content()
        tk.Label(self.main_content, text="ADD NEW COURSE", font=("Arial", 18, "bold"),
                bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        form_f = tk.Frame(self.main_content, bg="white", padx=30, pady=30,
                      highlightthickness=1, highlightbackground="#E2E8F0")
        form_f.pack(fill="x")

        self.course_entries = {}
        fields = ["Course Name:", "Course Code:", "Credit:"]

        for i, text in enumerate(fields):
            tk.Label(form_f, text=text, bg="white", font=("Arial", 9, "bold")).grid(row=i, column=0, sticky="w", pady=10)
            ent = tk.Entry(form_f, width=40)
            ent.grid(row=i, column=1, padx=20, pady=10)
            self.course_entries[text] = ent

        btn_f = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text="SAVE COURSE", bg=self.colors["success"], fg="white",
            font=("Arial", 9, "bold"), command=self.save_course_logic,
            padx=20, pady=10).pack(side="left")
        tk.Button(btn_f, text="CANCEL", bg=self.colors["danger"], fg="white",
            font=("Arial", 9, "bold"), command=self.show_courses,
            padx=20, pady=10).pack(side="right")

    def save_course_logic(self):
        course_name = self.course_entries["Course Name:"].get().strip()
        course_code = self.course_entries["Course Code:"].get().strip()
        credit = self.course_entries["Credit:"].get().strip()

        if not course_name or not course_code or not credit:
            messagebox.showwarning("Warning", "Please fill all fields!")
            return

        if not credit.isdigit():
            messagebox.showwarning("Warning", "Course ID and Credit must be numbers!")
            return

        try:
            import random
            course_id = random.randint(1000,9999)
            self.course_service.add_course(course_id, course_name, course_code, int(credit))
            messagebox.showinfo("Success", f"{course_name} added successfully!")
            self.show_courses()
        except Exception as e:
                messagebox.showerror("Error", str(e))

    def remove_course_logic(self):
        selected = self.c_tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Confirm", "Delete selected course?"):
            for item in selected:
                c_id = self.c_tree.item(item, "values")[0]
                try:
                    self.course_service.delete_course(c_id)
                    self.c_tree.delete(item)
                except Exception as e:
                    messagebox.showerror("Error", str(e))