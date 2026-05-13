import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class StudentWindow:
    def __init__(self, root, user_info, services):
        self.root = root
        self.user_info = user_info
        self.services = services
        self.student_service = services["student"]
        self.course_service = services["course"]
        self.enrollment_service = services["enrollment"]
        self.grade_service = services["grade"]
        self.attendance_service = services["attendance"]
        self.display_name = user_info.get('username', 'Student').upper()
        self.student_id = user_info.get('student_id')

        self.colors = {
            "bg": "#F8FAFC", "sidebar": "#1E293B", "accent": "#3B82F6",
            "card": "#FFFFFF", "text_dark": "#0F172A", "text_light": "#64748B",
            "danger": "#EF4444", "success": "#10B981"
        }

        self.root.configure(bg=self.colors["bg"])
        self.setup_sidebar()
        self.main_content = tk.Frame(self.root, bg=self.colors["bg"], padx=30, pady=20)
        self.main_content.pack(side="left", fill="both", expand=True)
        self.show_schedule()

    def setup_sidebar(self):
        sidebar = tk.Frame(self.root, bg=self.colors["sidebar"], width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text=f"WELCOME,\n{self.display_name}", font=("Arial", 11, "bold"),
                 bg=self.colors["sidebar"], fg="white", pady=40).pack()

        menu = [
            ("My Courses", self.show_schedule),
            ("Dashboard & Grades", self.show_dashboard),
            ("Attendance", self.show_attendance),
            ("Transcript", self.show_transcript),
            ("Messages", self.show_messages),
            ("Notifications", self.show_notifications),  # YENİ
            ("My Profile", self.show_profile),
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

    def create_custom_button(self, parent, text, color, command, width=20):
        btn = tk.Label(parent, text=text, bg=color, fg="white", font=("Arial", 10, "bold"),
                       pady=12, width=width, cursor="arrow")
        btn.bind("<Button-1>", lambda e: command())
        return btn

    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="white", padx=20, pady=20,
                        highlightthickness=1, highlightbackground="#E2E8F0")
        card.pack(side="left", padx=(0, 20))
        tk.Label(card, text=title, font=("Arial", 8, "bold"), bg="white",
                 fg=self.colors["text_light"]).pack()
        tk.Label(card, text=value, font=("Arial", 20, "bold"), bg="white", fg=color).pack()

    def show_schedule(self):
        self.clear_content()
        header = tk.Frame(self.main_content, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 20))
        now = datetime.now().strftime("%A, %d %B %Y")
        tk.Label(header, text="MY COURSES", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text_dark"]).pack(side="left")
        tk.Label(header, text=now, font=("Arial", 10),
                 bg=self.colors["bg"], fg=self.colors["text_light"]).pack(side="right")

        cols = ("Course Code", "Course Name", "Credit", "Grade", "Status")
        tree = ttk.Treeview(self.main_content, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=False)

        if self.student_id:
            enrollments = self.enrollment_service.get_enrollments_by_student(self.student_id)
            for e in enrollments:
                tree.insert("", "end", values=(e[2], e[1], e[3], e[4] or "N/A", e[5]))

    def show_dashboard(self):
        self.clear_content()
        tk.Label(self.main_content, text="ACADEMIC DASHBOARD", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text_dark"]).pack(anchor="w", pady=(0, 20))

        stats_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        stats_frame.pack(fill="x", pady=10)

        if self.student_id:
            gpa = self.grade_service.calculate_gpa(self.student_id)
            enrollments = self.enrollment_service.get_enrollments_by_student(self.student_id)
        else:
            gpa = 0.0
            enrollments = []

        self.create_stat_card(stats_frame, "CUMULATIVE GPA", str(gpa), self.colors["accent"])
        self.create_stat_card(stats_frame, "ENROLLED COURSES", str(len(enrollments)), self.colors["success"])

        tk.Label(self.main_content, text="My Courses", font=("Arial", 12, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(20, 10))

        cols = ("Course Code", "Course Name", "Credit", "Grade", "Status")
        tree = ttk.Treeview(self.main_content, columns=cols, show="headings", height=5)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        for e in enrollments:
            tree.insert("", "end", values=(e[2], e[1], e[3], e[4] or "N/A", e[5]))
        tree.pack(fill="x")

    def show_attendance(self):
        self.clear_content()

        tk.Label(
            self.main_content,
            text="ATTENDANCE STATUS",
            font=("Arial", 18, "bold"),
            bg=self.colors["bg"]
        ).pack(anchor="w", pady=(0, 20))

        cols = ("Course Code", "Course Name", "Total Hours", "Absent Hours", "Percentage")
        tree = ttk.Treeview(self.main_content, columns=cols, show="headings")

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        if self.student_id:
            attendance_service = self.services["attendance"]
            records = attendance_service.get_attendance_by_student(self.student_id)
            for r in records:
                tree.insert("", "end", values=r)

        tree.pack(fill="both", expand=False)

    def show_transcript(self):
        self.clear_content()
        tk.Label(self.main_content, text="ACADEMIC TRANSCRIPT", font=("Arial", 18, "bold"),
                bg=self.colors["bg"]).pack(anchor="w")

        btn_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        btn_frame.pack(fill="x", pady=20)

        if self.student_id:
            gpa = self.grade_service.calculate_gpa(self.student_id)
            enrollments = self.enrollment_service.get_enrollments_by_student(self.student_id)
            student = self.student_service.get_student_by_id(self.student_id)
        else:
            gpa = 0.0
            enrollments = []
            student = None

        from ui.SharedComponents import StudentDetailView
        export_btn = self.create_custom_button(
            btn_frame, "EXPORT PDF", self.colors["accent"],
            lambda: StudentDetailView.export_pdf(student, gpa, enrollments)
        )
        export_btn.pack(side="left")

        text_box = tk.Text(self.main_content, font=("Courier", 10), bg="white", padx=20, pady=20, bd=0)
        content = f"STUDENT TRANSCRIPT\n{'='*40}\nNAME: {self.display_name}\nGPA: {gpa}\n{'='*40}\n"
        for e in enrollments:
            content += f"{e[2]} - {e[1]} | Grade: {e[4] or 'N/A'} | {e[5]}\n"
        text_box.insert("1.0", content)
        text_box.config(state="disabled")
        text_box.pack(fill="both", expand=True)



    def show_messages(self):
        self.clear_content()
        tk.Label(self.main_content, text="INSTRUCTOR MESSAGING", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"]).pack(anchor="w", pady=(0, 20))

        all_courses = self.course_service.get_all_courses()
        course_map = {c[1]: c[0] for c in all_courses}
        instructor_names = list(course_map.keys())

        tk.Label(self.main_content, text="Select Course", bg=self.colors["bg"],
                 font=("Arial", 9, "bold")).pack(anchor="w")
        cb = ttk.Combobox(self.main_content, values=instructor_names, state="readonly")
        cb.pack(fill="x", pady=(5, 20))

        tk.Label(self.main_content, text="Your Message", bg=self.colors["bg"],
                 font=("Arial", 9, "bold")).pack(anchor="w")
        txt = tk.Text(self.main_content, height=10, bd=1, relief="flat",
                      highlightthickness=1, highlightbackground="#E2E8F0")
        txt.pack(fill="x", pady=5)

        def send_message():
            selected_course = cb.get()
            body = txt.get("1.0", tk.END).strip()

            if not selected_course:
                messagebox.showwarning("Warning", "Please select a course.")
                return
            if not body:
                messagebox.showwarning("Warning", "Message cannot be empty.")
                return

            try:
                user_id = self.user_info.get("user_id")
                course_id = course_map[selected_course]
                course_data = next((c for c in all_courses if c[0] == course_id), None)
                receiver_id = course_data[4] if course_data and len(course_data) > 4 else user_id
                self.services["message"].send_message(
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    body=body,
                    subject=f"Re: {selected_course}"
                )
                messagebox.showinfo("Success", "Message Sent")
                txt.delete("1.0", tk.END)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        send_btn = self.create_custom_button(self.main_content, "SEND MESSAGE",
                                             self.colors["sidebar"], send_message)
        send_btn.pack(pady=20, anchor="e")

    # YENİ — Notifications
    def show_notifications(self):
        self.clear_content()
        tk.Label(self.main_content, text="NOTIFICATIONS", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text_dark"]).pack(anchor="w", pady=(0, 20))

        user_id = self.user_info.get("user_id")
        try:
            rows = self.services["notification"].get_notifications(user_id)
        except Exception:
            rows = []

        if not rows:
            tk.Label(self.main_content, text="You have no notifications.",
                     font=("Arial", 11), bg=self.colors["bg"],
                     fg=self.colors["text_light"]).pack(pady=40)
            return

        for row in rows:
            notif_id, title, body, is_read, created_at = row
            card = tk.Frame(self.main_content, bg="white" if is_read else "#EFF6FF",
                            pady=12, padx=15,
                            highlightthickness=1, highlightbackground="#E2E8F0")
            card.pack(fill="x", pady=3)

            tk.Label(card, text=title,
                     font=("Arial", 10, "bold") if not is_read else ("Arial", 10),
                     bg=card["bg"], fg=self.colors["text_dark"]).pack(anchor="w")
            tk.Label(card, text=body, font=("Arial", 9),
                     bg=card["bg"], fg=self.colors["text_light"],
                     wraplength=700, justify="left").pack(anchor="w")
            tk.Label(card, text=created_at[:16] if created_at else "",
                     font=("Arial", 8), bg=card["bg"],
                     fg=self.colors["text_light"]).pack(anchor="e")

            if not is_read:
                card.bind("<Button-1>", lambda e, nid=notif_id: self._mark_notif_read(nid))

        mark_btn = self.create_custom_button(self.main_content, "MARK ALL AS READ",
                                             self.colors["sidebar"],
                                             lambda: self._mark_all_notif(user_id))
        mark_btn.pack(pady=20, anchor="e")

    def _mark_notif_read(self, notif_id):
        try:
            self.services["notification"].mark_as_read(notif_id)
            self.show_notifications()
        except Exception:
            pass

    def _mark_all_notif(self, user_id):
        try:
            self.services["notification"].mark_all_as_read(user_id)
            self.show_notifications()
        except Exception:
            pass

    def show_profile(self):
        self.clear_content()
        tk.Label(self.main_content, text="MY PROFILE", font=("Arial", 18, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text_dark"]).pack(anchor="w", pady=(0, 25))

        profile_card = tk.Frame(self.main_content, bg="white", padx=40, pady=40,
                                highlightthickness=1, highlightbackground="#E2E8F0")
        profile_card.pack(fill="x", padx=5)

        if self.student_id:
            student = self.student_service.get_student_by_id(self.student_id)
            if student:
                info_data = [
                    ("FULL NAME", f"{student.name} {student.surname}"),
                    ("STUDENT ID", str(student.student_id)),
                    ("DEPARTMENT", student.department),
                    ("USERNAME", self.user_info.get('username', 'N/A')),
                ]
            else:
                info_data = [("USERNAME", self.user_info.get('username', 'N/A'))]
        else:
            info_data = [("USERNAME", self.user_info.get('username', 'N/A'))]

        for label, value in info_data:
            row_frame = tk.Frame(profile_card, bg="white")
            row_frame.pack(fill="x", pady=10)
            tk.Label(row_frame, text=label, font=("Arial", 8, "bold"),
                     bg="white", fg=self.colors["text_light"], width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row_frame, font=("Arial", 10), bg="#F8FAFC",
                             fg=self.colors["text_dark"], bd=0, highlightthickness=1,
                             highlightbackground="#E2E8F0")
            entry.insert(0, value)
            if label in ["STUDENT ID", "DEPARTMENT"]:
                entry.config(state="readonly", readonlybackground="#F1F5F9")
            entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(10, 0))

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            for widget in self.root.winfo_children():
                widget.destroy()
            from ui.LoginWindow import LoginWindow
            LoginWindow(self.root, self.root.on_login_success_callback)