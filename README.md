# Online Voting System - Web Application

A modern, secure, and transparent online voting platform built with Flask, SQLite, and Bootstrap 5.

## Project Features

### Core Features
- **User Roles**: Admin, Voter, and Candidate
- **Secure Authentication**: Role-based login with password hashing
- **Voter Registration**: Complete registration with Aadhaar validation
- **Candidate Registration**: Nomination process with admin approval
- **Online Voting**: Secure voting with OTP verification
- **Election Management**: Admin dashboard for managing elections
- **Real-time Results**: Live election results with vote tracking

### Technical Features
- **Professional UI**: Card-based dashboard inspired by premium admin panels
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Security**: Input validation, password hashing, OTP verification
- **Database**: SQLite with proper relationships and constraints
- **Modular Architecture**: Organized folder structure with blueprints

## Technology Stack

### Frontend
- HTML5
- CSS3 (with custom styling)
- Bootstrap 5 (responsive framework)
- JavaScript (form validation and AJAX)
- Chart.js (data visualization)
- Font Awesome (icons)

### Backend
- Python 3.8+
- Flask (web framework)
- Flask-SQLAlchemy (ORM)
- Werkzeug (password hashing)

### Database
- SQLite 3

## Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- VS Code (recommended)

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

The application will start at: `http://localhost:5000`

## Project Structure

```
OnlineVotingSystem/
│
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
│
├── models/                   # Database models
│   ├── __init__.py
│   ├── user.py              # User model (Admin, Voter, Candidate)
│   ├── voter.py             # Voter-specific model
│   ├── candidate.py         # Candidate model
│   ├── vote.py              # Vote record model
│   ├── otp_log.py           # OTP tracking model
│   └── voting_log.py        # Voting activity log model
│
├── routes/                  # Route handlers (blueprints)
│   ├── __init__.py
│   ├── auth.py              # Login, registration routes
│   ├── main.py              # Public pages (home, results)
│   ├── admin.py             # Admin dashboard routes
│   ├── voter.py             # Voter dashboard and voting
│   └── candidate.py         # Candidate dashboard routes
│
├── utils/                   # Utility functions
│   └── helpers.py           # Validation, OTP generation, helpers
│
├── templates/               # HTML templates
│   ├── base.html            # Base template (navigation, layout)
│   ├── auth/                # Authentication pages
│   │   ├── login.html
│   │   ├── register_voter.html
│   │   └── register_candidate.html
│   ├── main/                # Public pages
│   │   ├── index.html       # Home page with slider
│   │   ├── about.html
│   │   ├── contact.html
│   │   └── results.html
│   ├── admin/               # Admin pages
│   │   ├── dashboard.html
│   │   ├── pending_voters.html
│   │   ├── pending_candidates.html
│   │   ├── voting_logs.html
│   │   └── change_password.html
│   ├── voter/               # Voter pages
│   │   ├── dashboard.html
│   │   ├── vote_step1.html
│   │   ├── vote_step2.html
│   │   ├── vote_step3.html
│   │   ├── vote_success.html
│   │   └── results.html
│   └── candidate/           # Candidate pages
│       ├── dashboard.html
│       ├── submit_nomination.html
│       └── results.html
│
├── static/                  # Static files
│   ├── css/
│   │   └── style.css        # Main stylesheet
│   ├── js/
│   │   └── main.js          # JavaScript utilities
│   ├── images/              # Image resources
│   └── uploads/             # User profile images
```

## User Roles & Workflows

### 1. Voter Workflow
1. Register as voter
2. Wait for admin approval
3. Receive voter ID
4. Login with credentials
5. Enter voter ID during voting
6. Verify identity with OTP
7. Cast vote for preferred candidate
8. View election results

### 2. Candidate Workflow
1. Register as candidate
2. Submit nomination
3. Wait for admin approval
4. View total votes received
5. View election results
6. Cancel nomination (if rejected)

### 3. Admin Workflow
1. Login as administrator
2. Review voter registrations
3. Approve/reject voters (generate voter IDs)
4. Review candidate nominations
5. Approve/reject candidates
6. Monitor voting process
7. View voting logs and statistics
8. Reset election if needed
9. Change admin password

## Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- name
- role (admin, voter, candidate)
- password (hashed)
- profile_image
- is_verified
- created_at, updated_at

### Voters Table
- id (Primary Key)
- user_id (Foreign Key → Users)
- voter_id (Unique, generated after approval)
- date_of_birth
- father_name
- phone_number
- aadhaar_number (Unique)
- occupation
- has_voted
- voted_at
- is_approved
- status (pending, approved, rejected)
- created_at, updated_at

### Candidates Table
- id (Primary Key)
- user_id (Foreign Key → Users)
- nomination_status
- is_approved
- party_name
- total_votes
- created_at, updated_at

### Votes Table
- id (Primary Key)
- voter_id (Foreign Key → Voters)
- candidate_id (Foreign Key → Candidates)
- voted_at

### OTP Logs Table
- id (Primary Key)
- voter_id (Foreign Key → Voters)
- otp_code
- is_verified
- created_at
- expires_at

### Voting Logs Table
- id (Primary Key)
- voter_id (Foreign Key → Voters)
- action
- details
- ip_address
- created_at

## Demo Login Credentials

### Administrator
- Email: `admin@voting.com`
- Password: `Admin@123`
- Role: Administrator

## Password Requirements

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character (!@#$%^&*()-_=+[]{}|;:,.<>?)

## Key Features Explained

### OTP Verification
- 6-digit OTP generated for voter verification
- OTP valid for 10 minutes
- Demo OTP displayed on page (for testing)
- Prevents unauthorized voting

### Voter ID Generation
- Format: `VOTER_YYYYMMDD_RANDOM4DIGITS`
- Example: `VOTER_20260127_3847`
- Generated after admin approval
- Unique for each voter

### Vote Security
- One vote per voter (enforced)
- Vote secrecy maintained
- Complete audit trail with voting logs
- No link between voter identity and vote

### Admin Controls
- Approve/reject voter registrations
- Approve/reject candidate nominations
- Remove candidates from election
- View voting statistics
- Reset election data
- Change admin password

## Security Measures

1. **Password Hashing**: Using Werkzeug security
2. **OTP Verification**: Two-factor authentication
3. **Aadhaar Validation**: Unique identity verification
4. **Input Validation**: Frontend and backend
5. **Session Management**: Secure session handling
6. **CSRF Protection**: Form validation
7. **SQL Injection Prevention**: Using ORM (SQLAlchemy)
8. **Vote Integrity**: One vote per voter enforcement

## Responsive Design

- **Desktop**: Full layout with sidebar navigation
- **Tablet**: Collapsible sidebar, optimized spacing
- **Mobile**: Touch-friendly buttons, stacked layout

## Color Scheme

- Primary Blue: `#4e73df`
- Success Green: `#1cc88a`
- Danger Red: `#e74c3c`
- Warning Yellow: `#f6c23e`
- Light Background: `#f8f9fc`
- Sidebar Blue: `#224abe`

## API Endpoints

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout
- `POST /register-voter` - Voter registration
- `POST /register-candidate` - Candidate registration

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/voters/pending` - Pending voter registrations
- `POST /admin/voter/<id>/approve` - Approve voter
- `POST /admin/voter/<id>/reject` - Reject voter
- `GET /admin/candidates/pending` - Pending candidate nominations
- `POST /admin/candidate/<id>/approve` - Approve candidate
- `POST /admin/candidate/<id>/reject` - Reject candidate

### Voter Routes
- `GET /voter/dashboard` - Voter dashboard
- `GET /voter/vote` - Start voting process
- `POST /voter/vote/otp` - OTP verification
- `POST /voter/vote/cast` - Cast vote

### Public Routes
- `GET /` - Home page
- `GET /results` - Election results
- `GET /about` - About us
- `GET /contact` - Contact us

## Troubleshooting

### Database Issues
```bash
# Delete existing database to start fresh
rm voting_system.db

# Run app to recreate database
python app.py
```

### Virtual Environment
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate
```

### Missing Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# Check installed packages
pip list
```

## Future Enhancements

1. Email integration for OTP and notifications
2. SMS integration for voter verification
3. Advanced analytics and reports
4. Export results to PDF/Excel
5. Two-factor authentication for admin
6. Biometric verification
7. Blockchain integration for audit trail
8. Multi-language support
9. Dark mode
10. Mobile app (React Native/Flutter)

## Contributing

This is an academic project. Contributions are welcome for:
- Bug fixes
- UI/UX improvements
- Documentation
- Performance optimization
- Security enhancements

## License

This project is created for educational purposes.

## Support

For issues or questions, please contact:
- Email: ashishkumar7807445804@gmail.com
- Phone: +91 7876626462

## Author

Online Voting System Development Team
2026

---

**Note**: This is a demonstration/academic project. For production use, additional security measures and compliance requirements must be implemented.

