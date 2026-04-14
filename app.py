from flask import Flask, render_template, redirect, url_for, request, session, flash, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get(
    'SECRET_KEY', 'dev-secret-change-in-production')

DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'armsdealer.db')


# ─────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────

def get_db():
    """Open a database connection if none exists for the current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def get_locale():
    return request.cookies.get('lang', 'english')


def get_currency(db):
    code = request.cookies.get('currency', 'PHP')
    currency = db.execute(
        "SELECT * FROM currencies WHERE code = ?", (code,)
    ).fetchone()
    return currency or db.execute(
        "SELECT * FROM currencies WHERE code = 'PHP'"
    ).fetchone()

# ─────────────────────────────────────────
# MAIN ROUTES
# ─────────────────────────────────────────


@app.route('/')
@app.route('/home')
def homepage():
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)

    product_rows = db.execute("""
    SELECT p.id, p.price, p.discount, p.image_file, p.tags,
           COALESCE(pt.name, p.name)               AS name,
           COALESCE(pt.description, p.description) AS description
    FROM products p
    LEFT JOIN product_translations pt
           ON pt.product_id = p.id AND pt.lang_code = ?
    WHERE p.id IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
    ORDER BY p.id
""", (lang,)).fetchall()

    products = {row["id"]: row for row in product_rows}

    service_rows = db.execute("""
    SELECT s.id, s.price, s.discount, s.image_file, s.tags,
           COALESCE(st.name, s.name)               AS name,
           COALESCE(st.description, s.description) AS description
    FROM services s
    LEFT JOIN service_translations st
           ON st.service_id = s.id AND st.lang_code = ?
    WHERE s.id IN (1,2,3)
    ORDER BY s.id
""", (lang,)).fetchall()
    services = {row["id"]: row for row in service_rows}

    return render_template('homepage.html', products=products, services=services, currency=currency)


@app.route('/products')
def products():
    return render_template('products.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/legal')
def legal():
    return render_template('legal.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


# ─────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: implement login logic
        pass
    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # TODO: implement registration logic
        pass
    return render_template('auth/register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))


# ─────────────────────────────────────────
# CART & CHECKOUT ROUTES
# ─────────────────────────────────────────

@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
