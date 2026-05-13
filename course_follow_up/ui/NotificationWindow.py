import tkinter as tk
from tkinter import ttk, messagebox


class NotificationWindow:
    """
    Hem TeacherWindow hem StudentWindow içinden çağrılır.
    Kullanım:
        NotificationWindow.show(parent_frame, user_info, services, colors)
    """

    @staticmethod
    def show(parent_frame, user_info, services, colors):
        inst = NotificationWindow(parent_frame, user_info, services, colors)
        inst._render()

    def __init__(self, parent_frame, user_info, services, colors):
        self.frame = parent_frame
        self.user_info = user_info
        self.services = services
        self.colors = colors
        self.notification_service = services["notification"]
        self.user_id = user_info.get("user_id")

    def _clear(self):
        for w in self.frame.winfo_children():
            w.destroy()

    def _render(self):
        self._clear()
        self._build_header()
        self._build_list()

    # ------------------------------------------------------------------ #
    #  HEADER
    # ------------------------------------------------------------------ #
    def _build_header(self):
        bar = tk.Frame(self.frame, bg=self.colors.get("bg", "#F8FAFC"))
        bar.pack(fill="x", pady=(0, 15))

        tk.Label(bar, text="NOTIFICATIONS", font=("Arial", 18, "bold"),
                 bg=self.colors.get("bg", "#F8FAFC"),
                 fg=self.colors.get("text_dark", "#0F172A")).pack(side="left")

        try:
            unread = self.notification_service.get_unread_count(self.user_id)
        except Exception:
            unread = 0

        if unread:
            badge = tk.Label(bar, text=f" {unread} new ",
                             font=("Arial", 8, "bold"),
                             bg="#EF4444", fg="white", padx=5, pady=2)
            badge.pack(side="left", padx=10)

        mark_btn = tk.Label(bar, text="Mark all as read",
                            font=("Arial", 9, "bold"),
                            bg=self.colors.get("sidebar", "#1E293B"),
                            fg="white", padx=12, pady=6, cursor="hand2")
        mark_btn.pack(side="right")
        mark_btn.bind("<Button-1>", lambda e: self._mark_all())

    # ------------------------------------------------------------------ #
    #  BİLDİRİM LİSTESİ
    # ------------------------------------------------------------------ #
    def _build_list(self):
        try:
            rows = self.notification_service.get_notifications(self.user_id)
        except Exception as ex:
            tk.Label(self.frame, text=f"Error: {ex}",
                     bg=self.colors.get("bg", "#F8FAFC"), fg="#EF4444").pack()
            return

        if not rows:
            tk.Label(self.frame,
                     text="You have no notifications.",
                     font=("Arial", 11),
                     bg=self.colors.get("bg", "#F8FAFC"),
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
            # row: (notification_id, title, body, is_read, created_at)
            notif_id, title, body, is_read, created_at = row
            is_unread = not is_read

            card = tk.Frame(list_frame,
                            bg="white" if not is_unread else "#EFF6FF",
                            pady=12, padx=15,
                            highlightthickness=1, highlightbackground="#E2E8F0")
            card.pack(fill="x", pady=3)

            left = tk.Frame(card, bg=card["bg"])
            left.pack(side="left", fill="x", expand=True)

            title_font = ("Arial", 10, "bold") if is_unread else ("Arial", 10)
            tk.Label(left, text=title, font=title_font,
                     bg=card["bg"],
                     fg=self.colors.get("text_dark", "#0F172A")).pack(anchor="w")
            tk.Label(left, text=body, font=("Arial", 9),
                     bg=card["bg"],
                     fg=self.colors.get("text_light", "#64748B"),
                     wraplength=600, justify="left").pack(anchor="w")

            right = tk.Frame(card, bg=card["bg"])
            right.pack(side="right")

            tk.Label(right, text=created_at[:16] if created_at else "",
                     font=("Arial", 8),
                     bg=card["bg"],
                     fg=self.colors.get("text_light", "#64748B")).pack(anchor="e")

            if is_unread:
                tk.Label(right, text="● NEW",
                         font=("Arial", 7, "bold"),
                         bg=card["bg"], fg="#3B82F6").pack(anchor="e", pady=(4, 0))

            del_btn = tk.Label(right, text="✕",
                               font=("Arial", 9, "bold"),
                               bg=card["bg"], fg="#EF4444",
                               cursor="hand2")
            del_btn.pack(anchor="e", pady=(4, 0))
            del_btn.bind("<Button-1>", lambda e, nid=notif_id: self._delete(nid))

            if is_unread:
                card.bind("<Button-1>", lambda e, nid=notif_id: self._mark_one(nid))
                left.bind("<Button-1>", lambda e, nid=notif_id: self._mark_one(nid))

    # ------------------------------------------------------------------ #
    #  ACTIONS
    # ------------------------------------------------------------------ #
    def _mark_all(self):
        try:
            self.notification_service.mark_all_as_read(self.user_id)
            self._render()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _mark_one(self, notif_id):
        try:
            self.notification_service.mark_as_read(notif_id)
            self._render()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _delete(self, notif_id):
        if messagebox.askyesno("Delete", "Delete this notification?"):
            try:
                self.notification_service.delete_notification(notif_id)
                self._render()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))