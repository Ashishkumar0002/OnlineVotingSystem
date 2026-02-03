# ========================================
# VOTER MODEL - Database table for voters
# ========================================
# This file defines the Voter table structure
# Stores additional information about voters

from models import db
from datetime import datetime

class Voter(db.Model):
    """
    Voter model stores detailed information about voters
    This extends the basic User information with voting-specific fields
    """
    
    __tablename__ = 'voters'  # Name of the database table
    
    # Primary key - unique identifier for each voter
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key - links to the User table
    # This connects each voter to a user account
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Unique voter ID generated after approval
    voter_id = db.Column(db.String(50), unique=True, nullable=True)
    
    # Voter's date of birth
    date_of_birth = db.Column(db.Date, nullable=False)
    
    # Voter's father's name
    father_name = db.Column(db.String(120), nullable=False)
    
    # Voter's phone number (linked with Aadhaar)
    phone_number = db.Column(db.String(20), nullable=False)
    
    # Voter's Aadhaar card number (unique identification)
    aadhaar_number = db.Column(db.String(12), unique=True, nullable=False)
    
    # Voter's occupation (job)
    occupation = db.Column(db.String(100), nullable=False)
    
    # Has this voter already cast their vote?
    has_voted = db.Column(db.Boolean, default=False)
    
    # When did the voter cast their vote?
    voted_at = db.Column(db.DateTime, nullable=True)
    
    # Is the voter approved by admin?
    is_approved = db.Column(db.Boolean, default=False)
    
    # Registration status - 'pending', 'approved', or 'rejected'
    status = db.Column(db.String(20), default='pending')
    
    # When was this voter registered?
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # When was this voter last updated?
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        """
        This function returns a string representation of the voter
        Useful for debugging
        """
        return f'<Voter {self.voter_id}>'
