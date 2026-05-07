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
def refresh_profile_image():
    """Keep session profile_image in sync with the DB on every request."""
    from flask import session
    user_id = session.get('user_id')
    if user_id:
        db = get_db()
        row = db.execute(
            'SELECT profile_image FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        if row:
            session['profile_image'] = row['profile_image'] or None


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
app.register_blueprint(api_bp)

# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
