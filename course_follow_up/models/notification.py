class Notification:
    def __init__(self, notification_id, user_id, title, body, is_read=0, created_at=None):
        self.notification_id = notification_id
        self.user_id = user_id
        self.title = title
        self.body = body
        self.is_read = bool(is_read)
        self.created_at = created_at

    def __repr__(self):
        return f"Notification(id={self.notification_id}, user={self.user_id}, read={self.is_read})"