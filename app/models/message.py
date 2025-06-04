from app import db
from datetime import datetime, timezone

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.BigInteger, db.ForeignKey('conversations.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'assistant'
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Optional fields for tracking and analysis
    tokens_used = db.Column(db.Integer, nullable=True)
    context_pages = db.Column(db.Text, nullable=True)  # JSON list of page numbers used as context
    
    def __repr__(self):
        return f"<Message {self.id} ({self.role}, Conv: {self.conversation_id})>"
