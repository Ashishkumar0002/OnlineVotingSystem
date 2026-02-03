# ========================================
# MAIN ROUTES - Public pages
# ========================================
# This file contains routes for public pages
# Home, About Us, Results

from flask import Blueprint, render_template
from models.vote import Vote
from models.candidate import Candidate
from models.user import User
from models import db

# Create a blueprint for main routes
main_bp = Blueprint('main', __name__)

# ===== HOME PAGE ROUTE =====
@main_bp.route('/')
def index():
    """
    Show the home/main page
    This page is accessible to everyone
    Includes awareness slider and information about voting
    """
    return render_template('main/index.html')

# ===== RESULTS PAGE ROUTE =====
@main_bp.route('/results')
def results():
    """
    Show election results
    Display all candidates and their vote counts
    """
    # Get all approved candidates with their vote counts
    candidates = db.session.query(Candidate, User).join(
        User, Candidate.user_id == User.id
    ).filter(Candidate.is_approved == True).all()
    
    # Convert to list of dictionaries for easier template use
    candidate_results = []
    for candidate, user in candidates:
        # Count votes for this candidate
        vote_count = Vote.query.filter_by(candidate_id=candidate.id).count()
        
        candidate_results.append({
            'id': candidate.id,
            'name': user.name,
            'party': candidate.party_name,
            'votes': vote_count,
            'image': user.profile_image
        })
    
    # Sort by votes in descending order (highest first)
    candidate_results.sort(key=lambda x: x['votes'], reverse=True)
    
    # Calculate total votes
    total_votes = sum(c['votes'] for c in candidate_results)
    
    return render_template('main/results.html', candidates=candidate_results, total_votes=total_votes)

# ===== ABOUT US PAGE ROUTE =====
@main_bp.route('/about')
def about():
    """
    Show About Us page
    Information about the online voting system
    """
    return render_template('main/about.html')


