# ==========================================
# STARTUP WRAPPER - Fixes Python 3.14 compatibility
# ==========================================
# This file works around SQLAlchemy compatibility issues with Python 3.14

import sys
import os
import logging

# CRITICAL: Patch typing BEFORE any imports, at the very beginning
# This only applies to Python 3.14+
if sys.version_info >= (3, 14):
    import typing
    
    # Only create TypingOnly if it doesn't already exist
    if not hasattr(typing, 'TypingOnly'):
        class TypingOnly:
            pass
        typing.TypingOnly = TypingOnly

# Suppress Flask and Werkzeug warnings
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the Flask app
if __name__ == '__main__':
    try:
        print("\nImporting app...")
        from app import app, init_app
        
        print("="*50)
        print("ONLINE VOTING SYSTEM - STARTING")
        print("="*50)
        print(f"Python Version: {sys.version.split()[0]}")
        print(f"Flask Starting on: http://localhost:5000")
        print("="*50)
        
        print("\nInitializing database...")
        init_app()
        
        print("\n✓ Starting Flask server on 0.0.0.0:5000")
        print("Dashboard: http://localhost:5000/admin")
        print("Press Ctrl+C to stop server\n")
        
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
