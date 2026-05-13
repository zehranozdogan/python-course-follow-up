
from models.notification import Notification


class NotificationService:
    def __init__(self, db_manager):
        self.db = db_manager

    def send_notification(self, user_id, title, body):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notifications (user_id, title, body)
                    VALUES (?, ?, ?)
                """, (user_id, title, body))
                conn.commit()
        except Exception as e:
            raise Exception(f"Notification could not be sent: {e}")

    def send_bulk_notification(self, user_ids, title, body):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.executemany("""
                    INSERT INTO notifications (user_id, title, body)
                    VALUES (?, ?, ?)
                """, [(uid, title, body) for uid in user_ids])
                conn.commit()
        except Exception as e:
            raise Exception(f"Bulk notification could not be sent: {e}")

    def get_notifications(self, user_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT notification_id, title, body, is_read, created_at
                FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            return cursor.fetchall()

    def mark_as_read(self, notification_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE notification_id = ?", (notification_id,))
            conn.commit()

    def mark_all_as_read(self, user_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
            conn.commit()

    def delete_notification(self, notification_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notifications WHERE notification_id = ?", (notification_id,))
            conn.commit()

    def get_unread_count(self, user_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM notifications
                WHERE user_id = ? AND is_read = 0
            """, (user_id,))
            return cursor.fetchone()[0]