import tkinter as tk
from tkinter import ttk, messagebox
from services.course_service import CourseService


class CourseWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Course Management")
        self.root.geometry("900x600")

        self.course_service = CourseService()
        self.selected_course_id = None

        self.create_widgets()
        self.load_courses()

    def create_widgets(self):
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Course Management", font=("Arial", 18, "bold")).pack(pady=10)

        form = ttk.LabelFrame(container, text="Course Information", padding=15)
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="Course ID:").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.entry_course_id = ttk.Entry(form, width=35)
        self.entry_course_id.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(form, text="Course Name:").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        self.entry_course_name = ttk.Entry(form, width=35)
        self.entry_course_name.grid(row=1, column=1, padx=5, pady=8)

        ttk.Label(form, text="Course Code:").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        self.entry_course_code = ttk.Entry(form, width=35)
        self.entry_course_code.grid(row=2, column=1, padx=5, pady=8)

        ttk.Label(form, text="Credit:").grid(row=3, column=0, sticky="w", padx=5, pady=8)
        self.entry_credit = ttk.Entry(form, width=35)
        self.entry_credit.grid(row=3, column=1, padx=5, pady=8)

        button_frame = ttk.Frame(container)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Add", command=self.add_course).grid(row=0, column=0, padx=8)
        ttk.Button(button_frame, text="Update", command=self.update_course).grid(row=0, column=1, padx=8)
        ttk.Button(button_frame, text="Delete", command=self.delete_course).grid(row=0, column=2, padx=8)
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).grid(row=0, column=3, padx=8)

        table_frame = ttk.Frame(container)
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = ("Course ID", "Course Name", "Course Code", "Credit")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=180)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        self.clear_fields(reset_selection=False)
        self.selected_course_id = int(values[0])

        self.entry_course_id.insert(0, values[0])
        self.entry_course_name.insert(0, values[1])
        self.entry_course_code.insert(0, values[2])
        self.entry_credit.insert(0, values[3])

    def add_course(self):
        course_id = self.entry_course_id.get().strip()
        course_name = self.entry_course_name.get().strip()
        course_code = self.entry_course_code.get().strip()
        credit = self.entry_credit.get().strip()

        if not course_id or not course_name or not course_code or not credit:
            messagebox.showwarning("Missing Information", "Please fill in all course fields.")
            return

        if not course_id.isdigit():
            messagebox.showwarning("Invalid Course ID", "Course ID must contain only numbers.\nExample: 201")
            return

        if not credit.isdigit():
            messagebox.showwarning("Invalid Credit", "Credit must contain only numbers.\nExample: 3")
            return

        try:
            self.course_service.add_course(int(course_id), course_name, course_code, int(credit))
            messagebox.showinfo("Success", "Course added successfully.")
            self.clear_fields()
            self.load_courses()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_course(self):
        if self.selected_course_id is None:
            messagebox.showwarning("No Selection", "Please select a course from the table before updating.")
            return

        course_name = self.entry_course_name.get().strip()
        course_code = self.entry_course_code.get().strip()
        credit = self.entry_credit.get().strip()

        if not course_name or not course_code or not credit:
            messagebox.showwarning("Missing Information", "Please fill in course name, code and credit fields.")
            return

        if not credit.isdigit():
            messagebox.showwarning("Invalid Credit", "Credit must contain only numbers.\nExample: 3")
            return

        try:
            self.course_service.update_course(self.selected_course_id, course_name, course_code, int(credit))
            messagebox.showinfo("Success", "Course updated successfully.")
            self.clear_fields()
            self.load_courses()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_course(self):
        if self.selected_course_id is None:
            messagebox.showwarning("No Selection", "Please select a course from the table before deleting.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this course?")
        if confirm:
            try:
                self.course_service.delete_course(self.selected_course_id)
                messagebox.showinfo("Success", "Course deleted successfully.")
                self.clear_fields()
                self.load_courses()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_courses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for course in self.course_service.get_all_courses():
            self.tree.insert("", tk.END, values=course)

    def clear_fields(self, reset_selection=True):
        if reset_selection:
            self.selected_course_id = None
            self.tree.selection_remove(self.tree.selection())

        self.entry_course_id.delete(0, tk.END)
        self.entry_course_name.delete(0, tk.END)
        self.entry_course_code.delete(0, tk.END)
        self.entry_credit.delete(0, tk.END)