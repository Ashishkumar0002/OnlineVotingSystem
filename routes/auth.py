# ========================================
# AUTHENTICATION ROUTES
# ========================================
# This file contains all authentication-related routes
# Handles login, logout, and registration

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db
from models.user import User
from models.voter import Voter
from models.candidate import Candidate
from utils.helpers import validate_password, validate_email, validate_aadhaar, validate_phone_number, generate_voter_id
import os
from flask import current_app

# Create a blueprint for auth routes
# A blueprint is like a mini Flask app with its own routes
auth_bp = Blueprint('auth', __name__)

# ===== LOGIN ROUTE =====
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login
    Users enter email and password to access their dashboard
    """
    if request.method == 'POST':
        # Get email and password from the form
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'voter')  # Which role is logging in
        
        # Validate inputs
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('auth.login'))
        
        # Find user in database
        user = User.query.filter_by(email=email, role=role).first()
        
        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            # Password is correct - log the user in
            session['user_id'] = user.id
            session['role'] = user.role
            flash(f'Welcome {user.name}!', 'success')
            
            # Redirect to appropriate dashboard based on role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'voter':
                return redirect(url_for('voter.dashboard'))
            elif user.role == 'candidate':
                return redirect(url_for('candidate.dashboard'))
        else:
            # Login failed - wrong email or password
            flash('Invalid email, password, or role', 'error')
            return redirect(url_for('auth.login'))
    
    # Show login form (GET request)
    return render_template('auth/login.html')

# ===== LOGOUT ROUTE =====
@auth_bp.route('/logout')
def logout():
    """
    Handle user logout
    Clear the session to log the user out
    """
    # Remove user from session
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))

# ===== VOTER REGISTRATION ROUTE =====
@auth_bp.route('/register-voter', methods=['GET', 'POST'])
def register_voter():
    """
    Handle voter registration
    Voters fill in their details and submit for admin approval
    """
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('password_confirm', '').strip()
            date_of_birth = request.form.get('date_of_birth', '').strip()
            father_name = request.form.get('father_name', '').strip()
            phone_number = request.form.get('phone_number', '').strip()
            aadhaar_number = request.form.get('aadhaar_number', '').strip()
            occupation = request.form.get('occupation', '').strip()
            
            # Validate all required fields
            if not all([name, email, password, date_of_birth, father_name, 
                       phone_number, aadhaar_number, occupation]):
                flash('All fields are required', 'error')
                return redirect(url_for('auth.register_voter'))
            
            # Validate email format
            if not validate_email(email):
                flash('Invalid email format', 'error')
                return redirect(url_for('auth.register_voter'))
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('auth.register_voter'))
            
            # Validate password match
            if password != password_confirm:
                flash('Passwords do not match', 'error')
                return redirect(url_for('auth.register_voter'))
            
            # Validate password strength
            is_valid, message = validate_password(password)
            if not is_valid:
                flash(message, 'error')
                return redirect(url_for('auth.register_voter'))
            
            # Validate Aadhaar format
            if not validate_aadhaar(aadhaar_number):
                flash('Aadhaar must be 12 digits', 'error')
                return redirect(url_for('auth.register_voter'))
            
            # Check if Aadhaar already registered
            if Voter.query.filter_by(aadhaar_number=aadhaar_number).first():
                flash('Aadhaar number already registered', 'error')
                return redirect(url_for('auth.register_voter'))
            
            # Validate phone number
            if not validate_phone_number(phone_number):
                flash('Phone number must be 10 digits', 'error')
                return redirect(url_for('auth.register_voter'))
            
            # Handle profile image upload
            profile_image = 'default.jpg'
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to make it unique
                    filename = f"{datetime.now().timestamp()}_{filename}"
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    profile_image = filename
            
            # Create new user
            new_user = User(
                email=email,
                name=name,
                role='voter',
                password=generate_password_hash(password),
                profile_image=profile_image,
                is_verified=False,
                created_at=datetime.now()
            )
            
            db.session.add(new_user)
            db.session.flush()  # Get the user ID without committing
            
            # Create voter record
            new_voter = Voter(
                user_id=new_user.id,
                date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date(),
                father_name=father_name,
                phone_number=phone_number,
                aadhaar_number=aadhaar_number,
                occupation=occupation,
                status='pending',
                is_approved=False
            )
            
            db.session.add(new_voter)
            db.session.commit()
            
            flash('Registration successful! Please wait for admin approval.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'error')
            return redirect(url_for('auth.register_voter'))
    
    # Show voter registration form (GET request)
    return render_template('auth/register_voter.html')

# ===== CANDIDATE REGISTRATION ROUTE =====
@auth_bp.route('/register-candidate', methods=['GET', 'POST'])
def register_candidate():
    """
    Handle candidate registration
    Candidates register to contest in the election
    """
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('password_confirm', '').strip()
            party_name = request.form.get('party_name', '').strip()
            date_of_birth = request.form.get('date_of_birth', '').strip()
            phone_number = request.form.get('phone_number', '').strip()
            aadhaar_number = request.form.get('aadhaar_number', '').strip()
            
            # Validate all required fields
            if not all([name, email, password, party_name, date_of_birth, 
                       phone_number, aadhaar_number]):
                flash('All fields are required', 'error')
                return redirect(url_for('auth.register_candidate'))
            
            # Validate email format
            if not validate_email(email):
                flash('Invalid email format', 'error')
                return redirect(url_for('auth.register_candidate'))
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('auth.register_candidate'))
            
            # Validate password match
            if password != password_confirm:
                flash('Passwords do not match', 'error')
                return redirect(url_for('auth.register_candidate'))
            
            # Validate password strength
            is_valid, message = validate_password(password)
            if not is_valid:
                flash(message, 'error')
                return redirect(url_for('auth.register_candidate'))
            
            # Validate Aadhaar
            if not validate_aadhaar(aadhaar_number):
                flash('Aadhaar must be 12 digits', 'error')
                return redirect(url_for('auth.register_candidate'))
            
            # Validate phone number
            if not validate_phone_number(phone_number):
                flash('Phone number must be 10 digits', 'error')
                return redirect(url_for('auth.register_candidate'))
            
            # Handle profile image
            profile_image = 'default.jpg'
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    filename = f"{datetime.now().timestamp()}_{filename}"
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    profile_image = filename
            
            # Create new user
            new_user = User(
                email=email,
                name=name,
                role='candidate',
                password=generate_password_hash(password),
                profile_image=profile_image,
                is_verified=False,
                created_at=datetime.now()
            )
            
            db.session.add(new_user)
            db.session.flush()
            
            # Create candidate record
            new_candidate = Candidate(
                user_id=new_user.id,
                party_name=party_name,
                nomination_status='pending',
                is_approved=False
            )
            
            db.session.add(new_candidate)
            db.session.commit()
            
            flash('Candidate registration submitted! Wait for admin approval.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'error')
            return redirect(url_for('auth.register_candidate'))
    
    # Show candidate registration form (GET request)
    return render_template('auth/register_candidate.html')
