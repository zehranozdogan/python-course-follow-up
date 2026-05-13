from models.message import Message


class MessageService:
    def __init__(self, db_manager):
        self.db = db_manager

    def send_message(self, sender_id, receiver_id, body, subject=None):
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (sender_id, receiver_id, subject, body)
                    VALUES (?, ?, ?, ?)
                """, (sender_id, receiver_id, subject, body))
                conn.commit()
        except Exception as e:
            raise Exception(f"Message could not be sent: {e}")

    def get_inbox(self, user_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.message_id, m.sender_id, u.username, m.subject, m.body, m.is_read, m.sent_at
                FROM messages m
                JOIN users u ON m.sender_id = u.user_id
                WHERE m.receiver_id = ?
                ORDER BY m.sent_at DESC
            """, (user_id,))
            return cursor.fetchall()

    def get_sent(self, user_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.message_id, m.receiver_id, u.username, m.subject, m.body, m.is_read, m.sent_at
                FROM messages m
                JOIN users u ON m.receiver_id = u.user_id
                WHERE m.sender_id = ?
                ORDER BY m.sent_at DESC
            """, (user_id,))
            return cursor.fetchall()

    def mark_as_read(self, message_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE messages SET is_read = 1 WHERE message_id = ?", (message_id,))
            conn.commit()

    def delete_message(self, message_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
            conn.commit()

    def get_unread_count(self, user_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM messages
                WHERE receiver_id = ? AND is_read = 0
            """, (user_id,))
            return cursor.fetchone()[0]