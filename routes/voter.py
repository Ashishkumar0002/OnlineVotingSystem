# ========================================
# VOTER ROUTES - Voter dashboard and voting
# ========================================
# This file contains voter dashboard and voting functionality

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime, timedelta
from models import db
from models.user import User
from models.voter import Voter
from models.candidate import Candidate
from models.vote import Vote
from models.otp_log import OtpLog
from models.voting_log import VotingLog
from utils.helpers import generate_otp, get_otp_expiry_time
import random
import string

# Create a blueprint for voter routes
voter_bp = Blueprint('voter', __name__, url_prefix='/voter')

# ===== LOGIN REQUIRED DECORATOR =====
def voter_login_required(f):
    """
    Decorator to check if user is logged in and is a voter
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'voter':
            flash('Access denied. Voters only.', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

# ===== VOTER DASHBOARD =====
@voter_bp.route('/dashboard')
@voter_login_required
def dashboard():
    """
    Show voter dashboard
    Display voter information and voting status
    """
    # Get voter information
    user = User.query.get(session['user_id'])
    voter = Voter.query.filter_by(user_id=user.id).first()
    
    if not voter:
        flash('Voter profile not found', 'error')
        return redirect(url_for('auth.login'))
    
    # Check if voter is approved
    if not voter.is_approved:
        return render_template('voter/pending_approval.html', voter=voter)
    
    # Get total candidates
    total_candidates = Candidate.query.filter_by(is_approved=True).count()
    
    # Check if voter has already voted
    has_voted = voter.has_voted
    
    return render_template('voter/dashboard.html',
                         voter=voter,
                         user=user,
                         has_voted=has_voted,
                         total_candidates=total_candidates)

# ===== VOTING PAGE - STEP 1: ENTER VOTER ID =====
@voter_bp.route('/vote', methods=['GET', 'POST'])
def vote_step1():
    """
    Step 1 of voting process
    Voter enters their Voter ID or Email
    """
    if request.method == 'POST':
        # Get voter ID or email
        identifier = request.form.get('identifier', '').strip()
        
        if not identifier:
            flash('Please enter Voter ID or Email', 'error')
            return redirect(url_for('voter.vote_step1'))
        
        # Find voter by ID or Email
        voter = None
        if identifier.startswith('VOTER_'):
            # Search by Voter ID
            voter = Voter.query.filter_by(voter_id=identifier).first()
        else:
            # Search by Email
            user = User.query.filter_by(email=identifier, role='voter').first()
            if user:
                voter = Voter.query.filter_by(user_id=user.id).first()
        
        if not voter:
            flash('Voter ID or Email not found', 'error')
            return redirect(url_for('voter.vote_step1'))
        
        if not voter.is_approved:
            flash('Your registration is not approved yet', 'error')
            return redirect(url_for('voter.vote_step1'))
        
        if voter.has_voted:
            flash('You have already voted', 'error')
            return redirect(url_for('voter.vote_step1'))
        
        # Store voter ID in session for next steps
        session['voting_voter_id'] = voter.id
        session['voting_email'] = identifier if '@' in identifier else voter.user_id
        
        return redirect(url_for('voter.vote_step2'))
    
    return render_template('voter/vote_step1.html')

# ===== VOTING PAGE - STEP 2: OTP VERIFICATION =====
@voter_bp.route('/vote/otp', methods=['GET', 'POST'])
def vote_step2():
    """
    Step 2 of voting process
    Generate and verify OTP
    """
    if 'voting_voter_id' not in session:
        flash('Please start voting process from the beginning', 'error')
        return redirect(url_for('voter.vote_step1'))
    
    voter_id = session['voting_voter_id']
    voter = Voter.query.get(voter_id)
    
    if request.method == 'POST':
        # Get OTP from form
        entered_otp = request.form.get('otp', '').strip()
        
        # Get the latest OTP for this voter
        latest_otp = OtpLog.query.filter_by(
            voter_id=voter_id,
            is_verified=False
        ).order_by(OtpLog.created_at.desc()).first()
        
        if not latest_otp:
            flash('No OTP generated. Please try again', 'error')
            return redirect(url_for('voter.vote_step2'))
        
        # Check if OTP is expired
        if latest_otp.is_expired():
            flash('OTP has expired. Please generate a new one', 'error')
            return redirect(url_for('voter.vote_step2'))
        
        # Check if OTP matches
        if entered_otp != latest_otp.otp_code:
            flash('OTP is incorrect', 'error')
            return redirect(url_for('voter.vote_step2'))
        
        # Mark OTP as verified
        latest_otp.is_verified = True
        db.session.commit()
        
        # Move to step 3
        return redirect(url_for('voter.vote_step3'))
    
    # Generate OTP on first visit
    if request.method == 'GET':
        # Check if there's already a valid OTP
        valid_otp = OtpLog.query.filter_by(
            voter_id=voter_id,
            is_verified=False
        ).filter(OtpLog.expires_at > datetime.now()).first()
        
        if not valid_otp:
            # Generate new OTP
            otp_code = generate_otp()
            expiry_time = get_otp_expiry_time(minutes=10)
            
            new_otp = OtpLog(
                voter_id=voter_id,
                otp_code=otp_code,
                is_verified=False,
                created_at=datetime.now(),
                expires_at=expiry_time
            )
            db.session.add(new_otp)
            db.session.commit()
            
            # Store OTP for display (in real app, send via SMS/Email)
            session['demo_otp'] = otp_code
        else:
            session['demo_otp'] = valid_otp.otp_code
    
    return render_template('voter/vote_step2.html',
                         voter=voter,
                         demo_otp=session.get('demo_otp'))

# ===== VOTING PAGE - STEP 3: CAST VOTE =====
@voter_bp.route('/vote/cast', methods=['GET', 'POST'])
def vote_step3():
    """
    Step 3 of voting process
    Cast vote for a candidate
    """
    if 'voting_voter_id' not in session:
        flash('Please complete OTP verification first', 'error')
        return redirect(url_for('voter.vote_step1'))
    
    voter_id = session['voting_voter_id']
    voter = Voter.query.get(voter_id)
    
    if request.method == 'POST':
        # Get selected candidate
        candidate_id = request.form.get('candidate_id')
        
        if not candidate_id:
            flash('Please select a candidate', 'error')
            return redirect(url_for('voter.vote_step3'))
        
        try:
            candidate_id = int(candidate_id)
            candidate = Candidate.query.get(candidate_id)
            
            if not candidate or not candidate.is_approved:
                flash('Invalid candidate selected', 'error')
                return redirect(url_for('voter.vote_step3'))
            
            # Create vote record
            new_vote = Vote(
                voter_id=voter_id,
                candidate_id=candidate_id,
                voted_at=datetime.now()
            )
            
            # Update voter status
            voter.has_voted = True
            voter.voted_at = datetime.now()
            
            # Update candidate vote count
            candidate.total_votes += 1
            
            # Create voting log
            voting_log = VotingLog(
                voter_id=voter_id,
                action='vote_cast',
                details=f'Voted for candidate {candidate_id}',
                ip_address=request.remote_addr,
                created_at=datetime.now()
            )
            
            db.session.add(new_vote)
            db.session.add(voting_log)
            db.session.commit()
            
            # Clear session
            session.pop('voting_voter_id', None)
            session.pop('demo_otp', None)
            
            # Go to thank you page
            return redirect(url_for('voter.vote_success'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error casting vote: {str(e)}', 'error')
            return redirect(url_for('voter.vote_step3'))
    
    # Get all approved candidates
    candidates = Candidate.query.filter_by(is_approved=True).all()
    
    candidate_list = []
    for candidate in candidates:
        user = User.query.get(candidate.user_id)
        candidate_list.append({
            'id': candidate.id,
            'name': user.name,
            'party': candidate.party_name,
            'image': user.profile_image
        })
    
    return render_template('voter/vote_step3.html', candidates=candidate_list)

# ===== VOTING SUCCESS PAGE =====
@voter_bp.route('/vote/success')
def vote_success():
    """
    Thank you page after successful voting
    """
    return render_template('voter/vote_success.html')

# ===== VIEW RESULTS =====
@voter_bp.route('/results')
@voter_login_required
def results():
    """
    Show election results to voter
    """
    # Get all approved candidates with their vote counts
    candidates = db.session.query(Candidate, User).join(
        User, Candidate.user_id == User.id
    ).filter(Candidate.is_approved == True).all()
    
    candidate_results = []
    for candidate, user in candidates:
        vote_count = Vote.query.filter_by(candidate_id=candidate.id).count()
        candidate_results.append({
            'id': candidate.id,
            'name': user.name,
            'party': candidate.party_name,
            'votes': vote_count,
            'image': user.profile_image
        })
    
    # Sort by votes
    candidate_results.sort(key=lambda x: x['votes'], reverse=True)
    
    total_votes = sum(c['votes'] for c in candidate_results)
    
    return render_template('voter/results.html',
                         candidates=candidate_results,
                         total_votes=total_votes)
