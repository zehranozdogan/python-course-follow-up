import tkinter as tk
from tkinter import messagebox
from database.db_manager import DatabaseManager

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        
        # Ekran Sabitleme
        self.root.title("University Portal")
        self.root.configure(bg="#1E293B") 

        # --- DEV BEYAZ KART ---
        self.card = tk.Frame(self.root, bg="white", highlightthickness=0)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.config(width=550, height=600)
        self.card.pack_propagate(False)

        # Başlıklar
        tk.Label(self.card, text="Welcome Back", font=("Arial", 32, "bold"), 
                 bg="white", fg="#0F172A").pack(pady=(60, 10))
        
        tk.Label(self.card, text="Please enter your details to sign in", font=("Arial", 11), 
                 bg="white", fg="#64748B").pack(pady=(0, 50))

        # --- GİRİŞ ALANLARI ---
        label_cfg = {"bg": "white", "fg": "#475569", "font": ("Arial", 10, "bold")}
        entry_cfg = {"font": ("Arial", 14), "bd": 0, "bg": "#F8FAFC", 
                     "highlightthickness": 1, "highlightbackground": "#E2E8F0"}

        # ID / Name
        tk.Label(self.card, text="NAME OR STUDENT ID", **label_cfg).pack(anchor="w", padx=60)
        self.username_entry = tk.Entry(self.card, **entry_cfg)
        self.username_entry.pack(fill="x", pady=(8, 35), ipady=15, padx=60)
        self.username_entry.focus_set() # İmleç otomatik burada başlar

        # Password
        tk.Label(self.card, text="PASSWORD", **label_cfg).pack(anchor="w", padx=60)
        self.password_entry = tk.Entry(self.card, show="*", **entry_cfg)
        self.password_entry.pack(fill="x", pady=(8, 50), ipady=15, padx=60)

        # --- ENTER TUŞU BAĞLANTISI ---
        # Klavye üzerinden Enter'a (Return) basıldığında handle_login çalışır
        self.root.bind('<Return>', lambda event: self.handle_login())

        # --- PARLAMAYAN BUTON (Label Metodu) ---
        self.login_btn = tk.Label(self.card, text="SIGN IN", 
                                  bg="#0F172A", fg="white", 
                                  font=("Arial", 12, "bold"), 
                                  pady=20, cursor="arrow")
        self.login_btn.pack(fill="x", padx=60)
        
        # Mouse olayları
        self.login_btn.bind("<Button-1>", lambda e: self.handle_login())
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg="#1E293B"))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg="#0F172A"))

        # Alt Bilgi
        tk.Label(self.card, text="Forgot Password?", font=("Arial", 10), 
                 bg="white", fg="#3B82F6").pack(pady=(35, 0))

    def handle_login(self):
        # Boşlukları temizle (strip) ve küçük harfe çevir (lower)
        try:
            user_val = self.username_entry.get().strip().lower()
            pass_val = self.password_entry.get().strip()
        except Exception:
            return
        
        if not user_val or not pass_val:
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return
        
        db = DatabaseManager()
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                        SELECT username, role, student_id, instructor_id
                        FROM users
                        WHERE username = ? AND password = ?
                """, (user_val, pass_val))
                user_data = cursor.fetchone()

            if user_data:

                self.on_login_success({
                    "username": user_data[0], 
                    "role": user_data[1],
                    "student_id": user_data[2],
                    "instructor_id": user_data[3]
                })
            else:
                messagebox.showerror("Error", "Invalid credentials. Please try again.")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            