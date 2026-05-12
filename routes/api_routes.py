# ──────────────────────────────────────────────────────────────────────────────────
# API ROUTES
# ──────────────────────────────────────────────────────────────────────────────────
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


@api_bp.route('/settings')
def settings():
    db = get_db()
    currency = get_currency(db)
    user = None
    if session.get('user_id'):
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (session['user_id'],)
        ).fetchone()
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))
    rate = currency['rate_to_php'] if currency else 1.0
    wallet_php = float(user['wallet_balance'] or 0) if user else 0.0
    wallet_display = round(wallet_php * rate, 2)
    return render_template('settings.html', user=user, currency=currency,
                           wallet_display=wallet_display)


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
        revenue_by_day=revenue_by_day,
        revenue_labels=revenue_labels,
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
# SET CURRENCY (POST) — saves cookie
# ─────────────────────────────────────────

@api_bp.route('/set-currency', methods=['POST'])
def set_currency():
    """Persist the chosen currency code as a cookie and return the symbol."""
    data = request.get_json(silent=True) or {}
    code = (data.get('currency') or '').strip().upper()

    VALID_CODES = {'PHP', 'USD', 'EUR', 'GBP', 'SGD', 'JPY'}
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
