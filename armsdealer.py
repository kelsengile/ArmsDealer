# ──────────────────────────────────────────────────────────────────────────────────
# ARMSDEALER.PY
# ──────────────────────────────────────────────────────────────────────────────────

from db_helpers import get_db, get_locale, get_currency
import json as _json
from flask import Flask, request, g
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get(
    'SECRET_KEY', 'dev-secret-change-in-production')
DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'armsdealer.db')

# ── Custom Jinja2 filter: parse a JSON string inside templates ──


@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return _json.loads(value)
    except Exception:
        return []

# ─────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────
# Imported from db_helpers to avoid circular imports


@app.teardown_appcontext
def close_db(error):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.before_request
def refresh_session_from_db():
    """Keep the session in sync with the DB on every request.

    Refreshes all user fields that the account panel and settings page
    display — username, email, role, profile_image, and extended profile
    fields — so changes saved in one tab are visible immediately in another,
    and the panel always reflects the live database state.
    """
    from flask import session, request as _req
    # Skip static file requests — no DB needed
    if _req.endpoint == 'static':
        return
    user_id = session.get('user_id')
    if not user_id:
        return
    try:
        db = get_db()
        row = db.execute(
            '''SELECT id, username, email, role, profile_image, created_at,
                      contact_number, bio, country, delivery_address,
                      payment_method, wallet_balance,
                      social_link_1, social_link_2, social_link_3, social_link_4
               FROM users WHERE id = ?''',
            (user_id,)
        ).fetchone()
        if not row:
            # User was deleted — clear stale session
            session.clear()
            return
        # Sync all panel-visible fields
        session['username'] = row['username']
        session['email'] = row['email']
        session['role'] = row['role']
        session['profile_image'] = row['profile_image'] or None
        session['created_at'] = row['created_at'] or None
        session['contact_number'] = row['contact_number'] or None
        session['bio'] = row['bio'] or None
        session['country'] = row['country'] or None
        session['delivery_address'] = row['delivery_address'] or None
        session['payment_method'] = row['payment_method'] or 'cash_on_delivery'
        session['wallet_balance'] = row['wallet_balance'] or 0
        session['social_link_1'] = row['social_link_1'] or None
        session['social_link_2'] = row['social_link_2'] or None
        session['social_link_3'] = row['social_link_3'] or None
        session['social_link_4'] = row['social_link_4'] or None
        # Sync live cart count
        cart_row = db.execute(
            'SELECT COALESCE(SUM(quantity), 0) AS cnt FROM cart_items WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        session['cart_count'] = int(cart_row['cnt']) if cart_row else 0
    except Exception:
        pass  # Never crash a page load due to a session-sync error


# ─────────────────────────────────────────
# REGISTER BLUEPRINTS
# ─────────────────────────────────────────

# Imports are placed here (after app/helpers are defined) to avoid circular imports
from routes.auth_routes import auth_bp      # noqa: E402
from routes.main_routes import main_bp      # noqa: E402
from routes.cart_routes import cart_bp      # noqa: E402
from routes.api_routes import api_bp        # noqa: E402

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(api_bp, url_prefix='/api')

# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
