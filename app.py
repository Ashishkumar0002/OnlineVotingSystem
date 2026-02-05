# ========================================
# ONLINE VOTING SYSTEM - FLASK APPLICATION
# ========================================
# This is the main Flask application file
# It sets up the web server and initializes all routes and database

import sys
import os
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash

# Suppress Flask and Werkzeug warnings
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Import Flask after suppressing warnings
from flask import Flask, render_template, session

# Import database instance
from models import db

# Create Flask application instance
app = Flask(__name__)

# Get absolute path to application directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Set Flask configuration
# Use forward slashes for SQLite URI (convert backslashes on Windows)
db_path = os.path.join(APP_DIR, "voting_system.db").replace("\\", "/")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'voting-system-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = os.path.join(APP_DIR, 'static/uploads')

# Initialize database with Flask app
db.init_app(app)

# Context processor to inject logged-in user into templates
@app.context_processor
def inject_user():
    """Make logged-in user available in all templates"""
    user = None
    if 'user_id' in session:
        from models.user import User
        user = User.query.get(session['user_id'])
    return {'logged_in_user': user}

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors (page not found)"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors (server errors)"""
    db.session.rollback()
    return render_template('500.html'), 500

# Register blueprints (must happen before database initialization)
from routes.auth import auth_bp
from routes.main import main_bp
from routes.admin import admin_bp
from routes.voter import voter_bp
from routes.candidate import candidate_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(voter_bp)
app.register_blueprint(candidate_bp)

# Initialize database and create tables
def init_app():
    """Initialize the application - creates database tables and default admin"""
    with app.app_context():
        # Import models
        from models.user import User
        from models.voter import Voter
        from models.candidate import Candidate
        from models.vote import Vote
        from models.otp_log import OtpLog
        from models.voting_log import VotingLog
        
        # Create all database tables
        db.create_all()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(email='admin@voting.com').first():
            admin = User(
                email='admin@voting.com',
                name='System Admin',
                role='admin',
                password=generate_password_hash('Admin@123'),
                is_verified=True,
                created_at=datetime.now()
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created")

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on app startup
try:
    init_app()
except Exception as e:
    print(f"Warning during app initialization: {e}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
