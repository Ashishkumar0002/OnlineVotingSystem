# ========================================
# OTP LOG MODEL - Database table for OTP records
# ========================================
# This file defines the OtpLog table structure
# Stores OTP (One Time Password) information for voting verification

from models import db
from datetime import datetime

class OtpLog(db.Model):
    """
    OtpLog model stores OTP (One Time Password) records
    OTPs are used to verify the identity of voters before they vote
    """
    
    __tablename__ = 'otp_logs'  # Name of the database table
    
    # Primary key - unique identifier for each OTP record
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key - voter who requested this OTP
    # This links to the Voter table
    voter_id = db.Column(db.Integer, db.ForeignKey('voters.id'), nullable=False)
    
    # The actual OTP code (6 digits)
    otp_code = db.Column(db.String(6), nullable=False)
    
    # Has this OTP been verified/used?
    is_verified = db.Column(db.Boolean, default=False)
    
    # When was this OTP created?
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # When does this OTP expire?
    # OTPs are valid for a limited time (usually 10-15 minutes)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        """
        Check if this OTP has expired
        Returns True if current time is after expires_at
        """
        return datetime.now() > self.expires_at
    
    def __repr__(self):
        """
        This function returns a string representation of the OTP log
        Useful for debugging
        """
        return f'<OtpLog voter_id={self.voter_id}>'
