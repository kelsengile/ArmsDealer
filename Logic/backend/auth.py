"""
ArmsDealer — Authentication Utilities
Simple session-based auth (no JWT dependency)
"""
import functools
from flask import session, jsonify
from .database import get_db


def login_required(f):
    """Decorator: requires a logged-in session."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorator: requires the user to have one of the given roles."""
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            db = get_db()
            user = db.execute(
                "SELECT user_type FROM users WHERE id = ?", (session['user_id'],)
            ).fetchone()
            db.close()
            if not user or user['user_type'] not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def get_current_user():
    """Return the current user row or None."""
    if 'user_id' not in session:
        return None
    db = get_db()
    user = db.execute(
        "SELECT id, username, email, user_type, first_name, last_name, is_active "
        "FROM users WHERE id = ?", (session['user_id'],)
    ).fetchone()
    db.close()
    return user
