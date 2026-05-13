class Message:
    def __init__(self, message_id, sender_id, receiver_id, body, subject=None, is_read=0, sent_at=None):
        self.message_id = message_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.subject = subject
        self.body = body
        self.is_read = bool(is_read)
        self.sent_at = sent_at

    def __repr__(self):
        return f"Message(id={self.message_id}, from={self.sender_id}, to={self.receiver_id}, read={self.is_read})"