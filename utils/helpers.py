# ========================================
# UTILITY FUNCTIONS - Helper functions for the application
# ========================================
# This file contains useful functions used throughout the application

import random
import string
from datetime import datetime, timedelta

# ===== OTP GENERATION =====
def generate_otp():
    """
    Generate a random 6-digit OTP (One Time Password)
    Used for voter verification before voting
    """
    # Create a random 6-digit number as a string
    otp = ''.join(random.choices(string.digits, k=6))
    return otp

# ===== VOTER ID GENERATION =====
def generate_voter_id():
    """
    Generate a unique Voter ID
    Format: VOTER_YYYYMMDD_RANDOM4DIGITS
    Example: VOTER_20260127_3847
    """
    # Get current date
    today = datetime.now().strftime('%Y%m%d')
    
    # Generate 4 random digits
    random_digits = ''.join(random.choices(string.digits, k=4))
    
    # Combine to create voter ID
    voter_id = f'VOTER_{today}_{random_digits}'
    
    return voter_id

# ===== VALIDATION FUNCTIONS =====
def validate_aadhaar(aadhaar_number):
    """
    Validate Aadhaar number format
    Aadhaar should be exactly 12 digits
    
    Parameters:
    aadhaar_number: The Aadhaar number to validate
    
    Returns:
    True if valid, False if invalid
    """
    # Check if it's a string and exactly 12 characters
    if isinstance(aadhaar_number, str) and len(aadhaar_number) == 12:
        # Check if all characters are digits
        return aadhaar_number.isdigit()
    return False

def validate_phone_number(phone_number):
    """
    Validate Indian phone number format
    Phone number should be exactly 10 digits
    
    Parameters:
    phone_number: The phone number to validate
    
    Returns:
    True if valid, False if invalid
    """
    # Check if it's a string and exactly 10 characters
    if isinstance(phone_number, str) and len(phone_number) == 10:
        # Check if all characters are digits
        return phone_number.isdigit()
    return False

def validate_password(password):
    """
    Validate password strength
    Password must contain:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    
    Parameters:
    password: The password to validate
    
    Returns:
    Tuple of (is_valid, error_message)
    """
    # Check minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase letter
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    # Check for special character
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    # If all checks pass, password is valid
    return True, "Password is valid"

def validate_email(email):
    """
    Validate email format
    Check if email has proper structure (something@domain.com)
    
    Parameters:
    email: The email address to validate
    
    Returns:
    True if valid, False if invalid
    """
    # Simple email validation
    if '@' in email and '.' in email:
        # Check if @ comes before .
        at_index = email.index('@')
        dot_index = email.index('.')
        if at_index < dot_index:
            return True
    return False

# ===== OTP TIMING =====
def get_otp_expiry_time(minutes=10):
    """
    Calculate the expiry time for an OTP
    By default, OTP expires after 10 minutes
    
    Parameters:
    minutes: Number of minutes before OTP expires (default 10)
    
    Returns:
    datetime object representing when OTP will expire
    """
    # Get current time and add the specified minutes
    expiry_time = datetime.now() + timedelta(minutes=minutes)
    return expiry_time

# ===== STATUS HELPER FUNCTIONS =====
def get_status_badge_class(status):
    """
    Get Bootstrap badge class based on status
    This is used to show colored status badges in templates
    
    Parameters:
    status: The status string ('pending', 'approved', 'rejected', etc.)
    
    Returns:
    Bootstrap badge class name
    """
    # Map status to Bootstrap badge colors
    status_colors = {
        'pending': 'badge bg-warning',      # Yellow
        'approved': 'badge bg-success',     # Green
        'rejected': 'badge bg-danger',      # Red
        'active': 'badge bg-primary',       # Blue
        'completed': 'badge bg-success'     # Green
    }
    
    # Return the appropriate class, or default if not found
    return status_colors.get(status, 'badge bg-secondary')

# ===== PAGINATION HELPER =====
def paginate(query, page=1, per_page=10):
    """
    Paginate a database query
    Splits results into pages for easier viewing
    
    Parameters:
    query: The database query to paginate
    page: The page number (default 1)
    per_page: Number of items per page (default 10)
    
    Returns:
    Paginated query object
    """
    # Flask-SQLAlchemy paginate method
    # Automatically handles limit and offset
    return query.paginate(page=page, per_page=per_page)
