# ========================================
# ONLINE VOTING SYSTEM - FLASK APPLICATION
# ========================================

import sys
import os
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash

# -------------------------------
# DEFINE APP BASE DIRECTORY FIRST
# -------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Suppress Flask and Werkzeug warnings
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Flask imports
from flask import Flask, render_template, session

# Database instance
from models import db

# Create Flask application instance
app = Flask(__name__)

# -------------------------------
# DATABASE CONFIGURATION
# -------------------------------

# Create instance directory for local DB
INSTANCE_DIR = os.path.join(APP_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

# Read DATABASE_URL from environment (Render PostgreSQL)
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # ✅ PRODUCTION (Render / PostgreSQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace(
        "postgres://", "postgresql://"
    )
else:
    # ✅ LOCAL DEVELOPMENT (SQLite)
    db_path = os.path.join(INSTANCE_DIR, "voting_system.db").replace("\\", "/")
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

# Other Flask configs
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'voting-system-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = os.path.join(APP_DIR, 'static/uploads')

# Initialize database with Flask app
db.init_app(app)

# -------------------------------
# CONTEXT PROCESSOR
# -------------------------------
@app.context_processor
def inject_user():
    """Make logged-in user available in all templates"""
    user = None
    if 'user_id' in session:
        from models.user import User
        user = User.query.get(session['user_id'])
    return {'logged_in_user': user}

# -------------------------------
# ERROR HANDLERS
# -------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

# -------------------------------
# REGISTER BLUEPRINTS
# -------------------------------
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

# -------------------------------
# INITIALIZE DATABASE
# -------------------------------
def init_app():
    """Create tables and default admin"""
    with app.app_context():
        from models.user import User
        from models.voter import Voter
        from models.candidate import Candidate
        from models.vote import Vote
        from models.otp_log import OtpLog
        from models.voting_log import VotingLog

        db.create_all()

        # Create default admin
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

# Run initialization
try:
    init_app()
except Exception as e:
    print(f"Warning during app initialization: {e}")

# -------------------------------
# RUN APPLICATION
# -------------------------------
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
