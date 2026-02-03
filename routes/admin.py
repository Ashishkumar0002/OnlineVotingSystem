# ========================================
# ADMIN ROUTES - Admin dashboard and functions
# ========================================
# This file contains all admin dashboard routes
# Approve voters/candidates, view statistics, manage election

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime
from models import db
from models.user import User
from models.voter import Voter
from models.candidate import Candidate
from models.vote import Vote
from models.voting_log import VotingLog
from werkzeug.security import generate_password_hash

# Create a blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ===== LOGIN REQUIRED DECORATOR =====
def login_required(f):
    """
    Decorator to check if user is logged in and is admin
    Use this on routes that need authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user_id is in session
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is admin
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Access denied. Admin only.', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

# ===== ADMIN DASHBOARD ROUTE =====
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Show comprehensive admin dashboard with all features
    Display statistics, pending voters, pending candidates, active candidates, voting logs
    """
    # Count statistics
    total_voters = Voter.query.count()
    approved_voters = Voter.query.filter_by(is_approved=True).count()
    pending_voter_count = Voter.query.filter_by(status='pending').count()
    rejected_voter_count = Voter.query.filter_by(status='rejected').count()
    total_candidates = Candidate.query.count()
    approved_candidates = Candidate.query.filter_by(is_approved=True).count()
    total_votes = Vote.query.count()
    
    # Get pending voters with user details
    pending_voters = []
    voters = Voter.query.filter_by(status='pending').all()
    for voter in voters:
        user = User.query.get(voter.user_id)
        pending_voters.append({
            'id': voter.id,
            'name': user.name,
            'email': user.email,
            'phone': voter.phone_number,
            'aadhaar': voter.aadhaar_number,
            'occupation': voter.occupation,
            'applied_on': voter.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Get pending candidates with user details
    pending_candidates = []
    candidates = Candidate.query.filter(Candidate.nomination_status.in_(['pending', 'rejected'])).all()
    for candidate in candidates:
        user = User.query.get(candidate.user_id)
        pending_candidates.append({
            'id': candidate.id,
            'name': user.name,
            'email': user.email,
            'party': candidate.party_name,
            'status': candidate.nomination_status,
            'applied_on': candidate.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Get active/approved candidates
    active_candidates = []
    candidates = Candidate.query.filter_by(is_approved=True).all()
    for candidate in candidates:
        user = User.query.get(candidate.user_id)
        votes = Vote.query.filter_by(candidate_id=candidate.id).count()
        active_candidates.append({
            'id': candidate.id,
            'name': user.name,
            'party': candidate.party_name,
            'votes': votes
        })
    
    # Get voting logs
    voting_logs = []
    logs = VotingLog.query.order_by(VotingLog.created_at.desc()).limit(50).all()
    for log in logs:
        voting_logs.append({
            'voter_id': log.voter_id,
            'action': log.action,
            'timestamp': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ip': log.ip_address
        })
    
    return render_template('admin/dashboard.html',
                         total_voters=total_voters,
                         approved_voters=approved_voters,
                         pending_voter_count=pending_voter_count,
                         rejected_voter_count=rejected_voter_count,
                         total_candidates=total_candidates,
                         approved_candidates=approved_candidates,
                         total_votes=total_votes,
                         pending_voters=pending_voters,
                         pending_candidates=pending_candidates,
                         active_candidates=active_candidates,
                         voting_logs=voting_logs)

# ===== PENDING VOTER REGISTRATIONS =====
@admin_bp.route('/voters/pending')
@login_required
def pending_voters():
    """
    Show all voters waiting for approval
    Admin can approve or reject them
    """
    # Get voters with pending status
    voters = Voter.query.filter_by(status='pending').all()
    
    # Convert to list with user details
    voter_list = []
    for voter in voters:
        user = User.query.get(voter.user_id)
        voter_list.append({
            'id': voter.id,
            'name': user.name,
            'email': user.email,
            'phone': voter.phone_number,
            'aadhaar': voter.aadhaar_number,
            'occupation': voter.occupation,
            'applied_on': voter.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Get counts for stats
    total_pending = len(voter_list)
    total_approved = Voter.query.filter_by(is_approved=True).count()
    total_rejected = Voter.query.filter_by(status='rejected').count()
    
    return render_template('admin/pending_voters.html', 
                         pending_voters=voter_list,
                         approved_voters=total_approved,
                         rejected_voters=[])

# ===== APPROVE VOTER ROUTE =====
@admin_bp.route('/voter/<int:voter_id>/approve', methods=['POST'])
@login_required
def approve_voter(voter_id):
    """
    Approve a voter registration
    After approval, voter can login and vote
    """
    try:
        # Find the voter
        voter = Voter.query.get(voter_id)
        if not voter:
            return jsonify({'success': False, 'message': 'Voter not found'})
        
        # Generate unique voter ID
        from utils.helpers import generate_voter_id
        voter.voter_id = generate_voter_id()
        voter.status = 'approved'
        voter.is_approved = True
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Voter approved with ID: {voter.voter_id}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ===== REJECT VOTER ROUTE =====
@admin_bp.route('/voter/<int:voter_id>/reject', methods=['POST'])
@login_required
def reject_voter(voter_id):
    """
    Reject a voter registration
    Voter can re-apply if needed
    """
    try:
        voter = Voter.query.get(voter_id)
        if not voter:
            return jsonify({'success': False, 'message': 'Voter not found'})
        
        voter.status = 'rejected'
        voter.is_approved = False
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Voter registration rejected'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ===== PENDING CANDIDATES =====
@admin_bp.route('/candidates/pending')
@login_required
def pending_candidates():
    """
    Show all candidates waiting for approval
    Admin can approve or reject nominations
    """
    candidates = Candidate.query.filter(Candidate.nomination_status.in_(['pending', 'rejected'])).all()
    
    candidate_list = []
    for candidate in candidates:
        user = User.query.get(candidate.user_id)
        candidate_list.append({
            'id': candidate.id,
            'name': user.name,
            'email': user.email,
            'party': candidate.party_name,
            'status': candidate.nomination_status,
            'applied_on': candidate.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Get approved/active candidates
    active_candidates = Candidate.query.filter_by(is_approved=True).all()
    active_candidate_list = []
    for candidate in active_candidates:
        user = User.query.get(candidate.user_id)
        votes = Vote.query.filter_by(candidate_id=candidate.id).count()
        active_candidate_list.append({
            'id': candidate.id,
            'name': user.name,
            'party': candidate.party_name,
            'votes': votes
        })
    
    # Get counts for stats
    total_pending = len(candidate_list)
    total_approved = len(active_candidate_list)
    
    return render_template('admin/pending_candidates.html', 
                         pending_candidates=candidate_list,
                         approved_candidates=total_approved,
                         rejected_candidates=[],
                         active_candidates=active_candidate_list)

# ===== APPROVE CANDIDATE =====
@admin_bp.route('/candidate/<int:candidate_id>/approve', methods=['POST'])
@login_required
def approve_candidate(candidate_id):
    """
    Approve a candidate nomination
    After approval, candidate can view votes and election results
    """
    try:
        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            return jsonify({'success': False, 'message': 'Candidate not found'})
        
        candidate.nomination_status = 'approved'
        candidate.is_approved = True
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Candidate approved'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ===== REJECT CANDIDATE =====
@admin_bp.route('/candidate/<int:candidate_id>/reject', methods=['POST'])
@login_required
def reject_candidate(candidate_id):
    """
    Reject a candidate nomination
    Candidate can reapply later
    """
    try:
        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            return jsonify({'success': False, 'message': 'Candidate not found'})
        
        candidate.nomination_status = 'rejected'
        candidate.is_approved = False
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Candidate rejected'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ===== REMOVE CANDIDATE =====
@admin_bp.route('/candidate/<int:candidate_id>/remove', methods=['POST'])
@login_required
def remove_candidate(candidate_id):
    """
    Remove a candidate from election
    Also removes votes cast for this candidate
    """
    try:
        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            return jsonify({'success': False, 'message': 'Candidate not found'})
        
        # Remove votes for this candidate
        Vote.query.filter_by(candidate_id=candidate_id).delete()
        
        # Delete candidate
        db.session.delete(candidate)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Candidate removed from election'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ===== VOTING LOGS =====
@admin_bp.route('/voting-logs')
@login_required
def voting_logs():
    """
    Show all voting activity logs
    For audit and verification purposes
    """
    # Get voting logs (limit to recent 100)
    logs = VotingLog.query.order_by(VotingLog.created_at.desc()).limit(100).all()
    
    log_list = []
    for log in logs:
        log_list.append({
            'voter_id': log.voter_id,
            'action': log.action,
            'timestamp': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ip': log.ip_address
        })
    
    return render_template('admin/voting_logs.html', logs=log_list)

# ===== RESET ELECTION =====
@admin_bp.route('/election/reset', methods=['POST'])
@login_required
def reset_election():
    """
    Reset the election (delete all votes)
    WARNING: This action cannot be undone!
    """
    try:
        # Delete all votes
        Vote.query.delete()
        
        # Reset voter voted status
        voters = Voter.query.all()
        for voter in voters:
            voter.has_voted = False
            voter.voted_at = None
        
        # Reset candidate vote counts
        candidates = Candidate.query.all()
        for candidate in candidates:
            candidate.total_votes = 0
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Election has been reset'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ===== CHANGE PASSWORD =====
@admin_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Allow admin to change their password
    """
    if request.method == 'POST':
        try:
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Get logged in user
            user = User.query.get(session['user_id'])
            
            # Check old password
            from werkzeug.security import check_password_hash
            if not check_password_hash(user.password, old_password):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('admin.change_password'))
            
            # Check if passwords match
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('admin.change_password'))
            
            # Update password
            user.password = generate_password_hash(new_password)
            db.session.commit()
            
            flash('Password changed successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('admin.change_password'))
    
    return render_template('admin/change_password.html')
