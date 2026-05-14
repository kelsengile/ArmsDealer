# ──────────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION ROUTES
# ──────────────────────────────────────────────────────────────────────────────────
import sqlite3
import os
import secrets
import datetime
import smtplib
from email.message import EmailMessage
from functools import wraps
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, g, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from db_helpers import get_db

auth_bp = Blueprint('auth', __name__)


def _send_otp_email(email, code, purpose='registration'):
    smtp_host = os.environ.get('SMTP_HOST')
    if not smtp_host:
        return False
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    smtp_from = os.environ.get('MAIL_FROM', 'no-reply@armsdealer.com')
    subject = 'Your ArmsDealer verification code'
    body = (
        f'Your ArmsDealer registration OTP is {code}.\n\n'
        'Enter this code on the registration page to complete your account setup.'
    )
    if purpose == 'reset':
        subject = 'Your ArmsDealer password reset code'
        body = (
            f'Your ArmsDealer password reset code is {code}.\n\n'
            'Enter this code on the reset page to update your password.'
        )
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = smtp_from
    msg['To'] = email
    msg.set_content(body)
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
            if os.environ.get('SMTP_USE_TLS', 'true').lower() != 'false':
                smtp.starttls()
            if smtp_user and smtp_pass:
                smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
        return True
    except Exception:
        return False


def _log_login(user_id, success: bool):
    """Insert a row into login_history. Silently ignores errors."""
    try:
        db = get_db()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr or '')
        # Trim forwarded-for to first address only
        ip = ip.split(',')[0].strip()[:45]
        ua = (request.headers.get('User-Agent') or '')[:300]
        db.execute(
            '''INSERT INTO login_history (user_id, ip_address, user_agent, success, login_at)
               VALUES (?, ?, ?, ?, datetime('now'))''',
            (user_id, ip, ua, 1 if success else 0)
        )
        db.commit()
    except Exception:
        pass  # Never crash a login because of history logging


def login_required(f):
    """Decorator — redirect to login if user is not in session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access that page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator — redirect if user is not admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.homepage'))
        return f(*args, **kwargs)
    return decorated


def _populate_session(user):
    """Write all user fields into the Flask session.

    Pulls a fresh cart_count from the DB so the panel badge is accurate
    immediately after login / registration.
    """
    session.permanent = True
    # ── Identity ──────────────────────────────────────────────────────
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['email'] = user['email']
    session['role'] = user['role']
    session['created_at'] = user['created_at'] if user['created_at'] else None
    session['profile_image'] = user['profile_image'] or None
    # ── Extended profile fields (shown in panel / settings) ───────────
    session['contact_number'] = user['contact_number'] if 'contact_number' in user.keys() else None
    session['bio'] = user['bio'] if 'bio' in user.keys() else None
    session['country'] = user['country'] if 'country' in user.keys() else None
    session['delivery_address'] = user['delivery_address'] if 'delivery_address' in user.keys() else None
    session['payment_method'] = user['payment_method'] if 'payment_method' in user.keys(
    ) else 'cash_on_delivery'
    session['wallet_balance'] = user['wallet_balance'] if 'wallet_balance' in user.keys() else 0
    session['social_link_1'] = user['social_link_1'] if 'social_link_1' in user.keys(
    ) else None
    session['social_link_2'] = user['social_link_2'] if 'social_link_2' in user.keys(
    ) else None
    session['social_link_3'] = user['social_link_3'] if 'social_link_3' in user.keys(
    ) else None
    session['social_link_4'] = user['social_link_4'] if 'social_link_4' in user.keys(
    ) else None
    # ── Live cart count ───────────────────────────────────────────────
    try:
        db = get_db()
        row = db.execute(
            'SELECT COALESCE(SUM(quantity), 0) AS cnt FROM cart_items WHERE user_id = ?',
            (user['id'],)
        ).fetchone()
        session['cart_count'] = int(row['cnt']) if row else 0
    except Exception:
        if 'cart_count' not in session:
            session['cart_count'] = 0
# ─── LOGIN ────────────────────────────────────────────────────────


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Already logged in — go home
    if session.get('user_id'):
        return redirect(url_for('main.homepage'))
    if request.method == 'POST':
        identifier = request.form.get(
            'identifier', '').strip()  # username OR email
        password = request.form.get('password', '')
        if not identifier or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/login.html')
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (identifier, identifier)
        ).fetchone()
        if user is None or not check_password_hash(user['password_hash'], password):
            if user is not None:
                _log_login(user['id'], success=False)
            flash('Invalid credentials. Try again.', 'danger')
            return render_template('auth/login.html')
        _populate_session(user)
        _log_login(user['id'], success=True)
        flash(f'Welcome back, {user["username"]}.', 'success')
        return redirect(request.args.get('next') or url_for('main.homepage'))
    return render_template('auth/login.html')
# ─── PASSWORD ──────────────────────────────────────────────


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@auth_bp.route('/password', methods=['GET', 'POST'])
def change_password():
    change_password = bool(session.get('user_id'))
    show_forgot_password = request.args.get('mode') == 'forgot'
    forgot_password_action = request.form.get(
        'auth_action') == 'forgot_password'
    if request.method == 'POST' and change_password and not forgot_password_action:
        # Handle change password for logged-in users
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        errors = []
        if not current_password or not new_password or not confirm_password:
            errors.append('All fields are required.')
        if new_password != confirm_password:
            errors.append('Passwords do not match.')
        if len(new_password) < 8:
            errors.append('Password must be at least 8 characters.')
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        if not check_password_hash(user['password_hash'], current_password):
            errors.append('Current password is incorrect.')
        if errors:
            for e in errors:
                flash(e, 'danger')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': '; '.join(errors)})
            return render_template('auth/changepassword.html', change_password=True)
        db.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (generate_password_hash(new_password), session['user_id'])
        )
        db.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': 'Password changed successfully.'})
        flash('Password changed successfully.', 'success')
        return redirect(url_for('main.homepage'))
    pending = session.get('password_reset_pending')
    if request.method == 'POST' and pending:
        if request.form.get('resend_otp'):
            otp = f'{secrets.randbelow(1000000):06d}'
            pending['otp'] = otp
            pending['otp_sent_at'] = datetime.datetime.utcnow().isoformat()
            session['password_reset_pending'] = pending
            if _send_otp_email(pending['email'], otp, purpose='reset'):
                flash('A new reset code was sent to your email.', 'info')
            else:
                flash(f'Password reset code (development): {otp}', 'warning')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'otp_sent': True, 'pending_email': pending['email']})
            return render_template('auth/changepassword.html', otp_sent=True, pending_email=pending['email'], show_forgot_password=True)
        reset_code = request.form.get('reset_code', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        errors = []
        if not reset_code or not new_password or not confirm_password:
            errors.append('All fields are required.')
        if new_password != confirm_password:
            errors.append('Passwords do not match.')
        if len(new_password) < 8:
            errors.append('Password must be at least 8 characters.')
        try:
            sent_at = datetime.datetime.fromisoformat(pending['otp_sent_at'])
        except Exception:
            sent_at = datetime.datetime.utcnow()
        if datetime.datetime.utcnow() > sent_at + datetime.timedelta(minutes=10):
            session.pop('password_reset_pending', None)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Reset code expired. Submit your email again.'})
            flash('Reset code expired. Submit your email again.', 'danger')
            return render_template('auth/changepassword.html')
        if reset_code != pending['otp']:
            errors.append('Invalid reset code.')
        if errors:
            for e in errors:
                flash(e, 'danger')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': '; '.join(errors)})
            return render_template('auth/changepassword.html', otp_sent=True, pending_email=pending['email'], show_forgot_password=True)
        db = get_db()
        db.execute(
            'UPDATE users SET password_hash = ? WHERE email = ?',
            (generate_password_hash(new_password), pending['email'])
        )
        db.commit()
        session.pop('password_reset_pending', None)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': 'Password updated successfully. Please log in.'})
        flash('Password updated successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Please enter your email address.'})
            flash('Please enter your email address.', 'danger')
            return render_template('auth/changepassword.html')
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if user is None:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'No account found for that email.'})
            flash('No account found for that email.', 'danger')
            return render_template('auth/changepassword.html', show_forgot_password=True)
        otp = f'{secrets.randbelow(1000000):06d}'
        session['password_reset_pending'] = {
            'email': email,
            'otp': otp,
            'otp_sent_at': datetime.datetime.utcnow().isoformat()
        }
        if _send_otp_email(email, otp, purpose='reset'):
            flash(
                'A reset code was sent to your email. Enter it below to reset your password.', 'info')
        else:
            flash(f'Password reset code (development): {otp}', 'warning')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'otp_sent': True, 'pending_email': email})
        return render_template('auth/changepassword.html', otp_sent=True, pending_email=email, show_forgot_password=True)
    if pending:
        return render_template('auth/changepassword.html', otp_sent=True, pending_email=pending['email'], show_forgot_password=True)
    return render_template('auth/changepassword.html', change_password=change_password, show_forgot_password=show_forgot_password)
# ─── FORGOT PASSWORD ALIAS ────────────────────────────────────────
# Keeps url_for('auth.forgot_password') working (used in templates).


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    from flask import current_app
    return current_app.view_functions['auth.change_password']()


# ─── REGISTER ─────────────────────────────────────────────────────


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('main.homepage'))
    pending = session.get('register_pending')
    if request.method == 'POST' and pending:
        if request.form.get('resend_otp'):
            otp = f'{secrets.randbelow(1000000):06d}'
            pending['otp'] = otp
            pending['otp_sent_at'] = datetime.datetime.utcnow().isoformat()
            session['register_pending'] = pending
            if _send_otp_email(pending['email'], otp):
                flash('A new verification code was sent to your email.', 'info')
            else:
                flash(f'OTP code (development): {otp}', 'warning')
            return render_template('auth/register.html', otp_sent=True, pending_email=pending['email'])
        otp_code = request.form.get('otp_code', '').strip()
        if not otp_code:
            flash('Please enter the OTP sent to your email.', 'danger')
            return render_template('auth/register.html', otp_sent=True, pending_email=pending['email'])
        try:
            sent_at = datetime.datetime.fromisoformat(pending['otp_sent_at'])
        except Exception:
            sent_at = datetime.datetime.utcnow()
        if datetime.datetime.utcnow() > sent_at + datetime.timedelta(minutes=10):
            session.pop('register_pending', None)
            flash('OTP expired. Please start registration again.', 'danger')
            return render_template('auth/register.html')
        if otp_code != pending['otp']:
            flash('Invalid OTP. Please try again.', 'danger')
            return render_template('auth/register.html', otp_sent=True, pending_email=pending['email'])
        db = get_db()
        db.execute(
            'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
            (pending['username'], pending['email'],
             pending['password_hash'], 'customer')
        )
        db.commit()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (pending['username'],)
        ).fetchone()
        session.pop('register_pending', None)
        _populate_session(user)
        flash(f'Account created. Welcome, {user["username"]}!', 'success')
        return redirect(url_for('main.homepage'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        errors = []
        if not username or not email or not password:
            errors.append('All fields are required.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('auth/register.html')
        db = get_db()
        existing = db.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        if existing:
            flash('Username or email already taken.', 'danger')
            return render_template('auth/register.html')
        pw_hash = generate_password_hash(password)
        otp = f'{secrets.randbelow(1000000):06d}'
        session['register_pending'] = {
            'username': username,
            'email': email,
            'password_hash': pw_hash,
            'otp': otp,
            'otp_sent_at': datetime.datetime.utcnow().isoformat()
        }
        if _send_otp_email(email, otp):
            flash(
                'A verification code was sent to your email. Enter it below to complete registration.', 'info')
        else:
            flash(f'OTP code (development): {otp}', 'warning')
        return render_template('auth/register.html', otp_sent=True, pending_email=email)
    if pending:
        return render_template('auth/register.html', otp_sent=True, pending_email=pending['email'])
    return render_template('auth/register.html')
# ─── LOGOUT ───────────────────────────────────────────────────────


@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'Operator')
    session.clear()
    flash(f'Session terminated. Goodbye, {username}.', 'info')
    return redirect(url_for('main.homepage'))
