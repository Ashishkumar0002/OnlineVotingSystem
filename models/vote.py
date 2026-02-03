# ========================================
# VOTE MODEL - Database table for votes
# ========================================
# This file defines the Vote table structure
# Stores records of votes cast by voters

from models import db
from datetime import datetime

class Vote(db.Model):
    """
    Vote model records each vote cast by a voter
    This ensures we track who voted for whom and when
    """
    
    __tablename__ = 'votes'  # Name of the database table
    
    # Primary key - unique identifier for each vote record
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key - voter who cast this vote
    # This links to the Voter table
    voter_id = db.Column(db.Integer, db.ForeignKey('voters.id'), nullable=False)
    
    # Foreign key - candidate who received this vote
    # This links to the Candidate table
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    
    # When was this vote cast?
    voted_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        """
        This function returns a string representation of the vote
        Useful for debugging
        """
        return f'<Vote voter_id={self.voter_id} candidate_id={self.candidate_id}>'
