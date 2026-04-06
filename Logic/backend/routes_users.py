"""
ArmsDealer — Users Blueprint
Routes: /api/auth/* and /api/users/*
"""
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_db
from .auth import login_required, role_required, get_current_user

users_bp = Blueprint('users', __name__)


# ── REGISTER ──────────────────────────────────────────────────────────────────
@users_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    required = ['username', 'email', 'password']
    for field in required:
        if not data.get(field, '').strip():
            return jsonify({'error': f'Field "{field}" is required'}), 400

    db = get_db()
    try:
        db.execute(
            """INSERT INTO users (username, email, password_hash, first_name, last_name, phone)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (data['username'].strip(),
             data['email'].strip().lower(),
             generate_password_hash(data['password']),
             data.get('first_name', '').strip(),
             data.get('last_name', '').strip(),
             data.get('phone', '').strip())
        )
        db.commit()
        return jsonify({'message': 'Account created successfully'}), 201
    except Exception as e:
        db.rollback()
        if 'UNIQUE' in str(e):
            return jsonify({'error': 'Username or email already exists'}), 409
        return jsonify({'error': 'Registration failed'}), 500
    finally:
        db.close()


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@users_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()   # username OR email
    password   = data.get('password', '')

    if not identifier or not password:
        return jsonify({'error': 'Identifier and password required'}), 400

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE (username = ? OR email = ?) AND is_active = 1",
        (identifier, identifier)
    ).fetchone()
    db.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['user_id']   = user['id']
    session['user_type'] = user['user_type']
    session.permanent    = True

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id':        user['id'],
            'username':  user['username'],
            'email':     user['email'],
            'user_type': user['user_type'],
            'first_name': user['first_name'],
            'last_name':  user['last_name'],
        }
    })


# ── LOGOUT ────────────────────────────────────────────────────────────────────
@users_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


# ── CURRENT USER ──────────────────────────────────────────────────────────────
@users_bp.route('/api/auth/me', methods=['GET'])
@login_required
def me():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(dict(user))


# ── UPDATE PROFILE ────────────────────────────────────────────────────────────
@users_bp.route('/api/auth/me', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json() or {}
    allowed = ['first_name', 'last_name', 'phone', 'address']
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400

    set_clause = ', '.join(f"{k} = ?" for k in updates)
    values     = list(updates.values()) + [session['user_id']]

    db = get_db()
    db.execute(
        f"UPDATE users SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
        values
    )
    db.commit()
    db.close()
    return jsonify({'message': 'Profile updated'})


# ── CHANGE PASSWORD ───────────────────────────────────────────────────────────
@users_bp.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json() or {}
    old_pw = data.get('old_password', '')
    new_pw = data.get('new_password', '')

    if not old_pw or not new_pw:
        return jsonify({'error': 'Both old and new passwords required'}), 400
    if len(new_pw) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400

    db = get_db()
    user = db.execute("SELECT password_hash FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if not user or not check_password_hash(user['password_hash'], old_pw):
        db.close()
        return jsonify({'error': 'Current password is incorrect'}), 401

    db.execute(
        "UPDATE users SET password_hash = ?, updated_at = datetime('now') WHERE id = ?",
        (generate_password_hash(new_pw), session['user_id'])
    )
    db.commit()
    db.close()
    return jsonify({'message': 'Password changed successfully'})


# ── ADMIN: LIST ALL USERS ─────────────────────────────────────────────────────
@users_bp.route('/api/users', methods=['GET'])
@role_required('admin', 'developer')
def list_users():
    db = get_db()
    users = db.execute(
        "SELECT id, username, email, user_type, first_name, last_name, "
        "is_active, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    db.close()
    return jsonify([dict(u) for u in users])


# ── ADMIN: UPDATE USER TYPE ───────────────────────────────────────────────────
@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    data = request.get_json() or {}
    allowed = ['user_type', 'is_active']
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return jsonify({'error': 'No valid fields'}), 400

    db = get_db()
    set_clause = ', '.join(f"{k} = ?" for k in updates)
    db.execute(
        f"UPDATE users SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
        list(updates.values()) + [user_id]
    )
    db.commit()
    db.close()
    return jsonify({'message': 'User updated'})
