import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class ScheduleWindow:
    """
    Hem TeacherWindow hem StudentWindow içinden çağrılır.
    Kullanım:
        ScheduleWindow.show(parent_frame, user_info, services, colors)
    """

    @staticmethod
    def show(parent_frame, user_info, services, colors):
        inst = ScheduleWindow(parent_frame, user_info, services, colors)
        inst._render()

    def __init__(self, parent_frame, user_info, services, colors):
        self.frame = parent_frame
        self.user_info = user_info
        self.services = services
        self.colors = colors
        self.schedule_service = services["schedule"]
        self.role = user_info.get("role")
        self.student_id = user_info.get("student_id")
        self.instructor_id = user_info.get("instructor_id")

        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    def _clear(self):
        for w in self.frame.winfo_children():
            w.destroy()

    def _render(self):
        self._clear()
        self._build_header()
        self._build_filter()
        self._build_table()
        self._load()

        # Öğretmen ise ekleme formu da göster
        if self.role == "teacher":
            self._build_add_form()

    # ------------------------------------------------------------------ #
    #  HEADER
    # ------------------------------------------------------------------ #
    def _build_header(self):
        bar = tk.Frame(self.frame, bg=self.colors.get("bg", "#F8FAFC"))
        bar.pack(fill="x", pady=(0, 10))

        tk.Label(bar, text="SCHEDULE", font=("Arial", 18, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC"),
                 fg=self.colors.get("text_dark", "#0F172A")).pack(side="left")

        now = datetime.now().strftime("%A, %d %B %Y")
        tk.Label(bar, text=now, font=("Arial", 10),
                 bg=self.colors.get("bg", "#F8FAFC"),
                 fg=self.colors.get("text_light", "#64748B")).pack(side="right")

    # ------------------------------------------------------------------ #
    #  FİLTRE
    # ------------------------------------------------------------------ #
    def _build_filter(self):
        f = tk.Frame(self.frame, bg=self.colors.get("bg", "#F8FAFC"))
        f.pack(fill="x", pady=(0, 10))

        tk.Label(f, text="Filter by day:", font=("Arial", 9, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC")).pack(side="left")

        self.day_filter = ttk.Combobox(f, values=["All Days"] + self.days,
                                       state="readonly", width=15)
        self.day_filter.set("All Days")
        self.day_filter.pack(side="left", padx=8)
        self.day_filter.bind("<<ComboboxSelected>>", lambda e: self._load())

        refresh_btn = tk.Label(f, text="↻ Refresh",
                               font=("Arial", 9, "bold"),
                               bg=self.colors.get("sidebar", "#1E293B"),
                               fg="white", padx=10, pady=5, cursor="hand2")
        refresh_btn.pack(side="right")
        refresh_btn.bind("<Button-1>", lambda e: self._load())

    # ------------------------------------------------------------------ #
    #  TABLO
    # ------------------------------------------------------------------ #
    def _build_table(self):
        cols = ("Course", "Code", "Day", "Start", "End", "Classroom", "Status")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=10)

        widths = {"Course": 180, "Code": 90, "Day": 100,
                  "Start": 70, "End": 70, "Classroom": 90, "Status": 80}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=widths.get(col, 100))

        self.tree.tag_configure("today", background="#EFF6FF", foreground="#1D4ED8")
        self.tree.tag_configure("done",  background="#F0FDF4", foreground="#15803D")

        self.tree.pack(fill="x", pady=5)

    def _load(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            if self.role == "student" and self.student_id:
                rows = self.schedule_service.get_schedule_by_student(self.student_id)
                # (schedule_id, course_name, course_code, day, start, end, classroom)
                data = [(r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
            elif self.role == "teacher" and self.instructor_id:
                rows = self.schedule_service.get_schedule_by_instructor(self.instructor_id)
                data = [(r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
            else:
                data = []
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
            return

        day_sel = self.day_filter.get()
        today = datetime.now().strftime("%A")
        now_time = datetime.now().strftime("%H:%M")

        for course_name, course_code, day, start, end, classroom in data:
            if day_sel != "All Days" and day != day_sel:
                continue

            if day == today:
                status = "Done" if now_time > end else ("Now" if now_time >= start else "Upcoming")
                tag = "done" if status == "Done" else "today"
            else:
                status = ""
                tag = ""

            self.tree.insert("", "end",
                             values=(course_name, course_code, day, start, end,
                                     classroom or "TBA", status),
                             tags=(tag,) if tag else ())

    # ------------------------------------------------------------------ #
    #  EKLEME FORMU (sadece öğretmen)
    # ------------------------------------------------------------------ #
    def _build_add_form(self):
        sep = tk.Frame(self.frame, height=1, bg="#E2E8F0")
        sep.pack(fill="x", pady=15)

        tk.Label(self.frame, text="Add Schedule Entry",
                 font=("Arial", 12, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC"),
                 fg=self.colors.get("text_dark", "#0F172A")).pack(anchor="w", pady=(0, 10))

        form = tk.Frame(self.frame, bg=self.colors.get("bg", "#F8FAFC"))
        form.pack(fill="x")

        # Kurs seçimi
        try:
            course_service = self.services.get("course")
            if self.instructor_id:
                courses_data = course_service.get_courses_by_instructor(self.instructor_id)
            else:
                courses_data = course_service.get_all_courses()
            course_map = {c[1]: c[0] for c in courses_data}
        except Exception:
            course_map = {}

        labels = ["Course", "Day", "Start (HH:MM)", "End (HH:MM)", "Classroom"]
        self.form_entries = {}

        for i, label in enumerate(labels):
            tk.Label(form, text=label + ":", font=("Arial", 9, "bold"),
                     bg=self.colors.get("bg", "#F8FAFC"),
                     width=16, anchor="w").grid(row=i, column=0, sticky="w", pady=4)

            if label == "Course":
                widget = ttk.Combobox(form, values=list(course_map.keys()),
                                      state="readonly", width=28)
            elif label == "Day":
                widget = ttk.Combobox(form, values=self.days,
                                      state="readonly", width=28)
            else:
                widget = tk.Entry(form, font=("Arial", 10), width=30, bd=0,
                                  highlightthickness=1, highlightbackground="#E2E8F0")

            widget.grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=4, ipady=5)
            self.form_entries[label] = widget

        form.columnconfigure(1, weight=1)
        self._course_map = course_map

        add_btn = tk.Label(self.frame, text="ADD TO SCHEDULE",
                           bg=self.colors.get("accent", "#3B82F6"),
                           fg="white", font=("Arial", 10, "bold"),
                           pady=10, cursor="hand2")
        add_btn.pack(fill="x", pady=10)
        add_btn.bind("<Button-1>", lambda e: self._save_entry())

    def _save_entry(self):
        course_name = self.form_entries["Course"].get()
        day = self.form_entries["Day"].get()
        start = self.form_entries["Start (HH:MM)"].get().strip()
        end = self.form_entries["End (HH:MM)"].get().strip()
        classroom = self.form_entries["Classroom"].get().strip() or None

        if not all([course_name, day, start, end]):
            messagebox.showwarning("Warning", "Please fill Course, Day, Start and End fields.")
            return

        course_id = self._course_map.get(course_name)
        if not course_id:
            messagebox.showwarning("Warning", "Invalid course selection.")
            return

        try:
            self.schedule_service.add_schedule(course_id, day, start, end, classroom)
            messagebox.showinfo("Success", "Schedule entry added.")
            self._load()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))