from app import db
from datetime import datetime, timezone

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    document_id = db.Column(db.BigInteger, db.ForeignKey('documents.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False, default='New Conversation')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('conversations', lazy=True))
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.id} (Doc: {self.document_id}, User: {self.user_id})>"
