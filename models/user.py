# ========================================
# USER MODEL - Database table for users
# ========================================
# This file defines the User table structure
# A User can be an Admin, Voter, or Candidate

from models import db
from datetime import datetime

class User(db.Model):
    """
    User model represents a user in the voting system
    This could be an admin, voter, or candidate
    """
    
    __tablename__ = 'users'  # Name of the database table
    
    # Primary key - unique identifier for each user
    id = db.Column(db.Integer, primary_key=True)
    
    # User's email address - must be unique
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # User's full name
    name = db.Column(db.String(120), nullable=False)
    
    # User's role - can be 'admin', 'voter', or 'candidate'
    role = db.Column(db.String(20), nullable=False, default='voter')
    
    # User's password (hashed for security)
    password = db.Column(db.String(255), nullable=False)
    
    # Path to user's profile image
    profile_image = db.Column(db.String(255), default='default.jpg')
    
    # Is the user's account verified (email verified)?
    is_verified = db.Column(db.Boolean, default=False)
    
    # When was this user account created?
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # When was this user account last updated?
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        """
        This function returns a string representation of the user
        Useful for debugging
        """
        return f'<User {self.email}>'
