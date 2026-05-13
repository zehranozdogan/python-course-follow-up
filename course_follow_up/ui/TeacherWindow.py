import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ui.SharedComponents import StudentProfileView


class TeacherWindow:
    def __init__(self, root, user_info, services):
        self.root = root
        self.user_info = user_info
        self.services = services
        self.student_service = services["student"]
        self.instructor_service = services["instructor"]
        self.course_service = services["course"]
        self.enrollment_service = services["enrollment"]
        self.grade_service = services["grade"]
        self.attendance_service = services["attendance"]
        self.root.title(f"Panel - {user_info['username']}")
        self.root.geometry("1240x850")

        self.bg_color = "#FFFFFF"
        self.sidebar_color = "#2C3E50"
        self.accent_color = "#34495E"
        self.completed_bg = "#E8F5E9"
        self.completed_fg = "#2E7D32"
        self.root.configure(bg=self.bg_color)

        instructor_id = user_info.get('instructor_id')
        if instructor_id:
            self.my_courses_data = self.course_service.get_courses_by_instructor(instructor_id)
            self.my_courses = [c[1] for c in self.my_courses_data]
        else:
            self.my_courses_data = []
            self.my_courses = []

        self.full_schedule = []
        for c in self.my_courses_data:
            self.full_schedule.append({"day": "Monday", "time": "09:00", "course": c[1], "room": "TBA"})

        self.students_db = {}
        for c in self.my_courses_data:
            students = self.enrollment_service.get_enrollments_by_course(c[0])
            for s in students:
                sid = str(s[0])
                if sid not in self.students_db:
                    self.students_db[sid] = {
                        "name": f"{s[1]} {s[2]}",
                        "no": sid,
                        "email": "", "phone": "",
                        "courses": [], "gpa": "N/A",
                        "grades": [], "attendance": [],
                        "last_msg": "No messages yet."
                    }
                self.students_db[sid]["courses"].append(c[1])

        # SIDEBAR
        self.sidebar = tk.Frame(self.root, bg=self.sidebar_color, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        user_lbl = tk.Label(self.sidebar, text=user_info['username'].upper(),
                            bg=self.sidebar_color, fg="#ECF0F1", font=("Arial", 14, "bold"))
        user_lbl.pack(pady=(60, 40))
        user_lbl.bind("<Button-1>", lambda e: self.show_lectures())

        menu_items = [
            ("SCHEDULE", self.show_lectures),
            ("STUDENTS", self.show_students_list),
            ("GRADES", self.show_grades),
            ("ATTENDANCE", self.show_attendance),
            ("MESSAGES", self.show_messages),
            ("ANNOUNCEMENTS", self.show_announcements),
            ("NOTIFICATIONS", self.show_notifications),
            ("LOGOUT", self.logout),
        ]

        for text, cmd in menu_items:
            btn = tk.Label(self.sidebar, text=text, bg=self.sidebar_color, fg="#ECF0F1",
                           font=("Arial", 9, "bold"), pady=15)
            btn.pack(fill="x", padx=10)
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.accent_color))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.sidebar_color))

        self.main_area = tk.Frame(self.root, bg=self.bg_color, padx=30, pady=20)
        self.main_area.pack(side="right", expand=True, fill="both")
        self.lbl_clock = tk.Label(self.main_area, text="", font=("Arial", 10),
                                  bg=self.bg_color, fg="#7F8C8D")
        self.lbl_clock.pack(anchor="ne")
        self.update_time()

        self.main_content = tk.Frame(self.main_area, bg=self.bg_color)
        self.main_content.pack(fill="both", expand=True)

        self.show_lectures()

    def clear_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def update_time(self):
        try:
            self.lbl_clock.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.root.after(1000, self.update_time)
        except Exception:
            pass

    # ── 1) SCHEDULE ──────────────────────────────────────────────────────────
    def show_lectures(self):
        self.clear_content()
        tk.Label(self.main_content, text="Schedule", font=("Arial", 20, "bold"),
                 bg=self.bg_color, fg="#2C3E50").pack(anchor="w", pady=(0, 20))

        f_frame = tk.Frame(self.main_content, bg=self.bg_color)
        f_frame.pack(fill="x", pady=10)

        self.course_cb = ttk.Combobox(f_frame, values=["All Courses"] + self.my_courses,
                                      state="readonly", width=22)
        self.course_cb.set("All Courses")
        self.course_cb.pack(side="left", padx=5)
        self.course_cb.bind("<<ComboboxSelected>>", lambda e: self.load_schedule())

        self.day_cb = ttk.Combobox(f_frame,
                                   values=["Default (Today)", "Monday", "Tuesday",
                                           "Wednesday", "Thursday", "Friday"],
                                   state="readonly", width=15)
        self.day_cb.set("Default (Today)")
        self.day_cb.pack(side="left", padx=5)
        self.day_cb.bind("<<ComboboxSelected>>", lambda e: self.load_schedule())

        self.tree = ttk.Treeview(self.main_content,
                                 columns=("DAY", "TIME", "COURSE", "ROOM", "STATUS"),
                                 show="headings")
        for col in ("DAY", "TIME", "COURSE", "ROOM", "STATUS"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.tag_configure('completed', background=self.completed_bg,
                                foreground=self.completed_fg)
        self.tree.pack(fill="both", expand=False, pady=10)
        self.load_schedule()

    def load_schedule(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        sel_c = self.course_cb.get()
        sel_d = self.day_cb.get()
        today = datetime.now().strftime('%A')
        curr_hr = datetime.now().hour
        for item in self.full_schedule:
            c_match = (sel_c == "All Courses" or sel_c == item["course"])
            target_d = today if sel_d == "Default (Today)" else sel_d
            d_match = (True if (sel_c != "All Courses" and sel_d == "Default (Today)")
                       else (item["day"] == target_d))
            if c_match and d_match:
                hr = int(item["time"].split(":")[0])
                tag = ('completed',) if (item["day"] == today and curr_hr >= hr) else ()
                status = "Completed" if tag else "Pending"
                self.tree.insert("", "end",
                                 values=(item["day"], item["time"], item["course"],
                                         item["room"], status), tags=tag)

    # ── 2) STUDENTS ──────────────────────────────────────────────────────────
    def show_students_list(self):
        self.clear_content()
        tk.Label(self.main_content, text="Student Management", font=("Arial", 20, "bold"),
                 bg=self.bg_color).pack(anchor="w", pady=(0, 10))

        filter_bar = tk.Frame(self.main_content, bg="#F4F6F7", padx=10, pady=10)
        filter_bar.pack(fill="x", pady=10)

        tk.Label(filter_bar, text="Search:", bg="#F4F6F7", font=("Arial", 9, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_student_list())
        tk.Entry(filter_bar, textvariable=self.search_var, width=25).pack(side="left", padx=5)

        tk.Label(filter_bar, text="Course:", bg="#F4F6F7",
                 font=("Arial", 9, "bold")).pack(side="left", padx=(15, 0))
        self.course_filter = ttk.Combobox(filter_bar,
                                          values=["All Students"] + self.my_courses,
                                          state="readonly")
        self.course_filter.set("All Students")
        self.course_filter.pack(side="left", padx=5)
        self.course_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_student_list())

        self.student_container = tk.Frame(self.main_content, bg=self.bg_color)
        self.student_container.pack(fill="both", expand=True)
        self.refresh_student_list()

    def refresh_student_list(self):
        for widget in self.student_container.winfo_children():
            widget.destroy()
        search_q = self.search_var.get().lower()
        course_q = self.course_filter.get()
        for sid, d in self.students_db.items():
            name_match = search_q in d['name'].lower() or search_q in d['no']
            course_match = (course_q == "All Students" or course_q in d['courses'])
            if name_match and course_match:
                card = tk.Frame(self.student_container, bg="#F8F9F9", pady=10, padx=15,
                                highlightthickness=1, highlightbackground="#D5DBDB")
                card.pack(fill="x", pady=2)
                tk.Label(card, text=f"{d['no']} - {d['name']}", font=("Arial", 10, "bold"),
                         bg="#F8F9F9").pack(side="left")
                tk.Label(card, text=f"GPA: {d['gpa']}", font=("Arial", 9),
                         bg="#F8F9F9", fg="#7F8C8D").pack(side="left", padx=20)
                btn = tk.Label(card, text="Detay Gör →", bg="#2980B9", fg="white",
                               font=("Arial", 8, "bold"), padx=10, pady=5)
                btn.pack(side="right")
                btn.bind("<Button-1>", lambda e, s=sid: self.show_student_full_profile(s))

    def show_student_full_profile(self, student_id):
        from ui.SharedComponents import StudentDetailView
        StudentDetailView.show(
            self.main_content, student_id, self.services,
            {"bg": self.bg_color, "sidebar": self.sidebar_color},
            self.show_students_list
    )
        
    
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
            messagebox.showinfo("Success", "Transcript saved!")

        except ImportError:
            messagebox.showerror("Error", "pip install reportlab")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    # ── 3) GRADES ────────────────────────────────────────────────────────────
    def show_grades(self):
        self.clear_content()
        tk.Label(self.main_content, text="Grade Management", font=("Arial", 20, "bold"),
                 bg=self.bg_color, fg="#2C3E50").pack(anchor="w", pady=(0, 15))

        top_f = tk.Frame(self.main_content, bg=self.bg_color)
        top_f.pack(fill="x", pady=(0, 15))
        tk.Label(top_f, text="Select Course:", font=("Arial", 9, "bold"),
                 bg=self.bg_color).pack(side="left")
        self.grade_course_cb = ttk.Combobox(top_f, values=self.my_courses,
                                            state="readonly", width=35)
        self.grade_course_cb.pack(side="left", padx=10)
        self.grade_course_cb.bind("<<ComboboxSelected>>", lambda e: self.load_grade_list())

        cols = ("Student ID", "Name", "Surname", "Current Grade", "Letter", "Status")
        self.grade_tree = ttk.Treeview(self.main_content, columns=cols,
                                       show="headings", height=10)
        for col in cols:
            self.grade_tree.heading(col, text=col)
            self.grade_tree.column(col, anchor="center", width=130)
        self.grade_tree.pack(fill="x", pady=(0, 20))
        self.grade_tree.bind("<<TreeviewSelect>>", self.on_grade_row_select)

        entry_f = tk.Frame(self.main_content, bg="#F4F6F7", padx=15, pady=15,
                           highlightthickness=1, highlightbackground="#D5DBDB")
        entry_f.pack(fill="x")

        tk.Label(entry_f, text="Student ID:", font=("Arial", 9, "bold"),
                 bg="#F4F6F7").grid(row=0, column=0, padx=5)
        self.grade_student_entry = tk.Entry(entry_f, width=12, font=("Arial", 10))
        self.grade_student_entry.grid(row=0, column=1, padx=5)

        tk.Label(entry_f, text="Grade (0-100):", font=("Arial", 9, "bold"),
                 bg="#F4F6F7").grid(row=0, column=2, padx=5)
        self.grade_value_entry = tk.Entry(entry_f, width=10, font=("Arial", 10))
        self.grade_value_entry.grid(row=0, column=3, padx=5)

        save_btn = tk.Label(entry_f, text="SAVE GRADE", bg="#27AE60", fg="white",
                            font=("Arial", 9, "bold"), padx=20, pady=8, cursor="hand2")
        save_btn.grid(row=0, column=4, padx=15)
        save_btn.bind("<Button-1>", lambda e: self.save_grade())

    def load_grade_list(self):
        for item in self.grade_tree.get_children():
            self.grade_tree.delete(item)
        selected = self.grade_course_cb.get()
        course = next((c for c in self.my_courses_data if c[1] == selected), None)
        if not course:
            return
        rows = self.enrollment_service.get_enrollments_by_course(course[0])
        for r in rows:
            from models.grade import Grade
            g = Grade(r[0], course[0], r[4])
            letter = g.get_letter_grade()
            self.grade_tree.insert("", "end",
                                   values=(r[0], r[1], r[2], r[4] or "N/A", letter, r[5]))

    def on_grade_row_select(self, event):
        selected = self.grade_tree.selection()
        if selected:
            values = self.grade_tree.item(selected[0], "values")
            self.grade_student_entry.delete(0, tk.END)
            self.grade_student_entry.insert(0, values[0])

    def save_grade(self):
        course_name = self.grade_course_cb.get()
        student_id = self.grade_student_entry.get().strip()
        grade_val = self.grade_value_entry.get().strip()

        if not course_name:
            messagebox.showwarning("Warning", "Please select a course first.")
            return
        if not student_id or not grade_val:
            messagebox.showwarning("Warning", "Please fill Student ID and Grade fields.")
            return
        if not student_id.isdigit():
            messagebox.showwarning("Warning", "Student ID must be a number.")
            return
        try:
            grade_float = float(grade_val)
            if not (0 <= grade_float <= 100):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Warning", "Grade must be a number between 0 and 100.")
            return

        course = next((c for c in self.my_courses_data if c[1] == course_name), None)
        if not course:
            messagebox.showerror("Error", "Course not found.")
            return
        try:
            self.enrollment_service.update_grade(int(student_id), course[0], grade_float)
            messagebox.showinfo("Success", f"Grade saved: {grade_float}")
            self.grade_value_entry.delete(0, tk.END)
            self.grade_student_entry.delete(0, tk.END)
            self.load_grade_list()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    # ── 4) ATTENDANCE ─────────────────────────────────────────────────────────
    def show_attendance(self):
        self.clear_content()
        tk.Label(self.main_content, text="Attendance Management", font=("Arial", 20, "bold"),
                 bg=self.bg_color).pack(anchor="w", pady=(0, 20))

        tk.Label(self.main_content, text="Select Course:", bg=self.bg_color,
                 font=("Arial", 9, "bold")).pack(anchor="w")
        course_cb = ttk.Combobox(self.main_content, values=self.my_courses, state="readonly")
        course_cb.pack(fill="x", pady=(5, 20))

        cols = ("Student ID", "Name", "Surname", "Course", "Total Hours", "Absent", "Percentage")
        tree = ttk.Treeview(self.main_content, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=False)

        def load_attendance(event=None):
            for item in tree.get_children():
                tree.delete(item)
            selected = course_cb.get()
            if selected:
                course = next((c for c in self.my_courses_data if c[1] == selected), None)
                if course:
                    records = self.services["attendance"].get_attendance_by_course(course[0])
                    for r in records:
                        tree.insert("", "end", values=r)

        course_cb.bind("<<ComboboxSelected>>", load_attendance)

    # ── 5) MESSAGES ───────────────────────────────────────────────────────────
    def show_messages(self):
        self.clear_content()
        tk.Label(self.main_content, text="Inbox", font=("Arial", 20, "bold"),
                 bg=self.bg_color).pack(anchor="w", pady=20)

        user_id = self.user_info.get("user_id")
        try:
            db_messages = self.services["message"].get_inbox(user_id)
            for row in db_messages:
                msg_id, sender_id, sender_name, subject, body, is_read, sent_at = row
                sid = str(sender_id)
                if sid not in self.students_db:
                    self.students_db[sid] = {
                        "name": sender_name, "no": sid,
                        "email": "", "phone": "",
                        "courses": [], "gpa": "N/A",
                        "grades": [], "attendance": [],
                        "last_msg": body
                    }
                else:
                    self.students_db[sid]["last_msg"] = body
        except Exception:
            pass

        for sid, d in self.students_db.items():
            card = tk.Frame(self.main_content, bg="#F8F9F9", pady=15, padx=15,
                            highlightthickness=1, highlightbackground="#D5DBDB")
            card.pack(fill="x", pady=5)
            msg_preview = f"{d['name']}: {d['last_msg'][:30]}..."
            lbl_msg = tk.Label(card, text=msg_preview, font=("Arial", 11), bg="#F8F9F9")
            lbl_msg.pack(side="left")
            lbl_more = tk.Label(card, text="View More...",
                                font=("Arial", 9, "italic", "bold"),
                                fg="#3498DB", bg="#F8F9F9")
            lbl_more.pack(side="right")
            card.bind("<Button-1>", lambda e, s=sid: self.show_message_detail_page(s))
            lbl_msg.bind("<Button-1>", lambda e, s=sid: self.show_message_detail_page(s))
            lbl_more.bind("<Button-1>", lambda e, s=sid: self.show_message_detail_page(s))
            card.bind("<Enter>", lambda e, c=card: c.config(bg="#F2F4F4"))
            card.bind("<Leave>", lambda e, c=card: c.config(bg="#F8F9F9"))

    def show_message_detail_page(self, student_id):
        self.clear_content()
        data = self.students_db[student_id]

        header = tk.Frame(self.main_content, bg="#F4F6F7", padx=20, pady=20,
                          highlightthickness=1, highlightbackground="#D5DBDB")
        header.pack(fill="x")
        tk.Label(header, text=data['name'].upper(), font=("Arial", 18, "bold"),
                 bg="#F4F6F7", fg=self.sidebar_color).pack(anchor="w")

        tk.Label(self.main_content, text="Full Message Text:", font=("Arial", 11, "bold"),
                 bg=self.bg_color).pack(anchor="w", pady=(20, 5))
        tk.Label(self.main_content, text=data['last_msg'], font=("Arial", 11),
                 bg="#FDFEFE", relief="solid", bd=1, padx=15, pady=15,
                 wraplength=900, justify="left").pack(fill="x")

        tk.Label(self.main_content, text="Your Reply:", font=("Arial", 11, "bold"),
                 bg=self.bg_color).pack(anchor="w", pady=(20, 5))
        reply_box = tk.Text(self.main_content, height=5, font=("Arial", 11),
                            highlightthickness=1, highlightbackground="#D5DBDB")
        reply_box.pack(fill="x", pady=5)

        btn_frame = tk.Frame(self.main_content, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=20)

        send_btn = tk.Label(btn_frame, text="SEND REPLY", bg=self.sidebar_color, fg="white",
                            font=("Arial", 9, "bold"), padx=20, pady=10)
        send_btn.pack(side="left")
        send_btn.bind("<Button-1>",
                      lambda e: self.process_reply(student_id, reply_box.get("1.0", tk.END)))

        profile_btn = tk.Label(btn_frame, text="VIEW ACADEMIC DATA", bg="#2980B9", fg="white",
                               font=("Arial", 9, "bold"), padx=20, pady=10)
        profile_btn.pack(side="left", padx=15)
        profile_btn.bind("<Button-1>",
                         lambda e, s=student_id: self.show_student_full_profile(s))

        cancel_btn = tk.Label(btn_frame, text="CANCEL", bg="#E74C3C", fg="white",
                              font=("Arial", 9, "bold"), padx=20, pady=10)
        cancel_btn.pack(side="left")
        cancel_btn.bind("<Button-1>", lambda e: self.show_messages())

    def process_reply(self, student_id, reply_content):
        if not reply_content.strip():
            return
        timestamp = datetime.now().strftime("%H:%M")
        self.students_db[student_id]['last_msg'] = (
            f"Me ({timestamp}): {reply_content}\n---\n"
            + self.students_db[student_id]['last_msg']
        )
        messagebox.showinfo("Sent", "Your reply has been saved.")
        self.show_messages()

    # ── 6) ANNOUNCEMENTS ──────────────────────────────────────────────────────
    def show_announcements(self):
        self.clear_content()
        header_f = tk.Frame(self.main_content, bg=self.bg_color)
        header_f.pack(fill="x", pady=(0, 20))
        tk.Label(header_f, text="Broadcast Center", font=("Arial", 22, "bold"),
                 bg=self.bg_color, fg=self.sidebar_color).pack(side="left")

        main_frame = tk.Frame(self.main_content, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True)

        lbl_font = ("Arial", 10, "bold")
        fp = {"bg": "#FDFDFD", "padx": 15, "pady": 15,
              "highlightthickness": 1, "highlightbackground": "#EBEDEF"}

        col1 = tk.Frame(main_frame, **fp)
        col1.pack(side="left", fill="both", expand=True)
        tk.Label(col1, text="SOURCE SELECTION", font=lbl_font,
                 bg="#FDFDFD", fg="#5D6D7E").pack(anchor="w", pady=(0, 10))
        tk.Label(col1, text="By Courses", font=("Arial", 9, "bold"),
                 bg="#FDFDFD").pack(anchor="w")
        self.course_vars = {}
        for course in self.my_courses:
            var = tk.BooleanVar()
            tk.Checkbutton(col1, text=course, variable=var, bg="#FDFDFD",
                           activebackground="#FDFDFD",
                           command=self.sync_broadcast_list).pack(anchor="w", padx=5)
            self.course_vars[course] = var
        tk.Frame(col1, height=1, bg="#D5DBDB").pack(fill="x", pady=15)
        tk.Label(col1, text="By Individual Students", font=("Arial", 9, "bold"),
                 bg="#FDFDFD").pack(anchor="w")
        self.individual_vars = {}
        for sid, d in self.students_db.items():
            var = tk.BooleanVar()
            tk.Checkbutton(col1, text=d['name'], variable=var, bg="#FDFDFD",
                           activebackground="#FDFDFD",
                           command=self.sync_broadcast_list).pack(anchor="w", padx=5)
            self.individual_vars[sid] = var

        col2 = tk.Frame(main_frame, **fp)
        col2.pack(side="left", fill="both", expand=True, padx=15)
        tk.Label(col2, text="TARGET RECIPIENTS", font=lbl_font,
                 bg="#FDFDFD", fg="#5D6D7E").pack(anchor="w", pady=(0, 5))
        tk.Label(col2, text="Uncheck to exclude someone", font=("Arial", 8, "italic"),
                 bg="#FDFDFD", fg="#AAB7B8").pack(anchor="w", pady=(0, 10))
        canvas = tk.Canvas(col2, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(col2, orient="vertical", command=canvas.yview)
        self.recipient_frame = tk.Frame(canvas, bg="white")
        self.recipient_frame.bind("<Configure>",
                                  lambda e: canvas.configure(
                                      scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.recipient_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.final_recipient_vars = {}

        col3 = tk.Frame(main_frame, **fp)
        col3.pack(side="left", fill="both", expand=True)
        tk.Label(col3, text="MESSAGE CONTENT", font=lbl_font,
                 bg="#FDFDFD", fg="#5D6D7E").pack(anchor="w", pady=(0, 10))
        self.broadcast_msg_text = tk.Text(col3, height=12, font=("Arial", 11),
                                          bg="white", relief="flat",
                                          highlightthickness=1,
                                          highlightbackground="#D5DBDB")
        self.broadcast_msg_text.pack(fill="both", expand=True, pady=5)
        send_btn = tk.Label(col3, text="SEND ANNOUNCEMENT", bg="#2C3E50", fg="white",
                            font=("Arial", 10, "bold"), pady=15)
        send_btn.pack(fill="x", pady=10)
        send_btn.bind("<Button-1>", lambda e: self.send_final_broadcast())

    def sync_broadcast_list(self):
        for widget in self.recipient_frame.winfo_children():
            widget.destroy()
        self.final_recipient_vars = {}
        sel_courses = [c for c, v in self.course_vars.items() if v.get()]
        sel_indivs = [sid for sid, v in self.individual_vars.items() if v.get()]
        target_pool = {}
        for sid, data in self.students_db.items():
            if any(course in sel_courses for course in data['courses']) or sid in sel_indivs:
                target_pool[sid] = data['name']
        for sid, name in target_pool.items():
            var = tk.BooleanVar(value=True)
            self.final_recipient_vars[sid] = var
            f = tk.Frame(self.recipient_frame, bg="white")
            f.pack(fill="x", pady=2)
            tk.Checkbutton(f, text=name, variable=var, bg="white",
                           activebackground="white",
                           font=("Arial", 10)).pack(side="left")

    def send_final_broadcast(self):
        recipients = [sid for sid, v in self.final_recipient_vars.items() if v.get()]
        msg = self.broadcast_msg_text.get("1.0", tk.END).strip()
        if not recipients:
            messagebox.showwarning("Warning", "Recipients list is empty!")
            return
        if not msg:
            messagebox.showwarning("Warning", "Message cannot be empty!")
            return
        for sid in recipients:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.students_db[sid]['last_msg'] = (
                f"📢 BROADCAST ({ts}):\n{msg}\n" + "-" * 20 + "\n"
                + self.students_db[sid]['last_msg']
            )
        messagebox.showinfo("Success", f"Broadcast sent to {len(recipients)} students!")
        self.broadcast_msg_text.delete("1.0", tk.END)
        self.show_announcements()

    # ── 7) NOTIFICATIONS ──────────────────────────────────────────────────────
    def show_notifications(self):
        self.clear_content()
        tk.Label(self.main_content, text="NOTIFICATIONS", font=("Arial", 24, "bold"),
                 bg=self.bg_color, fg=self.sidebar_color).pack(anchor="w", pady=(0, 20))

        no_notif_frame = tk.Frame(self.main_content, bg="#F4F6F7", pady=20)
        no_notif_frame.pack(fill="x", pady=(0, 30))
        tk.Label(no_notif_frame, text="✨ Şu an yeni bir bildiriminiz bulunmuyor.",
                 font=("Arial", 11), bg="#F4F6F7", fg="#7F8C8D").pack()

        tk.Label(self.main_content, text="Recent Activities", font=("Arial", 12, "bold"),
                 bg=self.bg_color, fg="#34495E").pack(anchor="w", pady=(10, 10))

        past_notifications = [
            {"msg": "Python Programming dersi için yoklama tamamlandı.", "date": "Bugün, 10:30"},
            {"msg": "Nisa Aktaş mesajınıza yanıt verdi.", "date": "Dün, 15:45"},
            {"msg": "Sistem güncellemesi başarıyla tamamlandı.", "date": "2 gün önce"},
        ]
        for notif in past_notifications:
            box = tk.Frame(self.main_content, bg="white", highlightthickness=1,
                           highlightbackground="#D5DBDB", pady=10, padx=15)
            box.pack(fill="x", pady=5)
            tk.Label(box, text=notif['msg'], font=("Arial", 10), bg="white").pack(side="left")
            tk.Label(box, text=notif['date'], font=("Arial", 9),
                     bg="white", fg="#BDC3C7").pack(side="right")

    # ── 8) LOGOUT ─────────────────────────────────────────────────────────────
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to return to the login screen?"):
            for widget in self.root.winfo_children():
                widget.destroy()
            from ui.LoginWindow import LoginWindow
            LoginWindow(self.root, self.root.on_login_success_callback)