# ──────────────────────────────────────────────────────────────────────────────────
# API ROUTES
# ──────────────────────────────────────────────────────────────────────────────────
import hashlib as _hashlib
import string as _string
import secrets as _secrets
import os
from flask import Blueprint, render_template, request, g, session, redirect, url_for, jsonify, make_response
from werkzeug.utils import secure_filename
from db_helpers import get_db, get_locale, get_currency

api_bp = Blueprint('api', __name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# Resolves to  <project_root>/static/assets/images/userimages/
# api_routes.py lives in  routes/  so we go one level up to reach project root.
_ROUTES_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_ROUTES_DIR)
PROFILE_IMAGE_FOLDER = os.path.join(
    _PROJECT_ROOT, 'static', 'assets', 'images', 'userimages'
)


def _allowed_image(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@api_bp.route('/')
@api_bp.route('/home')
def homepage():
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)
    product_rows = db.execute("""
    SELECT p.id, p.slug, p.price, p.discount, p.image_file, p.tags,
           p.rating, p.sales_count,
           COALESCE(pt.name, p.name)               AS name,
           COALESCE(pt.description, p.description) AS description
    FROM products p
    LEFT JOIN products_translations pt
           ON pt.product_id = p.id AND pt.lang_code = ?
    WHERE p.id IN (1,5,6,7,8,19,21,62,161,162,163,164,165,302,319,318)
    ORDER BY p.id
""", (lang,)).fetchall()
    products = {row["id"]: row for row in product_rows}
    service_rows = db.execute("""
    SELECT s.id, s.slug, s.price, s.discount, s.image_file, s.tags,
           s.rating, s.sales_count,
           COALESCE(st.name, s.name)               AS name,
           COALESCE(st.description, s.description) AS description
    FROM services s
    LEFT JOIN services_translations st
           ON st.service_id = s.id AND st.lang_code = ?
    WHERE s.id IN (1,2,3)
    ORDER BY s.id
""", (lang,)).fetchall()
    services = {row["id"]: row for row in service_rows}
    return render_template('homepage.html', products=products, services=services, currency=currency)


@api_bp.route('/products')
def products():
    return render_template('products.html')


@api_bp.route('/products/<slug>')
def products_by_category(slug):
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)
    rate = currency['rate_to_php'] if currency else 1.0
    symbol = currency['symbol'] if currency else '₱'
    access = request.args.get('access', 'authorized').lower()
    is_authorized = 1 if access == 'authorized' else 0

    product_rows = db.execute(
        """
        SELECT p.id, p.slug, p.price, p.discount, p.image_file, p.tags,
               p.rating, p.sales_count, p.stock,
               sc.slug AS subcategory_slug,
               COALESCE(pt.name, p.name)               AS name,
               COALESCE(pt.description, p.description) AS description
        FROM products p
        LEFT JOIN products_translations pt
               ON pt.product_id = p.id AND pt.lang_code = ?
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN subcategories sc ON sc.id = p.subcategory_id
        WHERE c.slug = ? AND p.is_authorized = ?
        ORDER BY p.id
    """, (lang, slug, is_authorized)).fetchall()

    products = []
    for row in product_rows:
        product = dict(row)
        price = product.get('price') or 0
        discount = product.get('discount') or 0
        product['currency_symbol'] = symbol
        product['old_price'] = round(price * rate)
        product['new_price'] = round(price * (1 - discount / 100.0) * rate)
        products.append(product)

    return jsonify(products=products)


@api_bp.route('/brands')
def brands():
    return jsonify(brands=[])


@api_bp.route('/brands/<slug>')
def brands_by_slug(slug):
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)
    rate = currency['rate_to_php'] if currency else 1.0
    symbol = currency['symbol'] if currency else '₱'
    access = request.args.get('access', 'authorized').lower()
    is_authorized = 1 if access == 'authorized' else 0

    product_rows = db.execute(
        """
        SELECT p.id, p.slug, p.price, p.discount, p.image_file, p.tags,
               p.rating, p.sales_count, p.stock,
               COALESCE(pt.name, p.name)               AS name,
               COALESCE(pt.description, p.description) AS description
        FROM products p
        LEFT JOIN products_translations pt
               ON pt.product_id = p.id AND pt.lang_code = ?
        LEFT JOIN brands b ON b.id = p.brand_id
        WHERE b.slug = ? AND p.is_authorized = ?
        ORDER BY p.id
    """, (lang, slug, is_authorized)).fetchall()

    products = []
    for row in product_rows:
        product = dict(row)
        price = product.get('price') or 0
        discount = product.get('discount') or 0
        product['currency_symbol'] = symbol
        product['old_price'] = round(price * rate)
        product['new_price'] = round(price * (1 - discount / 100.0) * rate)
        products.append(product)

    return jsonify(products=products)


@api_bp.route('/about')
def about():
    return render_template('about.html')


@api_bp.route('/contacts')
def contacts():
    return render_template('contacts.html')


# ─────────────────────────────────────────
# LOGIN HISTORY (GET) — returns JSON for the current user
# ─────────────────────────────────────────

@api_bp.route('/login-history')
def login_history():
    """Return the current user's login history as JSON (most-recent 50)."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401
    db = get_db()
    try:
        rows = db.execute(
            '''SELECT login_at, ip_address, user_agent, success
               FROM login_history
               WHERE user_id = ?
               ORDER BY login_at DESC
               LIMIT 50''',
            (session['user_id'],)
        ).fetchall()
        return jsonify({'ok': True, 'history': [dict(r) for r in rows]})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 500


# ─────────────────────────────────────────
# SETTINGS — SAVE ACCOUNT (POST)
# ─────────────────────────────────────────

@api_bp.route('/settings/account', methods=['POST'])
def settings_account_save():
    """Save account settings submitted from the settings page."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401

    user_id = session['user_id']
    db = get_db()

    # ── Collect form fields ───────────────────────────────────────
    username = (request.form.get('username') or '').strip()
    email = (request.form.get('email') or '').strip()
    contact_number = (request.form.get('contact_number') or '').strip()
    bio = (request.form.get('bio') or '').strip()
    country = (request.form.get('country') or '').strip()
    delivery_address = (request.form.get('delivery_address') or '').strip()
    payment_method = (request.form.get('payment_method')
                      or 'cash_on_delivery').strip()
    social_link_1 = (request.form.get('social_link_1') or '').strip()
    social_link_2 = (request.form.get('social_link_2') or '').strip()
    social_link_3 = (request.form.get('social_link_3') or '').strip()
    social_link_4 = (request.form.get('social_link_4') or '').strip()

    try:
        wallet_balance = float(request.form.get('wallet_balance') or 0)
    except ValueError:
        wallet_balance = 0.0

    # ── Basic validation ──────────────────────────────────────────
    if not username:
        return jsonify({'ok': False, 'error': 'Username is required'}), 400
    if not email:
        return jsonify({'ok': False, 'error': 'Email is required'}), 400

    # ── Uniqueness checks (exclude current user) ──────────────────
    conflict = db.execute(
        'SELECT id FROM users WHERE username = ? AND id != ?', (
            username, user_id)
    ).fetchone()
    if conflict:
        return jsonify({'ok': False, 'error': 'Username already taken'}), 409

    conflict = db.execute(
        'SELECT id FROM users WHERE email = ? AND id != ?', (email, user_id)
    ).fetchone()
    if conflict:
        return jsonify({'ok': False, 'error': 'Email already in use'}), 409

    # ── Optional profile image upload ─────────────────────────────
    profile_image = None
    file = request.files.get('profile_image')
    if file and file.filename and _allowed_image(file.filename):
        filename = secure_filename(f"user_{user_id}_{file.filename}")
        os.makedirs(PROFILE_IMAGE_FOLDER, exist_ok=True)
        file.save(os.path.join(PROFILE_IMAGE_FOLDER, filename))
        profile_image = filename

    # ── Persist to DB ─────────────────────────────────────────────
    if profile_image:
        db.execute(
            '''UPDATE users SET
                username=?, email=?, contact_number=?, bio=?, country=?,
                delivery_address=?, payment_method=?, wallet_balance=?,
                social_link_1=?, social_link_2=?, social_link_3=?, social_link_4=?,
                profile_image=?, updated_at=datetime('now')
               WHERE id=?''',
            (username, email, contact_number, bio, country,
             delivery_address, payment_method, wallet_balance,
             social_link_1, social_link_2, social_link_3, social_link_4,
             profile_image, user_id)
        )
    else:
        db.execute(
            '''UPDATE users SET
                username=?, email=?, contact_number=?, bio=?, country=?,
                delivery_address=?, payment_method=?, wallet_balance=?,
                social_link_1=?, social_link_2=?, social_link_3=?, social_link_4=?,
                updated_at=datetime('now')
               WHERE id=?''',
            (username, email, contact_number, bio, country,
             delivery_address, payment_method, wallet_balance,
             social_link_1, social_link_2, social_link_3, social_link_4,
             user_id)
        )
    db.commit()

    resp = {'ok': True}
    if profile_image:
        resp['profile_image'] = profile_image
    return jsonify(resp)


# ─────────────────────────────────────────
# ACCOUNT PAGE
# ─────────────────────────────────────────

@api_bp.route('/account')
def account():
    """User account profile page. Requires login."""
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()

    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    currency = get_currency(db)
    rate = currency['rate_to_php'] if currency else 1.0
    wallet_php = float(user['wallet_balance'] or 0)
    wallet_display = wallet_php * rate
    return render_template('user/account.html', user=user, currency=currency,
                           wallet_display=wallet_display)


# ─────────────────────────────────────────
# ORDERS PAGE
# ─────────────────────────────────────────

@api_bp.route('/orders')
def orders():
    """Orders, cart, and shipping page. Requires login."""
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    db = get_db()
    user_id = session['user_id']
    currency = get_currency(db)
    rate = currency['rate_to_php'] if currency else 1

    # ── Cart items ──────────────────────────────────────────────────
    cart_rows = db.execute("""
        SELECT
            ci.item_type,
            ci.item_id,
            ci.quantity,
            CASE
                WHEN ci.item_type = 'product' THEN p.name
                WHEN ci.item_type = 'service' THEN s.name
            END AS name,
            CASE
                WHEN ci.item_type = 'product' THEN p.price
                WHEN ci.item_type = 'service' THEN s.price
            END AS price,
            CASE
                WHEN ci.item_type = 'product' THEN p.image_file
                WHEN ci.item_type = 'service' THEN s.image_file
            END AS image_file,
            CASE
                WHEN ci.item_type = 'product' THEN p.slug
                WHEN ci.item_type = 'service' THEN s.slug
            END AS slug,
            CASE
                WHEN ci.item_type = 'product' THEN p.is_authorized
                WHEN ci.item_type = 'service' THEN s.is_authorized
            END AS is_authorized
        FROM cart_items ci
        LEFT JOIN products p ON ci.item_type = 'product' AND ci.item_id = p.id
        LEFT JOIN services s ON ci.item_type = 'service' AND ci.item_id = s.id
        WHERE ci.user_id = ?
        ORDER BY ci.id DESC
    """, (user_id,)).fetchall()

    cart_items = [dict(row) for row in cart_rows]
    cart_total_php = sum((item['price'] or 0) * item['quantity']
                         for item in cart_items)

    for item in cart_items:
        item['price'] = round((item['price'] or 0) * rate)
    cart_total = round(cart_total_php * rate)

    # ── Active orders (all statuses except delivered) ───────────────
    active_order_rows = db.execute(
        """SELECT * FROM orders WHERE user_id = ? AND status != 'delivered'
           ORDER BY created_at DESC""",
        (user_id,)
    ).fetchall()

    # Attach items to each active order
    active_orders = []
    for row in active_order_rows:
        order = dict(row)
        items = db.execute("""
            SELECT oi.quantity,
                   COALESCE(oi.unit_price, 0) AS unit_price,
                   oi.item_type,
                   oi.item_id,
                   COALESCE(
                       CASE
                           WHEN oi.item_type = 'product' THEN p.name
                           WHEN oi.item_type = 'service' THEN s.name
                       END,
                       '[Deleted Item]'
                   ) AS name,
                   CASE
                       WHEN oi.item_type = 'product' THEN p.slug
                       WHEN oi.item_type = 'service' THEN s.slug
                   END AS slug,
                   CASE
                       WHEN oi.item_type = 'product' THEN p.is_authorized
                       WHEN oi.item_type = 'service' THEN s.is_authorized
                   END AS is_authorized
            FROM order_items oi
            LEFT JOIN products p ON oi.item_type = 'product' AND oi.item_id = p.id
            LEFT JOIN services s ON oi.item_type = 'service' AND oi.item_id = s.id
            WHERE oi.order_id = ?
        """, (order['id'],)).fetchall()

        order_lines = []
        for i in items:
            line = dict(i)
            line['display_price'] = round((line['unit_price'] or 0) * rate)
            order_lines.append(line)

        order['order_lines'] = order_lines
        order['total_converted'] = round((order.get('total') or 0) * rate)
        active_orders.append(order)

    # ── Delivered orders (history) ──────────────────────────────────
    delivered_rows = db.execute(
        """SELECT * FROM orders WHERE user_id = ? AND status = 'delivered'
           ORDER BY COALESCE(updated_at, created_at) DESC""",
        (user_id,)
    ).fetchall()

    # Fetch all ratings this user has already submitted (for delivered orders)
    existing_ratings = {}
    try:
        rating_rows = db.execute(
            """SELECT item_type, item_id, rating FROM product_ratings
               WHERE user_id = ?""",
            (user_id,)
        ).fetchall()
        for r in rating_rows:
            existing_ratings[(r['item_type'], r['item_id'])] = r['rating']
    except Exception:
        # Table may not exist yet — will be created by migration SQL
        pass

    delivered_orders = []
    for row in delivered_rows:
        order = dict(row)
        items = db.execute("""
            SELECT oi.quantity,
                   COALESCE(oi.unit_price, 0) AS unit_price,
                   oi.item_type,
                   oi.item_id,
                   COALESCE(
                       CASE
                           WHEN oi.item_type = 'product' THEN p.name
                           WHEN oi.item_type = 'service' THEN s.name
                       END,
                       '[Deleted Item]'
                   ) AS name,
                   CASE
                       WHEN oi.item_type = 'product' THEN p.slug
                       WHEN oi.item_type = 'service' THEN s.slug
                   END AS slug,
                   CASE
                       WHEN oi.item_type = 'product' THEN p.is_authorized
                       WHEN oi.item_type = 'service' THEN s.is_authorized
                   END AS is_authorized
            FROM order_items oi
            LEFT JOIN products p ON oi.item_type = 'product' AND oi.item_id = p.id
            LEFT JOIN services s ON oi.item_type = 'service' AND oi.item_id = s.id
            WHERE oi.order_id = ?
        """, (order['id'],)).fetchall()

        order_lines = []
        for i in items:
            line = dict(i)
            line['display_price'] = round((line['unit_price'] or 0) * rate)
            # Attach any previously submitted rating for this item
            key = (line['item_type'], line['item_id'])
            line['existing_rating'] = existing_ratings.get(key)
            order_lines.append(line)

        order['order_lines'] = order_lines
        order['total_converted'] = round((order.get('total') or 0) * rate)
        delivered_orders.append(order)

    return render_template(
        'user/orders.html',
        cart_items=cart_items,
        cart_total=cart_total,
        active_orders=active_orders,
        delivered_orders=delivered_orders,
        currency=currency
    )


# ─────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────
@api_bp.route('/dashboard')
def dashboard():
    """Admin dashboard. Requires admin role."""
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    if session.get('role') != 'admin':
        return redirect(url_for('main.homepage'))

    db = get_db()

    # ── Stats ───────────────────────────────────────────────────────
    total_users = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_orders = db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_products = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    total_services = db.execute('SELECT COUNT(*) FROM services').fetchone()[0]
    pending_orders = db.execute(
        "SELECT COUNT(*) FROM orders WHERE status != 'delivered'"
    ).fetchone()[0]
    delivered_orders = db.execute(
        "SELECT COUNT(*) FROM orders WHERE status = 'delivered'"
    ).fetchone()[0]
    revenue_row = db.execute(
        "SELECT COALESCE(SUM(total), 0) FROM orders WHERE status = 'delivered'"
    ).fetchone()
    total_revenue = revenue_row[0] if revenue_row else 0

    # ── Inquiry count ───────────────────────────────────────────────
    try:
        new_inquiries = db.execute(
            "SELECT COUNT(*) FROM inquiries WHERE status = 'new'"
        ).fetchone()[0]
    except Exception:
        new_inquiries = 0

    stats = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_services': total_services,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_revenue': total_revenue,
        'new_inquiries': new_inquiries,
    }

    # ── All orders with username and item count ─────────────────────
    order_rows = db.execute("""
        SELECT o.id, o.status, o.total, o.created_at, o.updated_at,
               u.username,
               COUNT(oi.id) AS item_count
        FROM orders o
        LEFT JOIN users u ON u.id = o.user_id
        LEFT JOIN order_items oi ON oi.order_id = o.id
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """).fetchall()
    orders = [dict(row) for row in order_rows]

    # ── Inquiries ───────────────────────────────────────────────────
    try:
        inq_rows = db.execute(
            "SELECT * FROM inquiries ORDER BY created_at DESC"
        ).fetchall()
        inquiries = [dict(row) for row in inq_rows]
    except Exception:
        inquiries = []

    # ── Inventory: all products with category and brand names ────────
    product_rows = db.execute("""
        SELECT p.id, p.name, p.slug, p.price, p.discount, p.stock,
               p.rating, p.sales_count, p.is_authorized,
               c.name  AS category_name,
               b.name  AS brand_name
        FROM products p
        LEFT JOIN categories  c ON c.id = p.category_id
        LEFT JOIN brands      b ON b.id = p.brand_id
        ORDER BY p.id
    """).fetchall()
    products = [dict(row) for row in product_rows]

    # ── Services: all services with category name ───────────────────
    service_rows = db.execute("""
        SELECT s.id, s.name, s.slug, s.price, s.discount,
               s.rating, s.sales_count, s.is_authorized,
               c.name AS category_name
        FROM services s
        LEFT JOIN categories c ON c.id = s.category_id
        ORDER BY s.id
    """).fetchall()
    services = [dict(row) for row in service_rows]

    # ── Brands ──────────────────────────────────────────────────────
    brand_rows = db.execute(
        "SELECT id, name, slug, logo_file, is_authorized FROM brands ORDER BY name"
    ).fetchall()
    brands = [dict(row) for row in brand_rows]

    # ── Users ───────────────────────────────────────────────────────
    user_rows = db.execute(
        "SELECT id, username, email, role, profile_image, country, created_at FROM users ORDER BY id"
    ).fetchall()
    users = [dict(row) for row in user_rows]

    # ── Top products by sales_count ──────────────────────────────────
    top_product_rows = db.execute("""
        SELECT name, sales_count FROM products
        ORDER BY sales_count DESC
        LIMIT 6
    """).fetchall()
    top_products = [dict(row) for row in top_product_rows]

    # ── Revenue by day (last 7 days) ────────────────────────────────
    import datetime as _dt
    revenue_by_day = []
    revenue_labels = []
    for i in range(6, -1, -1):
        day = _dt.date.today() - _dt.timedelta(days=i)
        row = db.execute(
            """SELECT COALESCE(SUM(total), 0) FROM orders
               WHERE status = 'delivered'
               AND date(created_at) = ?""",
            (day.isoformat(),)
        ).fetchone()
        revenue_by_day.append(float(row[0]) if row else 0.0)
        revenue_labels.append(day.strftime('%a').upper())

    # ── Currency for dashboard display ─────────────────────────────
    currency = get_currency(db)
    rate = currency['rate_to_php'] if currency else 1.0
    symbol = currency['symbol'] if currency else '₱'

    # Apply currency rate to revenue data and stats
    revenue_by_day_converted = [round(v * rate) for v in revenue_by_day]
    stats['total_revenue_converted'] = round(stats['total_revenue'] * rate)
    stats['currency_symbol'] = symbol

    # ── Order status breakdown for more detailed analytics ──────────
    status_breakdown = {}
    try:
        status_rows = db.execute(
            "SELECT status, COUNT(*) as cnt FROM orders GROUP BY status"
        ).fetchall()
        for row in status_rows:
            status_breakdown[row['status']] = row['cnt']
    except Exception:
        pass

    # ── Top products by revenue ──────────────────────────────────────
    top_revenue_rows = db.execute("""
        SELECT p.name, COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue,
               p.sales_count
        FROM products p
        LEFT JOIN order_items oi ON oi.item_type = 'product' AND oi.item_id = p.id
        LEFT JOIN orders o ON o.id = oi.order_id AND o.status = 'delivered'
        GROUP BY p.id
        ORDER BY revenue DESC
        LIMIT 6
    """).fetchall()
    top_revenue_products = [dict(row) for row in top_revenue_rows]

    # ── Recent users (last 5 registered) ───────────────────────────
    recent_users = db.execute(
        "SELECT id, username, email, role, created_at FROM users ORDER BY id DESC LIMIT 5"
    ).fetchall()
    recent_users = [dict(r) for r in recent_users]

    # ── Low stock products (stock <= 5) ────────────────────────────
    low_stock_rows = db.execute(
        "SELECT id, name, stock FROM products WHERE stock <= 5 ORDER BY stock ASC LIMIT 10"
    ).fetchall()
    low_stock_products = [dict(r) for r in low_stock_rows]

    # ── Categories with product counts ─────────────────────────────
    category_stats = db.execute("""
        SELECT c.name, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.id ORDER BY product_count DESC LIMIT 8
    """).fetchall()
    category_stats = [dict(r) for r in category_stats]

    return render_template(
        'user/dashboard.html',
        stats=stats,
        orders=orders,
        inquiries=inquiries,
        products=products,
        services=services,
        brands=brands,
        users=users,
        top_products=top_products,
        top_revenue_products=top_revenue_products,
        revenue_by_day=revenue_by_day_converted,
        revenue_labels=revenue_labels,
        currency=currency,
        currency_rate=rate,
        currency_symbol=symbol,
        status_breakdown=status_breakdown,
        recent_users=recent_users,
        low_stock_products=low_stock_products,
        category_stats=category_stats,
    )


# ─────────────────────────────────────────
# ADMIN ORDER STATUS UPDATE
# ─────────────────────────────────────────

@api_bp.route('/admin/order/<int:order_id>/status', methods=['POST'])
def admin_update_order_status(order_id):
    """Admin API to update order status. Returns JSON."""
    if not session.get('user_id'):
        return jsonify(ok=False, error='Not authenticated'), 401
    if session.get('role') != 'admin':
        return jsonify(ok=False, error='Forbidden'), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get('status', '').strip().lower()
    valid = {'order placed', 'packing', 'shipping', 'delivered', 'cancelled'}
    if new_status not in valid:
        return jsonify(ok=False, error='Invalid status'), 400

    db = get_db()

    # Get current order status
    order_row = db.execute(
        "SELECT status FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    if not order_row:
        return jsonify(ok=False, error='Order not found'), 404

    old_status = order_row['status'].lower()

    # Update the order status
    db.execute(
        "UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (new_status, order_id)
    )

    stock_updates = []

    # If status changed to stock-deducting status and wasn't before, deduct stock
    stock_deduct_statuses = {'shipping', 'delivered'}
    if (new_status in stock_deduct_statuses and
        old_status not in stock_deduct_statuses and
            new_status != 'cancelled'):

        # Get order items (only products have stock)
        order_items = db.execute("""
            SELECT oi.item_id, oi.quantity, p.stock
            FROM order_items oi
            JOIN products p ON oi.item_type = 'product' AND oi.item_id = p.id
            WHERE oi.order_id = ?
        """, (order_id,)).fetchall()

        for item in order_items:
            product_id = item['item_id']
            quantity = item['quantity']
            current_stock = item['stock'] or 0

            new_stock = max(0, current_stock - quantity)  # Don't go below 0

            db.execute(
                "UPDATE products SET stock = ? WHERE id = ?",
                (new_stock, product_id)
            )

            stock_updates.append({
                'product_id': product_id,
                'new_stock': new_stock
            })

    db.commit()

    response = {'ok': True, 'status': new_status}
    if stock_updates:
        response['stock_updates'] = stock_updates

    return jsonify(response)


# ─────────────────────────────────────────
# ADMIN INQUIRY STATUS UPDATE
# ─────────────────────────────────────────

@api_bp.route('/admin/inquiry/<int:inquiry_id>/status', methods=['POST'])
def admin_update_inquiry_status(inquiry_id):
    """Admin API to update inquiry status. Returns JSON."""
    if not session.get('user_id'):
        return jsonify(ok=False, error='Not authenticated'), 401
    if session.get('role') != 'admin':
        return jsonify(ok=False, error='Forbidden'), 403

    data = request.get_json(silent=True) or {}
    status = data.get('status', '').strip().lower()
    valid = {'new', 'read', 'resolved'}
    if status not in valid:
        return jsonify(ok=False, error='Invalid status'), 400

    db = get_db()
    db.execute(
        "UPDATE inquiries SET status = ? WHERE id = ?",
        (status, inquiry_id)
    )
    db.commit()
    return jsonify(ok=True, status=status)


# ─────────────────────────────────────────
# ADMIN INQUIRY REPLY (email user)
# ─────────────────────────────────────────

@api_bp.route('/admin/inquiry/<int:inquiry_id>/reply', methods=['POST'])
def admin_reply_inquiry(inquiry_id):
    """Admin sends a reply email to the inquiry submitter.
    Always sends from kelsengile.dev@gmail.com regardless of which admin is logged in.
    """
    if not session.get('user_id'):
        return jsonify(ok=False, error='Not authenticated'), 401
    if session.get('role') != 'admin':
        return jsonify(ok=False, error='Forbidden'), 403

    data = request.get_json(silent=True) or {}
    reply_message = (data.get('message') or '').strip()
    if not reply_message:
        return jsonify(ok=False, error='Reply message is required'), 400

    db = get_db()
    inq = db.execute('SELECT * FROM inquiries WHERE id = ?',
                     (inquiry_id,)).fetchone()
    if not inq:
        return jsonify(ok=False, error='Inquiry not found'), 404

    # ── Build styled email using the shared template ──────────────────────
    from email_service import _html_wrap

    inq_name = inq['name'] or 'Operator'
    inq_subject = inq['subject'] or 'Your Support Inquiry'
    inq_message = (inq['message'] or '').replace('\n', '<br>')
    reply_html = reply_message.replace('\n', '<br>')

    content = f"""
<h2>Support Reply</h2>
<p>Hello <strong>{inq_name}</strong>,</p>
<p>Thank you for reaching out to Arms Dealer Support.
   Here is our response to your inquiry.</p>

<table class="table">
  <thead>
    <tr><th>FIELD</th><th>DETAIL</th></tr>
  </thead>
  <tbody>
    <tr><td>Subject</td><td>{inq_subject}</td></tr>
    <tr><td>Inquiry&nbsp;ID</td><td>INQ-{str(inquiry_id).zfill(4)}</td></tr>
  </tbody>
</table>

<hr class="divider">
<p><strong>Your original message:</strong></p>
<p style="background:#0d160d;padding:12px 16px;border-left:3px solid #3a5a3a;
          font-size:12px;color:#8aaa80;line-height:1.7;">
  {inq_message}
</p>

<hr class="divider">
<p><strong>Our response:</strong></p>
<p style="background:#0d1a0d;padding:12px 16px;border-left:3px solid #a8c47a;
          font-size:12px;color:#c8d8c0;line-height:1.7;">
  {reply_html}
</p>

<hr class="divider">
<p style="font-size:11px;color:#5a7a5a;">
  If you have further questions, submit a new ticket from
  <em>Settings &rarr; Help &amp; Support</em>.<br>
  Do not reply to this email &mdash; replies are not monitored.
</p>
"""

    html_body = _html_wrap(content)
    subject = f'[ArmsDealer] Re: {inq_subject}'

    # ── Send via SMTP — always use the hardcoded platform address ─────────
    import smtplib as _smtp
    from email.mime.multipart import MIMEMultipart as _MIMEMulti
    from email.mime.text import MIMEText as _MIMEText

    SENDER = 'kelsengile.dev@gmail.com'
    SMTP_PASS = os.environ.get('SMTP_PASS', '')

    if not SMTP_PASS:
        return jsonify(ok=False, error='SMTP credentials not configured (SMTP_PASS missing in .env)'), 500

    try:
        msg = _MIMEMulti('alternative')
        msg['Subject'] = subject
        msg['From'] = f'ArmsDealer Support <{SENDER}>'
        msg['To'] = inq['email']
        msg['Reply-To'] = SENDER
        msg.attach(_MIMEText(html_body, 'html'))

        with _smtp.SMTP('smtp.gmail.com', 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER, SMTP_PASS)
            server.sendmail(SENDER, inq['email'], msg.as_string())

    except _smtp.SMTPAuthenticationError:
        return jsonify(ok=False, error='SMTP authentication failed — verify SMTP_PASS in .env is a valid Gmail App Password'), 500
    except _smtp.SMTPRecipientsRefused:
        return jsonify(ok=False, error=f'Recipient address rejected by server: {inq["email"]}'), 500
    except Exception as exc:
        return jsonify(ok=False, error=f'Email send failed: {exc}'), 500

    # ── Mark inquiry as resolved ──────────────────────────────────────────
    db.execute(
        "UPDATE inquiries SET status = 'resolved' WHERE id = ?", (inquiry_id,))
    db.commit()
    return jsonify(ok=True, sent_to=inq['email'])


# ─────────────────────────────────────────
# SET CURRENCY (POST) — saves cookie
# ─────────────────────────────────────────

@api_bp.route('/set-currency', methods=['POST'])
def set_currency():
    """Persist the chosen currency code as a cookie and return the symbol."""
    data = request.get_json(silent=True) or {}
    code = (data.get('currency') or '').strip().upper()

    VALID_CODES = {'PHP', 'USD', 'EUR', 'GBP', 'SGD', 'JPY', 'CNY'}
    if code not in VALID_CODES:
        return jsonify({'ok': False, 'error': 'Invalid currency code'}), 400

    db = get_db()
    row = db.execute(
        'SELECT symbol, rate_to_php FROM currencies WHERE code = ?', (code,)).fetchone()
    symbol = row['symbol'] if row else '₱'
    rate = row['rate_to_php'] if row else 1.0

    resp = make_response(
        jsonify({'ok': True, 'symbol': symbol, 'code': code, 'rate': rate}))
    resp.set_cookie('currency', code, max_age=60 *
                    60 * 24 * 365, samesite='Lax')
    return resp


@api_bp.route('/product-price/<slug>')
def product_price(slug):
    """Return currency-converted prices for a single product.
    Used by specificproduct.js to update prices live when the currency cookie changes."""
    db = get_db()
    currency = get_currency(db)
    rate = currency['rate_to_php'] if currency else 1.0
    symbol = currency['symbol'] if currency else '₱'

    row = db.execute(
        'SELECT price, discount FROM products WHERE slug = ?', (slug,)
    ).fetchone()
    if not row:
        return jsonify({'ok': False, 'error': 'Not found'}), 404

    price = row['price'] or 0
    discount = row['discount'] or 0
    old_price = round(price * rate)
    new_price = round(price * (1 - discount / 100.0) * rate)

    return jsonify({
        'ok': True,
        'symbol': symbol,
        'old_price': old_price,
        'new_price': new_price,
        'discount': discount,
    })


@api_bp.route('/search')
def search():
    q = (request.args.get('q') or '').strip()
    if len(q) < 2:
        return jsonify(products=[], brands=[], is_guest=True)

    db = get_db()
    lang = get_locale()
    currency = get_currency(db)
    rate = currency['rate_to_php'] if currency else 1.0
    symbol = currency['symbol'] if currency else '₱'

    is_logged_in = bool(session.get('user_id'))
    auth_clause = '' if is_logged_in else 'AND p.is_authorized = 1'
    brand_clause = '' if is_logged_in else 'AND b.is_authorized = 1'

    like = f'%{q}%'

    # ── Products ────────────────────────────────────────────────────
    product_rows = db.execute(f"""
        SELECT p.id, p.slug, p.price, p.discount, p.is_authorized,
               c.slug  AS category_slug,
               b.name  AS brand_name,
               COALESCE(pt.name,        p.name)        AS name,
               COALESCE(pt.description, p.description) AS description
        FROM products p
        LEFT JOIN products_translations pt
               ON pt.product_id = p.id AND pt.lang_code = ?
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN brands     b ON b.id = p.brand_id
        WHERE (
              COALESCE(pt.name, p.name)        LIKE ?
           OR COALESCE(pt.description, p.description) LIKE ?
           OR p.tags  LIKE ?
           OR b.name  LIKE ?
           OR c.name  LIKE ?
        )
        {auth_clause}
        ORDER BY p.sales_count DESC
        LIMIT 10
    """, (lang, like, like, like, like, like)).fetchall()

    products = []
    for row in product_rows:
        p = dict(row)
        price = p.get('price') or 0
        discount = p.get('discount') or 0
        p['currency_symbol'] = symbol
        p['old_price'] = round(price * rate)
        p['new_price'] = round(price * (1 - discount / 100.0) * rate)
        products.append(p)

    # ── Brands ──────────────────────────────────────────────────────
    brand_rows = db.execute(f"""
        SELECT b.id, b.name, b.slug, b.is_authorized,
               COUNT(p.id) AS product_count
        FROM brands b
        LEFT JOIN products p
               ON p.brand_id = b.id
              {'AND p.is_authorized = 1' if not is_logged_in else ''}
        WHERE b.name LIKE ?
        {brand_clause}
        GROUP BY b.id
        ORDER BY b.name
        LIMIT 6
    """, (like,)).fetchall()

    brands = [dict(row) for row in brand_rows]

    return jsonify(products=products, brands=brands, is_guest=not is_logged_in)


# ─────────────────────────────────────────
# TWO-FACTOR AUTHENTICATION
# ─────────────────────────────────────────
# Requires:  pip install pyotp


def _get_or_create_2fa_row(db, user_id):
    """Return the user_2fa row, creating the table + row if needed."""
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_2fa (
            user_id    INTEGER PRIMARY KEY REFERENCES users(id),
            secret     TEXT,
            enabled    INTEGER NOT NULL DEFAULT 0,
            backup_codes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    row = db.execute('SELECT * FROM user_2fa WHERE user_id = ?',
                     (user_id,)).fetchone()
    if not row:
        db.execute(
            'INSERT OR IGNORE INTO user_2fa (user_id) VALUES (?)', (user_id,))
        db.commit()
        row = db.execute(
            'SELECT * FROM user_2fa WHERE user_id = ?', (user_id,)).fetchone()
    return row


def _generate_backup_codes(n=8):
    import json
    chars = _string.ascii_uppercase + _string.digits
    codes = ['-'.join(''.join(_secrets.choice(chars)
                      for _ in range(4)) for _ in range(2)) for _ in range(n)]
    return codes


@api_bp.route('/2fa/status')
def twofa_status():
    """Return whether 2FA is currently enabled for the session user."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401
    db = get_db()
    row = _get_or_create_2fa_row(db, session['user_id'])
    return jsonify({'ok': True, 'enabled': bool(row['enabled'])})


@api_bp.route('/2fa/setup', methods=['POST'])
def twofa_setup():
    """Generate (or regenerate) a TOTP secret and return the otpauth URL + secret."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401
    try:
        import pyotp
    except ImportError:
        return jsonify({'ok': False, 'error': 'pyotp not installed — run: pip install pyotp'}), 500

    db = get_db()
    user_id = session['user_id']
    _get_or_create_2fa_row(db, user_id)

    secret = pyotp.random_base32()
    # Store secret but keep enabled=0 until verified
    db.execute(
        "UPDATE user_2fa SET secret=?, enabled=0, updated_at=datetime('now') WHERE user_id=?",
        (secret, user_id)
    )
    db.commit()

    # Build the otpauth:// URI for QR scanning
    username = session.get('username', 'user')
    totp = pyotp.TOTP(secret)
    otpauth = totp.provisioning_uri(name=username, issuer_name='ArmsDealer')

    return jsonify({'ok': True, 'secret': secret, 'otpauth_url': otpauth})


@api_bp.route('/2fa/enable', methods=['POST'])
def twofa_enable():
    """Verify the user's TOTP code and mark 2FA as enabled; return backup codes."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401
    try:
        import pyotp
        import json as _j
    except ImportError:
        return jsonify({'ok': False, 'error': 'pyotp not installed'}), 500

    data = request.get_json(silent=True) or {}
    code = (data.get('code') or '').strip()
    if not code:
        return jsonify({'ok': False, 'error': 'Code is required'}), 400

    db = get_db()
    user_id = session['user_id']
    row = _get_or_create_2fa_row(db, user_id)
    secret = row['secret']
    if not secret:
        return jsonify({'ok': False, 'error': 'No setup in progress — start setup first'}), 400

    totp = pyotp.TOTP(secret)
    if not totp.verify(code, valid_window=1):
        return jsonify({'ok': False, 'error': 'Invalid code — check the time on your device and try again'}), 400

    backup_codes = _generate_backup_codes()
    import json as _j
    db.execute(
        "UPDATE user_2fa SET enabled=1, backup_codes=?, updated_at=datetime('now') WHERE user_id=?",
        (_j.dumps(backup_codes), user_id)
    )
    db.commit()
    return jsonify({'ok': True, 'backup_codes': backup_codes})


@api_bp.route('/2fa/disable', methods=['POST'])
def twofa_disable():
    """Verify TOTP code and disable 2FA."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401
    try:
        import pyotp
    except ImportError:
        return jsonify({'ok': False, 'error': 'pyotp not installed'}), 500

    data = request.get_json(silent=True) or {}
    code = (data.get('code') or '').strip()
    if not code:
        return jsonify({'ok': False, 'error': 'Code is required'}), 400

    db = get_db()
    user_id = session['user_id']
    row = _get_or_create_2fa_row(db, user_id)
    if not row['enabled'] or not row['secret']:
        return jsonify({'ok': False, 'error': '2FA is not currently enabled'}), 400

    totp = pyotp.TOTP(row['secret'])
    if not totp.verify(code, valid_window=1):
        return jsonify({'ok': False, 'error': 'Invalid code — check the time on your device and try again'}), 400

    db.execute(
        "UPDATE user_2fa SET enabled=0, secret=NULL, backup_codes=NULL, updated_at=datetime('now') WHERE user_id=?",
        (user_id,)
    )
    db.commit()
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# ACTIVE SESSIONS
# ─────────────────────────────────────────


def _ensure_sessions_table(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id          TEXT PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            ip_address  TEXT,
            user_agent  TEXT,
            device_label TEXT,
            device_type  TEXT DEFAULT 'desktop',
            created_at  TEXT DEFAULT (datetime('now')),
            last_seen   TEXT DEFAULT (datetime('now')),
            revoked     INTEGER NOT NULL DEFAULT 0
        )
    ''')
    db.commit()


def _current_session_id():
    """Derive a stable session identifier from Flask's session cookie."""
    from flask import session as _session
    raw = str(_session.get('user_id', '')) + str(_session.get('_id', ''))
    return _hashlib.sha256(raw.encode()).hexdigest()[:32]


def _upsert_session(db, user_id):
    """Create or refresh the current session row (call this at login / on requests)."""
    _ensure_sessions_table(db)
    sid = _current_session_id()
    ip = request.remote_addr or '—'
    ua = request.headers.get('User-Agent', '')
    device_type = 'mobile' if any(k in ua.lower() for k in (
        'mobile', 'android', 'iphone')) else 'desktop'
    # Build a friendly label from the UA
    import re as _re
    label_parts = []
    for pattern, name in [
        (r'Chrome/(\d+)',  'Chrome'), (r'Firefox/(\d+)', 'Firefox'),
        (r'Safari/(\d+)',  'Safari'), (r'Edg/(\d+)',      'Edge'),
    ]:
        m = _re.search(pattern, ua)
        if m:
            label_parts.append(f'{name} {m.group(1)}')
            break
    for platform, pname in [('Windows NT', 'Windows'), ('Macintosh', 'macOS'), ('Linux', 'Linux'), ('Android', 'Android'), ('iPhone', 'iPhone')]:
        if platform in ua:
            label_parts.append(pname)
            break
    device_label = ' · '.join(label_parts) or 'Unknown Device'

    db.execute('''
        INSERT INTO user_sessions (id, user_id, ip_address, user_agent, device_label, device_type)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            last_seen=datetime('now'), ip_address=excluded.ip_address,
            user_agent=excluded.user_agent, device_label=excluded.device_label
    ''', (sid, user_id, ip, ua, device_label, device_type))
    db.commit()


@api_bp.route('/sessions')
def list_sessions():
    """Return all active (non-revoked) sessions for the current user."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401

    db = get_db()
    user_id = session['user_id']
    _ensure_sessions_table(db)

    # Register / refresh the current session so it always appears in the list
    _upsert_session(db, user_id)

    current_sid = _current_session_id()
    rows = db.execute(
        '''SELECT id, ip_address, user_agent, device_label, device_type, created_at, last_seen
           FROM user_sessions
           WHERE user_id=? AND revoked=0
           ORDER BY last_seen DESC''',
        (user_id,)
    ).fetchall()

    sessions_out = []
    for r in rows:
        s = dict(r)
        s['is_current'] = (s['id'] == current_sid)
        sessions_out.append(s)

    return jsonify({'ok': True, 'sessions': sessions_out})


@api_bp.route('/sessions/<session_id>/revoke', methods=['POST'])
def revoke_session(session_id):
    """Revoke a specific session (cannot revoke current one)."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401

    if session_id == _current_session_id():
        return jsonify({'ok': False, 'error': 'Cannot revoke your current session'}), 400

    db = get_db()
    _ensure_sessions_table(db)
    db.execute(
        "UPDATE user_sessions SET revoked=1 WHERE id=? AND user_id=?",
        (session_id, session['user_id'])
    )
    db.commit()
    return jsonify({'ok': True})


@api_bp.route('/sessions/revoke-all', methods=['POST'])
def revoke_all_sessions():
    """Revoke all sessions except the current one."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401

    current_sid = _current_session_id()
    db = get_db()
    _ensure_sessions_table(db)
    db.execute(
        "UPDATE user_sessions SET revoked=1 WHERE user_id=? AND id != ?",
        (session['user_id'], current_sid)
    )
    db.commit()
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# NOTIFICATION PREFERENCES
# ─────────────────────────────────────────

@api_bp.route('/settings/notifications', methods=['GET', 'POST'])
def settings_notifications():
    """GET: return current notification prefs.
       POST: save notification prefs JSON to users.notification_prefs column.
       Auto-creates the column if it doesn't yet exist (migration-safe).
    """
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not logged in'}), 401

    import json as _json
    user_id = session['user_id']
    db = get_db()

    # Ensure the column exists (safe no-op if it already does)
    try:
        db.execute("ALTER TABLE users ADD COLUMN notification_prefs TEXT")
        db.commit()
    except Exception:
        pass  # Column already exists — ignore

    if request.method == 'GET':
        from email_service import _get_notif_prefs
        prefs = _get_notif_prefs(db, user_id)
        return jsonify({'ok': True, 'prefs': prefs})

    # POST — save
    data = request.get_json(silent=True) or {}
    prefs_json = _json.dumps(data)
    db.execute(
        "UPDATE users SET notification_prefs = ? WHERE id = ?",
        (prefs_json, user_id)
    )
    db.commit()
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# SUPPORT TICKET SUBMISSION
# ─────────────────────────────────────────

@api_bp.route('/settings/support', methods=['POST'])
def settings_support():
    """Save a support inquiry from a logged-in user into the inquiries table."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not authenticated'}), 401

    data = request.get_json(silent=True) or {}
    subject = (data.get('subject') or '').strip()
    message = (data.get('message') or '').strip()

    if not subject or not message:
        return jsonify({'ok': False, 'error': 'Subject and message are required'}), 400
    if len(message) < 10:
        return jsonify({'ok': False, 'error': 'Message too short'}), 400

    db = get_db()
    user = db.execute('SELECT username, email FROM users WHERE id = ?',
                      (session['user_id'],)).fetchone()
    if not user:
        return jsonify({'ok': False, 'error': 'User not found'}), 404

    db.execute(
        'INSERT INTO inquiries (name, email, subject, message, status) VALUES (?, ?, ?, ?, ?)',
        (user['username'], user['email'], subject, message, 'new')
    )
    db.commit()
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# EXPORT ACCOUNT DATA  (shared helper)
# ─────────────────────────────────────────

def _collect_export_data(db, user_id):
    """Gather every piece of data tied to user_id. Returns a dict."""
    import datetime as _dt

    user = db.execute('SELECT * FROM users WHERE id = ?',
                      (user_id,)).fetchone()
    if not user:
        return None

    # ── Orders + items + resolved product/service names ──────────────
    orders_raw = db.execute(
        'SELECT id, status, total, notes, created_at, updated_at '
        'FROM orders WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()

    orders = []
    for o in orders_raw:
        items_raw = db.execute(
            '''SELECT oi.item_type, oi.item_id, oi.quantity, oi.unit_price,
                      COALESCE(p.name, s.name, 'Unknown Item') AS item_name
               FROM order_items oi
               LEFT JOIN products p ON oi.item_type = 'product' AND p.id = oi.item_id
               LEFT JOIN services s ON oi.item_type = 'service' AND s.id = oi.item_id
               WHERE oi.order_id = ?''',
            (o['id'],)
        ).fetchall()
        orders.append({'order': dict(o), 'items': [
                      dict(i) for i in items_raw]})

    # ── Inquiries submitted by this user (matched by email) ───────────
    try:
        inqs = db.execute(
            'SELECT id, subject, message, status, created_at '
            'FROM inquiries WHERE email = ? ORDER BY created_at DESC',
            (user['email'],)
        ).fetchall()
        inquiries = [dict(r) for r in inqs]
    except Exception:
        inquiries = []

    # ── Ratings submitted by this user ────────────────────────────────
    try:
        rat_rows = db.execute(
            '''SELECT pr.item_type, pr.item_id, pr.rating,
                      COALESCE(p.name, s.name, 'Unknown') AS item_name
               FROM product_ratings pr
               LEFT JOIN products p ON pr.item_type = 'product' AND p.id = pr.item_id
               LEFT JOIN services s ON pr.item_type = 'service' AND s.id = pr.item_id
               WHERE pr.user_id = ?
               ORDER BY pr.item_id''',
            (user_id,)
        ).fetchall()
        ratings = [dict(r) for r in rat_rows]
    except Exception:
        ratings = []

    # ── Current cart ──────────────────────────────────────────────────
    try:
        cart_rows = db.execute(
            '''SELECT ci.item_type, ci.item_id, ci.quantity, ci.added_at,
                      COALESCE(p.name, s.name, 'Unknown') AS item_name
               FROM cart_items ci
               LEFT JOIN products p ON ci.item_type = 'product' AND p.id = ci.item_id
               LEFT JOIN services s ON ci.item_type = 'service' AND s.id = ci.item_id
               WHERE ci.user_id = ?''',
            (user_id,)
        ).fetchall()
        cart = [dict(r) for r in cart_rows]
    except Exception:
        cart = []

    # ── Notification prefs ────────────────────────────────────────────
    try:
        notif_raw = db.execute(
            'SELECT notification_prefs FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        import json as _json
        notif_prefs = _json.loads(
            notif_raw['notification_prefs']) if notif_raw and notif_raw['notification_prefs'] else {}
    except Exception:
        notif_prefs = {}

    return {
        'user': dict(user),
        'orders': orders,
        'inquiries': inquiries,
        'ratings': ratings,
        'cart': cart,
        'notif_prefs': notif_prefs,
        'generated_at': _dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
    }


def _build_export_html(data):
    """Turn the export data dict into a styled HTML email body."""
    from email_service import _html_wrap

    u = data['user']
    orders = data['orders']
    inquiries = data['inquiries']
    ratings = data['ratings']
    cart = data['cart']
    notif = data['notif_prefs']
    gen = data['generated_at']

    # ── helper ───────────────────────────────────────────────────────
    def v(val, fallback='—'):
        return str(val) if val not in (None, '', 'None') else fallback

    def yn(val):
        return 'Yes' if val else 'No'

    def stars(n):
        try:
            n = int(n)
        except Exception:
            n = 0
        return ('★' * n + '☆' * (5 - n)) if 0 <= n <= 5 else v(n)

    # ── Profile ──────────────────────────────────────────────────────
    profile_rows = ''.join([
        f'<tr><td>Username</td><td>{v(u.get("username"))}</td></tr>',
        f'<tr><td>Email</td><td>{v(u.get("email"))}</td></tr>',
        f'<tr><td>Role</td><td>{v(u.get("role"))}</td></tr>',
        f'<tr><td>Country</td><td>{v(u.get("country"))}</td></tr>',
        f'<tr><td>Contact</td><td>{v(u.get("contact_number"))}</td></tr>',
        f'<tr><td>Bio</td><td>{v(u.get("bio"))}</td></tr>',
        f'<tr><td>Delivery Address</td><td>{v(u.get("delivery_address"))}</td></tr>',
        f'<tr><td>Payment Method</td><td>{v(u.get("payment_method"))}</td></tr>',
        f'<tr><td>Wallet Balance</td><td>₱{float(u.get("wallet_balance") or 0):,.2f}</td></tr>',
        f'<tr><td>Account Active</td><td>{yn(u.get("is_active", 1))}</td></tr>',
        f'<tr><td>Member Since</td><td>{v(u.get("created_at"))}</td></tr>',
        f'<tr><td>Last Updated</td><td>{v(u.get("updated_at"))}</td></tr>',
    ])

    # ── Orders ───────────────────────────────────────────────────────
    if orders:
        order_blocks = []
        for entry in orders:
            o = entry['order']
            items_html = ''.join(
                f'<tr><td>{v(i["item_name"])} ({i["item_type"]})</td>'
                f'<td style="text-align:center">{i["quantity"]}</td>'
                f'<td>₱{float(i["unit_price"]):,.2f}</td>'
                f'<td>₱{float(i["unit_price"]) * int(i["quantity"]):,.2f}</td></tr>'
                for i in entry['items']
            ) or '<tr><td colspan="4" style="color:#5a7a5a">No items recorded</td></tr>'

            order_blocks.append(f'''
<p style="margin:16px 0 6px;font-size:12px;color:#a8c47a;letter-spacing:1px;">
  ORDER #{o["id"]} &nbsp;·&nbsp;
  <span style="color:#c8d8c0">{v(o["status"]).upper()}</span> &nbsp;·&nbsp;
  ₱{float(o["total"]):,.2f} &nbsp;·&nbsp;
  <span style="color:#5a7a5a">{v(o["created_at"])}</span>
</p>
<table class="table">
  <thead><tr><th>ITEM</th><th>QTY</th><th>UNIT</th><th>SUBTOTAL</th></tr></thead>
  <tbody>{items_html}</tbody>
</table>
{"<p style='font-size:11px;color:#5a7a5a'>Notes: " + v(o['notes']) + "</p>" if o.get('notes') else ""}
''')
        orders_section = ''.join(order_blocks)
    else:
        orders_section = '<p style="color:#5a7a5a">No orders on record.</p>'

    # ── Inquiries ────────────────────────────────────────────────────
    if inquiries:
        inq_rows = ''.join(
            f'<tr><td>INQ-{str(i["id"]).zfill(4)}</td>'
            f'<td>{v(i["subject"])}</td>'
            f'<td>{v(i["status"]).upper()}</td>'
            f'<td>{v(i["created_at"])}</td>'
            f'<td style="font-size:11px;color:#8aaa80">{v(i["message"])[:120]}{"…" if len(v(i["message"])) > 120 else ""}</td></tr>'
            for i in inquiries
        )
        inquiries_section = f'''
<table class="table">
  <thead><tr><th>ID</th><th>SUBJECT</th><th>STATUS</th><th>DATE</th><th>MESSAGE</th></tr></thead>
  <tbody>{inq_rows}</tbody>
</table>'''
    else:
        inquiries_section = '<p style="color:#5a7a5a">No support inquiries on record.</p>'

    # ── Ratings ──────────────────────────────────────────────────────
    if ratings:
        rat_rows = ''.join(
            f'<tr><td>{v(r["item_name"])}</td>'
            f'<td style="text-transform:capitalize">{v(r["item_type"])}</td>'
            f'<td style="letter-spacing:2px;color:#e8b84b">{stars(r["rating"])}</td>'
            f'<td>{v(r["rating"])}/5</td></tr>'
            for r in ratings
        )
        ratings_section = f'''
<table class="table">
  <thead><tr><th>ITEM</th><th>TYPE</th><th>RATING</th><th>SCORE</th></tr></thead>
  <tbody>{rat_rows}</tbody>
</table>'''
    else:
        ratings_section = '<p style="color:#5a7a5a">No ratings submitted.</p>'

    # ── Cart ─────────────────────────────────────────────────────────
    if cart:
        cart_rows = ''.join(
            f'<tr><td>{v(c["item_name"])}</td>'
            f'<td style="text-transform:capitalize">{v(c["item_type"])}</td>'
            f'<td style="text-align:center">{v(c["quantity"])}</td>'
            f'<td>{v(c["added_at"])}</td></tr>'
            for c in cart
        )
        cart_section = f'''
<table class="table">
  <thead><tr><th>ITEM</th><th>TYPE</th><th>QTY</th><th>ADDED</th></tr></thead>
  <tbody>{cart_rows}</tbody>
</table>'''
    else:
        cart_section = '<p style="color:#5a7a5a">Cart is empty.</p>'

    # ── Notification prefs ────────────────────────────────────────────
    if notif:
        notif_rows = ''.join(
            f'<tr><td>{k.replace("_", " ").title()}</td><td>{yn(nv) if isinstance(nv, bool) else v(nv)}</td></tr>'
            for k, nv in notif.items()
        )
        notif_section = f'''
<table class="table">
  <thead><tr><th>SETTING</th><th>VALUE</th></tr></thead>
  <tbody>{notif_rows}</tbody>
</table>'''
    else:
        notif_section = '<p style="color:#5a7a5a">Default notification preferences.</p>'

    # ── Assemble full content ─────────────────────────────────────────
    def section(title, count_label, body):
        return f'''
<h2 style="margin:28px 0 8px;font-size:13px;color:#a8c47a;letter-spacing:2px;text-transform:uppercase;border-bottom:1px solid #2a3a2a;padding-bottom:6px;">
  {title} <span style="font-size:10px;color:#5a7a5a;font-weight:normal;">{count_label}</span>
</h2>
{body}'''

    content = f'''
<h2>Your Account Data Export</h2>
<p>Hello <strong>{v(u.get("username"))}</strong>,</p>
<p>As requested, here is a complete export of all data ArmsDealer holds for your account.
   This export was generated on <strong>{gen}</strong>.</p>
<hr class="divider">

{section("Profile", "", f'<table class="table"><tbody>{profile_rows}</tbody></table>')}

{section("Orders", f'— {len(orders)} total', orders_section)}

{section("Support Inquiries", f'— {len(inquiries)} total', inquiries_section)}

{section("Ratings &amp; Reviews", f'— {len(ratings)} submitted', ratings_section)}

{section("Current Cart", f'— {len(cart)} item(s)', cart_section)}

{section("Notification Preferences", "", notif_section)}

<hr class="divider">
<p style="font-size:11px;color:#5a7a5a;">
  This is a complete record of your data as of the export date.
  If you have questions, submit a ticket via Settings &rarr; Help &amp; Support.
</p>
'''
    return _html_wrap(content)


@api_bp.route('/settings/export', methods=['GET'])
def settings_export():
    """Download a plain-text export of the user's account data."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not authenticated'}), 401

    import io as _io

    db = get_db()
    data = _collect_export_data(db, session['user_id'])
    if not data:
        return jsonify({'ok': False, 'error': 'User not found'}), 404

    u = data['user']
    orders = data['orders']
    inquiries = data['inquiries']
    ratings = data['ratings']
    cart = data['cart']
    notif = data['notif_prefs']
    gen = data['generated_at']

    def v(val):
        return str(val) if val not in (None, '', 'None') else '—'

    buf = _io.StringIO()
    buf.write('=' * 60 + '\n')
    buf.write('  ARMS DEALER — ACCOUNT DATA EXPORT\n')
    buf.write('  Generated: ' + gen + '\n')
    buf.write('=' * 60 + '\n\n')

    buf.write('[PROFILE]\n')
    for field in ['username', 'email', 'role', 'country', 'contact_number',
                  'bio', 'delivery_address', 'payment_method', 'wallet_balance',
                  'is_active', 'created_at', 'updated_at']:
        buf.write(f'  {field:<20}: {v(u.get(field))}\n')

    buf.write('\n[ORDERS] — ' + str(len(orders)) + ' total\n')
    buf.write('-' * 60 + '\n')
    for entry in orders:
        o = entry['order']
        buf.write(
            f'  Order #{o["id"]}  status:{v(o["status"])}  total:PHP {o["total"]}  placed:{v(o["created_at"])}\n')
        for i in entry['items']:
            buf.write(
                f'    - {v(i["item_name"])} ({i["item_type"]})  qty:{i["quantity"]}  unit:PHP {i["unit_price"]}\n')
        if o.get('notes'):
            buf.write(f'    Notes: {v(o["notes"])}\n')
        buf.write('\n')

    buf.write('[INQUIRIES] — ' + str(len(inquiries)) + ' total\n')
    buf.write('-' * 60 + '\n')
    for inq in inquiries:
        buf.write(
            f'  INQ-{str(inq["id"]).zfill(4)}  subject:{v(inq["subject"])}  status:{v(inq["status"])}  date:{v(inq["created_at"])}\n')
        buf.write(f'    Message: {v(inq["message"])}\n\n')

    buf.write('[RATINGS] — ' + str(len(ratings)) + ' submitted\n')
    buf.write('-' * 60 + '\n')
    for r in ratings:
        buf.write(
            f'  {v(r["item_name"])} ({r["item_type"]})  rating:{r["rating"]}/5\n')

    buf.write('\n[CART] — ' + str(len(cart)) + ' item(s)\n')
    buf.write('-' * 60 + '\n')
    for c in cart:
        buf.write(
            f'  {v(c["item_name"])} ({c["item_type"]})  qty:{c["quantity"]}  added:{v(c["added_at"])}\n')

    if notif:
        buf.write('\n[NOTIFICATION PREFERENCES]\n')
        buf.write('-' * 60 + '\n')
        for k, nv in notif.items():
            buf.write(f'  {k:<30}: {nv}\n')

    buf.write('\n' + '=' * 60 + '\n')
    buf.write('End of export.\n')

    content = buf.getvalue()
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename="armsdealer_account_export.txt"'
    return response


# ─────────────────────────────────────────
# EMAIL ACCOUNT DATA EXPORT
# ─────────────────────────────────────────

@api_bp.route('/settings/export-email', methods=['POST'])
def settings_export_email():
    """Send a full HTML account data export to the user's registered email."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not authenticated'}), 401

    if not os.environ.get('SMTP_PASS', ''):
        return jsonify({'ok': False, 'error': 'Email service not configured on this server (SMTP_PASS missing)'}), 500

    db = get_db()
    data = _collect_export_data(db, session['user_id'])
    if not data:
        return jsonify({'ok': False, 'error': 'User not found'}), 404

    user_email = data['user']['email']
    username = data['user'].get('username', 'Operator')

    html_body = _build_export_html(data)

    from email_service import _send as _email_send
    sent = _email_send(
        user_email,
        '[ArmsDealer] Your Account Data Export',
        html_body
    )

    if not sent:
        return jsonify({'ok': False, 'error': 'Failed to send email — check server logs'}), 500

    return jsonify({'ok': True, 'sent_to': user_email})


# ─────────────────────────────────────────
# DEACTIVATE ACCOUNT
# ─────────────────────────────────────────

@api_bp.route('/settings/deactivate', methods=['POST'])
def settings_deactivate():
    """Set is_active=0 on the user's row, then clear the session."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not authenticated'}), 401

    db = get_db()
    db.execute('UPDATE users SET is_active = 0 WHERE id = ?',
               (session['user_id'],))
    db.commit()
    session.clear()
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# DELETE ACCOUNT (PERMANENT)
# ─────────────────────────────────────────

@api_bp.route('/settings/delete-account', methods=['POST'])
def settings_delete_account():
    """Permanently delete the user and all associated data, then clear session."""
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    db = get_db()

    # Delete cascade: cart, order_items, orders, then user
    db.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))
    order_ids = [r[0] for r in db.execute(
        'SELECT id FROM orders WHERE user_id = ?', (user_id,)).fetchall()]
    for oid in order_ids:
        db.execute('DELETE FROM order_items WHERE order_id = ?', (oid,))
    db.execute('DELETE FROM orders WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()

    session.clear()
    return jsonify({'ok': True})


# ─────────────────────────────────────────
# ADMIN PRODUCT CRUD
# ─────────────────────────────────────────

_PRODUCT_IMAGE_FOLDER = os.path.join(
    _PROJECT_ROOT, 'static', 'assets', 'images', 'productimages'
)
_SERVICE_IMAGE_FOLDER = os.path.join(
    _PROJECT_ROOT, 'static', 'assets', 'images', 'serviceimages'
)
_BRAND_IMAGE_FOLDER = os.path.join(
    _PROJECT_ROOT, 'static', 'assets', 'images', 'brandimages'
)


def _admin_required():
    if not session.get('user_id'):
        return jsonify(ok=False, error='Not authenticated'), 401
    if session.get('role') != 'admin':
        return jsonify(ok=False, error='Forbidden'), 403
    return None


@api_bp.route('/admin/product/add', methods=['POST'])
def admin_add_product():
    err = _admin_required()
    if err:
        return err
    db = get_db()
    name = (request.form.get('name') or '').strip()
    if not name:
        return jsonify(ok=False, error='Name is required'), 400
    try:
        price = float(request.form.get('price') or 0)
        stock = int(request.form.get('stock') or 0)
        discount = float(request.form.get('discount') or 0)
        category_id = request.form.get('category_id') or None
        brand_id = request.form.get('brand_id') or None
        description = (request.form.get('description') or '').strip()
        is_authorized = int(request.form.get('is_authorized') or 1)
        slug = name.lower().replace(' ', '-').replace('/', '-')
        # Ensure slug uniqueness
        existing = db.execute(
            'SELECT id FROM products WHERE slug = ?', (slug,)).fetchone()
        if existing:
            import time
            slug = slug + '-' + str(int(time.time()))[-4:]
        image_file = None
        file = request.files.get('image_file')
        if file and file.filename and _allowed_image(file.filename):
            fname = secure_filename(f"prod_{slug}_{file.filename}")
            os.makedirs(_PRODUCT_IMAGE_FOLDER, exist_ok=True)
            file.save(os.path.join(_PRODUCT_IMAGE_FOLDER, fname))
            image_file = fname
        cur = db.execute(
            '''INSERT INTO products (name, slug, price, stock, discount, description,
               category_id, brand_id, is_authorized, image_file, rating, sales_count)
               VALUES (?,?,?,?,?,?,?,?,?,?,0,0)''',
            (name, slug, price, stock, discount, description,
             category_id, brand_id, is_authorized, image_file)
        )
        db.commit()
        return jsonify(ok=True, id=cur.lastrowid, slug=slug)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@api_bp.route('/admin/product/<int:pid>/edit', methods=['POST'])
def admin_edit_product(pid):
    err = _admin_required()
    if err:
        return err
    db = get_db()
    row = db.execute('SELECT * FROM products WHERE id = ?', (pid,)).fetchone()
    if not row:
        return jsonify(ok=False, error='Product not found'), 404
    try:
        name = (request.form.get('name') or row['name']).strip()
        price = float(request.form.get('price') or row['price'])
        stock = int(request.form.get('stock') or row['stock'])
        discount = float(request.form.get('discount') or row['discount'] or 0)
        category_id = request.form.get('category_id') or row['category_id']
        brand_id = request.form.get('brand_id') or row['brand_id']
        description = (request.form.get('description')
                       or row['description'] or '').strip()
        is_authorized = int(request.form.get('is_authorized') if request.form.get(
            'is_authorized') is not None else row['is_authorized'])
        image_file = row['image_file']
        file = request.files.get('image_file')
        if file and file.filename and _allowed_image(file.filename):
            slug = row['slug']
            fname = secure_filename(f"prod_{slug}_{file.filename}")
            os.makedirs(_PRODUCT_IMAGE_FOLDER, exist_ok=True)
            file.save(os.path.join(_PRODUCT_IMAGE_FOLDER, fname))
            image_file = fname
        db.execute(
            '''UPDATE products SET name=?, price=?, stock=?, discount=?, description=?,
               category_id=?, brand_id=?, is_authorized=?, image_file=?
               WHERE id=?''',
            (name, price, stock, discount, description,
             category_id, brand_id, is_authorized, image_file, pid)
        )
        db.commit()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@api_bp.route('/admin/product/<int:pid>/delete', methods=['POST'])
def admin_delete_product(pid):
    err = _admin_required()
    if err:
        return err
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (pid,))
    db.commit()
    return jsonify(ok=True)


# ─────────────────────────────────────────
# ADMIN SERVICE CRUD
# ─────────────────────────────────────────

@api_bp.route('/admin/service/add', methods=['POST'])
def admin_add_service():
    err = _admin_required()
    if err:
        return err
    db = get_db()
    name = (request.form.get('name') or '').strip()
    if not name:
        return jsonify(ok=False, error='Name is required'), 400
    try:
        price = float(request.form.get('price') or 0)
        discount = float(request.form.get('discount') or 0)
        category_id = request.form.get('category_id') or None
        description = (request.form.get('description') or '').strip()
        is_authorized = int(request.form.get('is_authorized') or 1)
        slug = name.lower().replace(' ', '-').replace('/', '-')
        existing = db.execute(
            'SELECT id FROM services WHERE slug = ?', (slug,)).fetchone()
        if existing:
            import time
            slug = slug + '-' + str(int(time.time()))[-4:]
        image_file = None
        file = request.files.get('image_file')
        if file and file.filename and _allowed_image(file.filename):
            fname = secure_filename(f"svc_{slug}_{file.filename}")
            os.makedirs(_SERVICE_IMAGE_FOLDER, exist_ok=True)
            file.save(os.path.join(_SERVICE_IMAGE_FOLDER, fname))
            image_file = fname
        cur = db.execute(
            '''INSERT INTO services (name, slug, price, discount, description,
               category_id, is_authorized, image_file, rating, sales_count)
               VALUES (?,?,?,?,?,?,?,?,0,0)''',
            (name, slug, price, discount, description,
             category_id, is_authorized, image_file)
        )
        db.commit()
        return jsonify(ok=True, id=cur.lastrowid, slug=slug)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@api_bp.route('/admin/service/<int:sid>/edit', methods=['POST'])
def admin_edit_service(sid):
    err = _admin_required()
    if err:
        return err
    db = get_db()
    row = db.execute('SELECT * FROM services WHERE id = ?', (sid,)).fetchone()
    if not row:
        return jsonify(ok=False, error='Service not found'), 404
    try:
        name = (request.form.get('name') or row['name']).strip()
        price = float(request.form.get('price') or row['price'])
        discount = float(request.form.get('discount') or row['discount'] or 0)
        category_id = request.form.get('category_id') or row['category_id']
        description = (request.form.get('description')
                       or row['description'] or '').strip()
        is_authorized = int(request.form.get('is_authorized') if request.form.get(
            'is_authorized') is not None else row['is_authorized'])
        image_file = row['image_file']
        file = request.files.get('image_file')
        if file and file.filename and _allowed_image(file.filename):
            slug = row['slug']
            fname = secure_filename(f"svc_{slug}_{file.filename}")
            os.makedirs(_SERVICE_IMAGE_FOLDER, exist_ok=True)
            file.save(os.path.join(_SERVICE_IMAGE_FOLDER, fname))
            image_file = fname
        db.execute(
            '''UPDATE services SET name=?, price=?, discount=?, description=?,
               category_id=?, is_authorized=?, image_file=? WHERE id=?''',
            (name, price, discount, description,
             category_id, is_authorized, image_file, sid)
        )
        db.commit()
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@api_bp.route('/admin/service/<int:sid>/delete', methods=['POST'])
def admin_delete_service(sid):
    err = _admin_required()
    if err:
        return err
    db = get_db()
    db.execute('DELETE FROM services WHERE id = ?', (sid,))
    db.commit()
    return jsonify(ok=True)


# ─────────────────────────────────────────
# ADMIN USER MANAGEMENT
# ─────────────────────────────────────────

@api_bp.route('/admin/user/<int:uid>/role', methods=['POST'])
def admin_update_user_role(uid):
    err = _admin_required()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    role = (data.get('role') or '').strip().lower()
    if role not in ('admin', 'customer'):
        return jsonify(ok=False, error='Invalid role'), 400
    db = get_db()
    db.execute("UPDATE users SET role=? WHERE id=?", (role, uid))
    db.commit()
    return jsonify(ok=True, role=role)


@api_bp.route('/admin/user/<int:uid>/delete', methods=['POST'])
def admin_delete_user(uid):
    err = _admin_required()
    if err:
        return err
    if uid == session.get('user_id'):
        return jsonify(ok=False, error='Cannot delete your own account'), 400
    db = get_db()
    db.execute('DELETE FROM cart_items WHERE user_id = ?', (uid,))
    order_ids = [r[0] for r in db.execute(
        'SELECT id FROM orders WHERE user_id = ?', (uid,)).fetchall()]
    for oid in order_ids:
        db.execute('DELETE FROM order_items WHERE order_id = ?', (oid,))
    db.execute('DELETE FROM orders WHERE user_id = ?', (uid,))
    db.execute('DELETE FROM users WHERE id = ?', (uid,))
    db.commit()
    return jsonify(ok=True)


# ─────────────────────────────────────────
# ADMIN CATEGORIES (for product/service add forms)
# ─────────────────────────────────────────

@api_bp.route('/admin/categories')
def admin_get_categories():
    err = _admin_required()
    if err:
        return err
    db = get_db()
    rows = db.execute(
        'SELECT id, name, type FROM categories ORDER BY name').fetchall()
    return jsonify(ok=True, categories=[dict(r) for r in rows])


@api_bp.route('/admin/brands-list')
def admin_get_brands():
    err = _admin_required()
    if err:
        return err
    db = get_db()
    rows = db.execute('SELECT id, name FROM brands ORDER BY name').fetchall()
    return jsonify(ok=True, brands=[dict(r) for r in rows])
