import tkinter as tk
from tkinter import ttk, messagebox

class StudentProfileView:
    """GPA, Notlar, Devamsızlık ve Bilgilerin tam listelendiği ortak profil ekranı"""
    
    @staticmethod
    def show(parent_frame, data, colors, back_command):
        # Ekranı temizle
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # --- 1) ÜST BİLGİ ALANI (İsim, No, İletişim, GANO) ---
        header_f = tk.Frame(parent_frame, bg="#F4F6F7", padx=20, pady=20, 
                           highlightthickness=1, highlightbackground="#D5DBDB")
        header_f.pack(fill="x")
        
        # İsim ve Numara
        tk.Label(header_f, text=data.get('name', '').upper(), font=("Arial", 18, "bold"), 
                 bg="#F4F6F7", fg=colors.get("sidebar", "#2C3E50")).pack(anchor="w")
        tk.Label(header_f, text=f"Student ID: {data.get('id', data.get('no', 'N/A'))}", 
                 font=("Arial", 10), bg="#F4F6F7", fg="#7F8C8D").pack(anchor="w")
        
        # İletişim Bilgileri
        tk.Label(header_f, text=f"Mail: {data.get('email', 'N/A')} | TC: {data.get('tc', 'N/A')}", 
                 font=("Arial", 9), bg="#F4F6F7").pack(anchor="w", pady=(5, 0))

        # GANO (GPA) Kutusu - Sağ Üst
        if 'gpa' in data:
            gpa_frame = tk.Frame(header_f, bg="#2980B9", padx=15, pady=10)
            gpa_frame.place(relx=1.0, rely=0.5, anchor="e")
            tk.Label(gpa_frame, text=f"GANO: {data['gpa']}", fg="white", bg="#2980B9", 
                     font=("Arial", 14, "bold")).pack()

        # --- 2) NOTLAR TABLOSU ---
        tk.Label(parent_frame, text="GRADES", font=("Arial", 11, "bold"), 
                 bg=colors.get("bg", "#FFFFFF")).pack(anchor="w", pady=(20, 5))
        
        g_tree = ttk.Treeview(parent_frame, columns=("Course", "Grade"), show="headings", height=4)
        g_tree.heading("Course", text="Course Name")
        g_tree.heading("Grade", text="Grade")
        g_tree.pack(fill="x")
        
        if 'grades' in data:
            for course, grade in data['grades']:
                g_tree.insert("", "end", values=(course, grade))

        # --- 3) DEVAMSIZLIK TABLOSU (Ayrı Tablo) ---
        tk.Label(parent_frame, text="ATTENDANCE RECORDS", font=("Arial", 11, "bold"), 
                 bg=colors.get("bg", "#FFFFFF")).pack(anchor="w", pady=(20, 5))
        
        a_tree = ttk.Treeview(parent_frame, columns=("Course", "Status"), show="headings", height=4)
        a_tree.heading("Course", text="Course Name")
        a_tree.heading("Status", text="Attendance Status")
        a_tree.pack(fill="x")
        
        if 'attendance' in data:
            for course, status in data['attendance']:
                a_tree.insert("", "end", values=(course, status))

        # --- 4) EXPORT BUTONU (En Alt) ---
        export_f = tk.Frame(parent_frame, bg=colors.get("bg", "#FFFFFF"))
        export_f.pack(fill="x", pady=30)

        exp_btn = tk.Label(export_f, text="⬇ EXPORT ALL DATA (PDF)", bg="#27AE60", fg="white", 
                          font=("Arial", 10, "bold"), padx=20, pady=12, cursor="hand2")
        exp_btn.pack(side="left")
        exp_btn.bind("<Button-1>", lambda e: messagebox.showinfo("Export", "Student Report Exported!"))

        # --- 5) BACK TO LIST ---
        back_link = tk.Label(parent_frame, text="← Back to Students List", fg="#3498DB", 
                            bg=colors.get("bg", "#FFFFFF"), font=("Arial", 10, "bold"), cursor="hand2")
        back_link.pack(anchor="w")
        back_link.bind("<Button-1>", lambda e: back_command())


class StudentDetailView:
    @staticmethod
    def show(parent, student_id, services, colors, back_callback):
        for widget in parent.winfo_children():
            widget.destroy()

        student = services["student"].get_student_by_id(student_id)
        if not student:
            return

        tk.Label(parent, text=f"{student.name} {student.surname}".upper(),
                font=("Arial", 18, "bold"), bg=colors["bg"],
                fg=colors["sidebar"]).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text=f"ID: {student.student_id} | Department: {student.department}",
                font=("Arial", 10), bg=colors["bg"], fg="#64748B").pack(anchor="w", pady=(0, 20))

        gpa = services["grade"].calculate_gpa(student_id)
        enrollments = services["enrollment"].get_enrollments_by_student(student_id)

        stats_frame = tk.Frame(parent, bg=colors["bg"])
        stats_frame.pack(fill="x", pady=(0, 20))
        for title, val, color in [
            ("GPA", str(gpa), colors["sidebar"]),
            ("COURSES", str(len(enrollments)), "#10B981")
        ]:
            card = tk.Frame(stats_frame, bg="white", padx=20, pady=15,
                            highlightthickness=1, highlightbackground="#D5DBDB")
            card.pack(side="left", padx=(0, 10))
            tk.Label(card, text=title, font=("Arial", 8, "bold"),
                     bg="white", fg="#64748B").pack()
            tk.Label(card, text=val, font=("Arial", 18, "bold"),
                     bg="white", fg=color).pack()

        tk.Label(parent, text="TRANSCRIPT", font=("Arial", 12, "bold"),
                bg=colors["bg"]).pack(anchor="w", pady=(0, 10))

        cols = ("Course Code", "Course Name", "Credit", "Grade", "Status")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=8)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        for e in enrollments:
            tree.insert("", "end", values=(e[2], e[1], e[3], e[4] or "N/A", e[5]))
        tree.pack(fill="x")

        btn_f = tk.Frame(parent, bg=colors["bg"])
        btn_f.pack(fill="x", pady=20)
        tk.Button(btn_f, text="EXPORT PDF", bg=colors["sidebar"], fg="white",
                font=("Arial", 9, "bold"),
                command=lambda: StudentDetailView.export_pdf(student, gpa, enrollments),
                padx=20, pady=8).pack(side="left")
        tk.Button(btn_f, text="BACK TO LIST", bg="#EF4444", fg="white",
                font=("Arial", 9, "bold"), command=back_callback,
                padx=20, pady=8).pack(side="right")

    @staticmethod
    def export_pdf(student, gpa, enrollments):
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