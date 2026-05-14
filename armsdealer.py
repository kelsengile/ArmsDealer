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
# APPEARANCE CONTEXT PROCESSOR
# Parses the appearance cookie once per request and exposes a clean
# `appearance` dict to every template, so both base.html and subbase.html
# can inject server-side CSS without any JavaScript race conditions.
# ─────────────────────────────────────────

_ACCENT_HEX = {
    'olive':  '#a8c47a',
    'steel':  '#5b9bd5',
    'red':    '#c0392b',
    'amber':  '#e8b84b',
    'violet': '#9b59b6',
}
_FONT_PX = {
    'Small (10px)':   '10px',
    'Default (12px)': '12px',
    'Large (14px)':   '14px',
}
_APPEARANCE_DEFAULTS = {
    'colorMode':     'Dark (Default)',
    'accentColor':   'olive',
    'bgImage':       'camobackground',
    'bgOpacity':     38,
    'fontScale':     'Default (12px)',
    'scanlines':     True,
    'monospaceBody': True,
    'compactMode':   False,
    'animations':    True,
}


@app.context_processor
def inject_appearance():
    """Make `appearance` and `appearance_css` available in every template."""
    import json as _json
    raw = request.cookies.get('armsdealer_appearance')
    try:
        saved = _json.loads(raw) if raw else {}
    except Exception:
        saved = {}

    # Merge saved values over defaults so missing keys are always filled
    s = dict(_APPEARANCE_DEFAULTS)
    s.update(saved)

    accent = _ACCENT_HEX.get(s['accentColor'], _ACCENT_HEX['olive'])
    font_size = _FONT_PX.get(s['fontScale'], '12px')
    opacity = max(0, min(100, int(s['bgOpacity']))) / 100
    dark_op = round(opacity * 1.35, 3)
    bg_img = s['bgImage'] or 'camobackground'
    bg_url = f"/static/assets/images/pageimages/globalmages/{bg_img}.png"
    spacing_mul = 0.7 if s['compactMode'] else 1
    # None means use stylesheet default
    trans = '0s' if not s['animations'] else None

    # Build the <style> block that gets injected into <head>
    lines = [
        ':root {',
        f'  --mil-bright: {accent};',
        f'  --mil-green: {accent};',
        f'  font-size: {font_size};',
        f'  --spacing-sm: {round(8 * spacing_mul, 1)}px;',
        f'  --spacing-md: {round(12 * spacing_mul, 1)}px;',
        f'  --spacing-lg: {round(15 * spacing_mul, 1)}px;',
    ]
    if trans:
        lines += [
            f'  --transition-fast: {trans};',
            f'  --transition-base: {trans};',
            f'  --transition-slow: {trans};',
        ]
    lines.append('}')
    lines.append(
        f'body {{ background: linear-gradient(rgba(0,0,0,{opacity}),rgba(2,15,4,{dark_op})),'
        f' url("{bg_url}") center/cover repeat fixed; }}'
    )
    if s['scanlines']:
        lines.append('body { background-image: repeating-linear-gradient('
                     '0deg,transparent,transparent 2px,rgba(0,0,0,.08) 2px,rgba(0,0,0,.08) 4px),'
                     f' url("{bg_url}"); }}')
        # Simpler: just keep the scanlines class logic via JS; inject the class state instead
        # Reset — the scanlines CSS class already exists, just signal it server-side
        lines[-1] = ''  # Remove duplicate bg rule

    appearance_css = '\n'.join(l for l in lines if l)
    return dict(appearance=s, appearance_css=appearance_css, appearance_scanlines=s['scanlines'])


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
