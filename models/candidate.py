# ========================================
# CANDIDATE MODEL - Database table for candidates
# ========================================
# This file defines the Candidate table structure
# Stores information about election candidates

from models import db
from datetime import datetime

class Candidate(db.Model):
    """
    Candidate model stores information about election candidates
    Each candidate can receive votes from voters
    """
    
    __tablename__ = 'candidates'  # Name of the database table
    
    # Primary key - unique identifier for each candidate
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key - links to the User table
    # This connects each candidate to a user account
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Candidate's nomination status - 'pending', 'approved', 'rejected', 'active'
    nomination_status = db.Column(db.String(20), default='pending')
    
    # Is the candidate's nomination approved by admin?
    is_approved = db.Column(db.Boolean, default=False)
    
    # Which party is the candidate contesting from?
    party_name = db.Column(db.String(100), nullable=False)
    
    # How many votes has this candidate received so far?
    total_votes = db.Column(db.Integer, default=0)
    
    # When was the candidate registration created?
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # When was the candidate registration last updated?
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        """
        This function returns a string representation of the candidate
        Useful for debugging
        """
        return f'<Candidate {self.user_id}>'
