from app import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import uuid

# Define the User model
# This model represents the users table in the database
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(50))
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    api_key = db.Column(db.String(100), nullable=True, index=True, unique=True)
    
    # Relationships are defined in their respective models:
    # documents = relationship in Document model
    # conversations = relationship in Conversation model

    def __repr__(self):
        return f"<User {self.email}>"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate a unique token for password reset and set expiry"""
        token = str(uuid.uuid4())
        self.reset_token = token
        self.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)  # Token valid for 24 hours
        return token
    
    def verify_reset_token(self, token):
        """Verify if the reset token is valid and not expired"""
        if self.reset_token != token:
            return False
            
        if not self.reset_token_expiry or datetime.now(timezone.utc) > self.reset_token_expiry:
            return False
            
        return True
    
    def clear_reset_token(self):
        """Clear the reset token after it has been used"""
        self.reset_token = None
        self.reset_token_expiry = None
    
    def generate_api_key(self):
        """Generate a new API key for the user"""
        self.api_key = str(uuid.uuid4())
        return self.api_key 
