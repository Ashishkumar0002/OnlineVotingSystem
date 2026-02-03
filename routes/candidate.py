# ========================================
# CANDIDATE ROUTES - Candidate dashboard
# ========================================
# This file contains candidate dashboard routes

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime
from models import db
from models.user import User
from models.candidate import Candidate
from models.vote import Vote

# Create a blueprint for candidate routes
candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

# ===== LOGIN REQUIRED DECORATOR =====
def candidate_login_required(f):
    """
    Decorator to check if user is logged in and is a candidate
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'candidate':
            flash('Access denied. Candidates only.', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

# ===== CANDIDATE DASHBOARD =====
@candidate_bp.route('/dashboard')
@candidate_login_required
def dashboard():
    """
    Show candidate dashboard
    Display vote count and nomination status
    """
    # Get logged in user
    user = User.query.get(session['user_id'])
    
    # Get candidate record
    candidate = Candidate.query.filter_by(user_id=user.id).first()
    
    if not candidate:
        flash('Candidate profile not found', 'error')
        return redirect(url_for('auth.login'))
    
    # Check if nomination is approved
    if not candidate.is_approved:
        return render_template('candidate/pending_approval.html', candidate=candidate)
    
    # Get vote count for this candidate
    total_votes = Vote.query.filter_by(candidate_id=candidate.id).count()
    
    # Get all votes for this candidate with voter count
    total_voters = db.session.query(Vote).filter_by(candidate_id=candidate.id).count()
    
    return render_template('candidate/dashboard.html',
                         candidate=candidate,
                         user=user,
                         total_votes=total_votes)

# ===== SUBMIT/UPDATE NOMINATION =====
@candidate_bp.route('/submit-nomination', methods=['GET', 'POST'])
@candidate_login_required
def submit_nomination():
    """
    Submit or update candidate nomination
    """
    user = User.query.get(session['user_id'])
    candidate = Candidate.query.filter_by(user_id=user.id).first()
    
    if request.method == 'POST':
        try:
            party_name = request.form.get('party_name', '').strip()
            
            if not party_name:
                flash('Party name is required', 'error')
                return redirect(url_for('candidate.submit_nomination'))
            
            if not candidate:
                # Create new candidate nomination
                candidate = Candidate(
                    user_id=user.id,
                    party_name=party_name,
                    nomination_status='pending',
                    is_approved=False
                )
                db.session.add(candidate)
            else:
                # Update existing nomination
                candidate.party_name = party_name
                candidate.nomination_status = 'pending'
                candidate.is_approved = False
            
            db.session.commit()
            flash('Nomination submitted for admin approval', 'success')
            return redirect(url_for('candidate.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting nomination: {str(e)}', 'error')
            return redirect(url_for('candidate.submit_nomination'))
    
    # Show form with existing party name if available
    party_name = candidate.party_name if candidate else ''
    
    return render_template('candidate/submit_nomination.html',
                         candidate=candidate,
                         party_name=party_name)

# ===== CANCEL NOMINATION =====
@candidate_bp.route('/cancel-nomination', methods=['POST'])
@candidate_login_required
def cancel_nomination():
    """
    Cancel candidate nomination
    """
    try:
        user = User.query.get(session['user_id'])
        candidate = Candidate.query.filter_by(user_id=user.id).first()
        
        if not candidate:
            return jsonify({'success': False, 'message': 'Nomination not found'})
        
        if candidate.is_approved:
            return jsonify({'success': False, 'message': 'Cannot cancel approved nomination'})
        
        # Delete the nomination
        db.session.delete(candidate)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Nomination cancelled'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ===== VIEW RESULTS =====
@candidate_bp.route('/results')
@candidate_login_required
def results():
    """
    Show election results to candidate
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
            'image': user.profile_image,
            'is_self': candidate.user_id == session['user_id']
        })
    
    # Sort by votes
    candidate_results.sort(key=lambda x: x['votes'], reverse=True)
    
    total_votes = sum(c['votes'] for c in candidate_results)
    
    return render_template('candidate/results.html',
                         candidates=candidate_results,
                         total_votes=total_votes)
