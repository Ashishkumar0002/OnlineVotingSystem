# ========================================
# DATABASE INITIALIZATION
# ========================================
# This file initializes the database for the application

import sys

# CRITICAL: Patch typing BEFORE any SQLAlchemy imports
if sys.version_info >= (3, 14):
    import typing
    if not hasattr(typing, 'TypingOnly'):
        class TypingOnly:
            # Don't restrict attributes - allow anything to be added
            pass
        typing.TypingOnly = TypingOnly

from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance without binding to app
# This allows models to import db without circular imports
db = SQLAlchemy()
