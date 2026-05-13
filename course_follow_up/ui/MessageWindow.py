import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class MessageWindow:
    """
    Hem TeacherWindow hem StudentWindow içinden çağrılır.
    Kullanım:
        MessageWindow.show(parent_frame, user_info, services, colors)
    """

    @staticmethod
    def show(parent_frame, user_info, services, colors):
        inst = MessageWindow(parent_frame, user_info, services, colors)
        inst._render()

    def __init__(self, parent_frame, user_info, services, colors):
        self.frame = parent_frame
        self.user_info = user_info
        self.services = services
        self.colors = colors
        self.message_service = services["message"]
        self.user_id = user_info.get("user_id")

        # Aktif görünüm: "inbox" | "sent" | "compose" | "detail"
        self.current_view = "inbox"
        self.selected_message = None

    # ------------------------------------------------------------------ #
    #  ANA RENDER
    # ------------------------------------------------------------------ #
    def _render(self):
        self._clear()
        self._build_toolbar()
        self._build_body()

    def _clear(self):
        for w in self.frame.winfo_children():
            w.destroy()

    # ------------------------------------------------------------------ #
    #  ÜST ARAÇ ÇUBUĞU
    # ------------------------------------------------------------------ #
    def _build_toolbar(self):
        bar = tk.Frame(self.frame, bg=self.colors.get("bg", "#F8FAFC"))
        bar.pack(fill="x", pady=(0, 15))

        tk.Label(bar, text="MESSAGES", font=("Arial", 18, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC"),
                 fg=self.colors.get("text_dark", "#0F172A")).pack(side="left")

        # Okunmamış sayacı
        try:
            unread = self.message_service.get_unread_count(self.user_id)
        except Exception:
            unread = 0

        if unread:
            badge = tk.Label(bar, text=f" {unread} unread ",
                             font=("Arial", 8, "bold"),
                             bg="#EF4444", fg="white", padx=5, pady=2)
            badge.pack(side="left", padx=10)

        # Tab butonları
        btn_style = {"font": ("Arial", 9, "bold"), "padx": 15, "pady": 8, "cursor": "hand2"}
        sidebar_c = self.colors.get("sidebar", "#1E293B")
        accent_c = self.colors.get("accent", "#3B82F6")

        for label, view in [("INBOX", "inbox"), ("SENT", "sent")]:
            active = (self.current_view == view)
            btn = tk.Label(bar, text=label,
                           bg=sidebar_c if active else "#E2E8F0",
                           fg="white" if active else "#64748B",
                           **btn_style)
            btn.pack(side="left", padx=3)
            btn.bind("<Button-1>", lambda e, v=view: self._switch_view(v))

        compose_btn = tk.Label(bar, text="+ COMPOSE",
                               bg=accent_c, fg="white", **btn_style)
        compose_btn.pack(side="right")
        compose_btn.bind("<Button-1>", lambda e: self._switch_view("compose"))

    # ------------------------------------------------------------------ #
    #  GÖRÜNÜM GEÇİŞİ
    # ------------------------------------------------------------------ #
    def _switch_view(self, view):
        self.current_view = view
        self._render()

    def _build_body(self):
        if self.current_view == "inbox":
            self._build_message_list(inbox=True)
        elif self.current_view == "sent":
            self._build_message_list(inbox=False)
        elif self.current_view == "compose":
            self._build_compose()
        elif self.current_view == "detail":
            self._build_detail()

    # ------------------------------------------------------------------ #
    #  MESAJ LİSTESİ (INBOX / SENT)
    # ------------------------------------------------------------------ #
    def _build_message_list(self, inbox=True):
        try:
            if inbox:
                rows = self.message_service.get_inbox(self.user_id)
            else:
                rows = self.message_service.get_sent(self.user_id)
        except Exception as ex:
            tk.Label(self.frame, text=f"Error loading messages: {ex}",
                     bg=self.colors.get("bg", "#F8FAFC"), fg="#EF4444").pack()
            return

        if not rows:
            tk.Label(self.frame,
                     text="No messages here yet." if inbox else "No sent messages.",
                     font=("Arial", 11), bg=self.colors.get("bg", "#F8FAFC"),
                     fg=self.colors.get("text_light", "#64748B")).pack(pady=40)
            return

        canvas = tk.Canvas(self.frame, bg=self.colors.get("bg", "#F8FAFC"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        list_frame = tk.Frame(canvas, bg=self.colors.get("bg", "#F8FAFC"))

        list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for row in rows:
            # row: (message_id, other_user_id, other_username, subject, body, is_read, sent_at)
            msg_id, _, other_name, subject, body, is_read, sent_at = row
            is_unread = not is_read and inbox

            card = tk.Frame(list_frame, bg="white" if not is_unread else "#EFF6FF",
                            pady=12, padx=15,
                            highlightthickness=1, highlightbackground="#E2E8F0")
            card.pack(fill="x", pady=3)

            left = tk.Frame(card, bg=card["bg"])
            left.pack(side="left", fill="x", expand=True)

            name_font = ("Arial", 10, "bold") if is_unread else ("Arial", 10)
            tk.Label(left, text=other_name, font=name_font,
                     bg=card["bg"], fg=self.colors.get("text_dark", "#0F172A")).pack(anchor="w")

            preview = (subject or "") + (" — " if subject else "") + body[:60] + ("..." if len(body) > 60 else "")
            tk.Label(left, text=preview, font=("Arial", 9),
                     bg=card["bg"], fg=self.colors.get("text_light", "#64748B")).pack(anchor="w")

            right = tk.Frame(card, bg=card["bg"])
            right.pack(side="right")
            tk.Label(right, text=sent_at[:16] if sent_at else "",
                     font=("Arial", 8), bg=card["bg"],
                     fg=self.colors.get("text_light", "#64748B")).pack(anchor="e")

            if is_unread:
                tk.Label(right, text="● NEW", font=("Arial", 7, "bold"),
                         bg=card["bg"], fg="#3B82F6").pack(anchor="e")

            for widget in [card, left, right]:
                widget.bind("<Button-1>", lambda e, r=row: self._open_detail(r))
            card.bind("<Enter>", lambda e, c=card: c.config(bg="#F8FAFC"))
            card.bind("<Leave>", lambda e, c=card, orig=card["bg"]: c.config(bg=orig))

    # ------------------------------------------------------------------ #
    #  MESAJ DETAYI
    # ------------------------------------------------------------------ #
    def _open_detail(self, row):
        self.selected_message = row
        self.current_view = "detail"
        # Okundu olarak işaretle
        try:
            self.message_service.mark_as_read(row[0])
        except Exception:
            pass
        self._render()

    def _build_detail(self):
        if not self.selected_message:
            self._switch_view("inbox")
            return

        msg_id, _, other_name, subject, body, is_read, sent_at = self.selected_message

        # Geri butonu
        back = tk.Label(self.frame, text="← Back to Inbox",
                        font=("Arial", 9, "bold"), bg=self.colors.get("bg", "#F8FAFC"),
                        fg=self.colors.get("accent", "#3B82F6"), cursor="hand2")
        back.pack(anchor="w", pady=(0, 15))
        back.bind("<Button-1>", lambda e: self._switch_view("inbox"))

        # Başlık kartı
        header = tk.Frame(self.frame, bg="#F1F5F9", padx=20, pady=15,
                          highlightthickness=1, highlightbackground="#CBD5E1")
        header.pack(fill="x")
        tk.Label(header, text=f"From: {other_name}", font=("Arial", 12, "bold"),
                 bg="#F1F5F9", fg=self.colors.get("text_dark", "#0F172A")).pack(anchor="w")
        if subject:
            tk.Label(header, text=f"Subject: {subject}", font=("Arial", 10),
                     bg="#F1F5F9", fg=self.colors.get("text_light", "#64748B")).pack(anchor="w")
        tk.Label(header, text=sent_at[:16] if sent_at else "",
                 font=("Arial", 9), bg="#F1F5F9",
                 fg=self.colors.get("text_light", "#64748B")).pack(anchor="w")

        # Mesaj gövdesi
        body_box = tk.Text(self.frame, font=("Arial", 11), bg="white", bd=0,
                           highlightthickness=1, highlightbackground="#E2E8F0",
                           padx=15, pady=15, wrap="word", height=10)
        body_box.insert("1.0", body)
        body_box.config(state="disabled")
        body_box.pack(fill="x", pady=15)

        # Yanıt alanı
        tk.Label(self.frame, text="Reply:", font=("Arial", 9, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC")).pack(anchor="w")
        reply_box = tk.Text(self.frame, height=5, font=("Arial", 11), bd=0,
                            highlightthickness=1, highlightbackground="#E2E8F0", padx=10, pady=10)
        reply_box.pack(fill="x", pady=5)

        btn_frame = tk.Frame(self.frame, bg=self.colors.get("bg", "#F8FAFC"))
        btn_frame.pack(fill="x", pady=10)

        send_btn = tk.Label(btn_frame, text="SEND REPLY",
                            bg=self.colors.get("sidebar", "#1E293B"), fg="white",
                            font=("Arial", 9, "bold"), padx=20, pady=10, cursor="hand2")
        send_btn.pack(side="left")
        send_btn.bind("<Button-1>", lambda e: self._send_reply(_, reply_box))

        del_btn = tk.Label(btn_frame, text="DELETE",
                           bg="#EF4444", fg="white",
                           font=("Arial", 9, "bold"), padx=20, pady=10, cursor="hand2")
        del_btn.pack(side="left", padx=10)
        del_btn.bind("<Button-1>", lambda e: self._delete_message(msg_id))

    def _send_reply(self, receiver_id, reply_box):
        content = reply_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Reply cannot be empty.")
            return
        try:
            self.message_service.send_message(
                sender_id=self.user_id,
                receiver_id=receiver_id,
                body=content
            )
            messagebox.showinfo("Sent", "Reply sent successfully.")
            self._switch_view("inbox")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _delete_message(self, msg_id):
        if messagebox.askyesno("Delete", "Delete this message?"):
            try:
                self.message_service.delete_message(msg_id)
                self._switch_view("inbox")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

    # ------------------------------------------------------------------ #
    #  YENİ MESAJ OLUŞTUR
    # ------------------------------------------------------------------ #
    def _build_compose(self):
        tk.Label(self.frame, text="New Message", font=("Arial", 14, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC"),
                 fg=self.colors.get("text_dark", "#0F172A")).pack(anchor="w", pady=(0, 15))

        form = tk.Frame(self.frame, bg=self.colors.get("bg", "#F8FAFC"))
        form.pack(fill="x")

        # Alıcı kullanıcı ID girişi
        tk.Label(form, text="Receiver User ID:", font=("Arial", 9, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC")).grid(row=0, column=0, sticky="w", pady=5)
        receiver_entry = tk.Entry(form, font=("Arial", 10), bd=0,
                                  highlightthickness=1, highlightbackground="#E2E8F0", width=30)
        receiver_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5, ipady=6)

        tk.Label(form, text="Subject (optional):", font=("Arial", 9, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC")).grid(row=1, column=0, sticky="w", pady=5)
        subject_entry = tk.Entry(form, font=("Arial", 10), bd=0,
                                 highlightthickness=1, highlightbackground="#E2E8F0", width=30)
        subject_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5, ipady=6)

        form.columnconfigure(1, weight=1)

        tk.Label(self.frame, text="Message:", font=("Arial", 9, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC")).pack(anchor="w", pady=(15, 5))
        msg_box = tk.Text(self.frame, height=10, font=("Arial", 11), bd=0,
                          highlightthickness=1, highlightbackground="#E2E8F0", padx=10, pady=10)
        msg_box.pack(fill="x")

        btn_frame = tk.Frame(self.frame, bg=self.colors.get("bg", "#F8FAFC"))
        btn_frame.pack(fill="x", pady=15)

        send_btn = tk.Label(btn_frame, text="SEND MESSAGE",
                            bg=self.colors.get("accent", "#3B82F6"), fg="white",
                            font=("Arial", 9, "bold"), padx=20, pady=10, cursor="hand2")
        send_btn.pack(side="left")
        send_btn.bind("<Button-1>", lambda e: self._send_new(receiver_entry, subject_entry, msg_box))

        cancel_btn = tk.Label(btn_frame, text="CANCEL",
                              bg="#94A3B8", fg="white",
                              font=("Arial", 9, "bold"), padx=20, pady=10, cursor="hand2")
        cancel_btn.pack(side="left", padx=10)
        cancel_btn.bind("<Button-1>", lambda e: self._switch_view("inbox"))

    def _send_new(self, receiver_entry, subject_entry, msg_box):
        receiver_raw = receiver_entry.get().strip()
        subject = subject_entry.get().strip() or None
        body = msg_box.get("1.0", tk.END).strip()

        if not receiver_raw.isdigit():
            messagebox.showwarning("Warning", "Receiver User ID must be a number.")
            return
        if not body:
            messagebox.showwarning("Warning", "Message body cannot be empty.")
            return

        try:
            self.message_service.send_message(
                sender_id=self.user_id,
                receiver_id=int(receiver_raw),
                body=body,
                subject=subject
            )
            messagebox.showinfo("Sent", "Message sent successfully.")
            self._switch_view("sent")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))