from app import db
from datetime import datetime, timezone

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Name of file in storage
    original_filename = db.Column(db.String(255), nullable=False)  # Original name before upload
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=False, default='application/pdf')
    upload_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    processed = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.String(100), nullable=True)  # For API access
    page_count = db.Column(db.Integer, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('documents', lazy=True))
    
    def __repr__(self):
        return f"<Document {self.filename} (User: {self.user_id})>"