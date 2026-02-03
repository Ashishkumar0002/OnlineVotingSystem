# ========================================
# VOTING LOG MODEL - Database table for voting records
# ========================================
# This file defines the VotingLog table structure
# Stores logs of voting activities for audit purposes

from models import db
from datetime import datetime

class VotingLog(db.Model):
    """
    VotingLog model records all voting activities
    This is used for audit trails and statistics
    """
    
    __tablename__ = 'voting_logs'  # Name of the database table
    
    # Primary key - unique identifier for each voting log entry
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key - voter who cast the vote
    # This links to the Voter table
    voter_id = db.Column(db.Integer, db.ForeignKey('voters.id'), nullable=False)
    
    # Action taken - can be 'vote_cast', 'vote_viewed', 'login', etc.
    action = db.Column(db.String(50), nullable=False)
    
    # Additional details about the action (as JSON or text)
    details = db.Column(db.Text, nullable=True)
    
    # IP address from which the action was performed
    ip_address = db.Column(db.String(45), nullable=True)
    
    # When was this action performed?
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        """
        This function returns a string representation of the voting log
        Useful for debugging
        """
        return f'<VotingLog voter_id={self.voter_id} action={self.action}>'
