# ──────────────────────────────────────────────────────────────────────────────────
# MAIN ROUTES
# ──────────────────────────────────────────────────────────────────────────────────
from flask import Blueprint, render_template, request, g, session, redirect, url_for
from db_helpers import get_db, get_locale, get_currency

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/home')
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


@main_bp.route('/products')
def products():
    return render_template('products.html')


@main_bp.route('/services')
def services():
    return render_template('services.html')


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/contacts')
def contacts():
    return render_template('contacts.html')


@main_bp.route('/settings')
def settings():
    return render_template('settings.html')


@main_bp.route('/legal')
def legal():
    return render_template('legal.html')


# ─────────────────────────────────────────
# ACCOUNT PAGE
# ─────────────────────────────────────────

@main_bp.route('/account')
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

    return render_template('user/account.html', user=user)


# ─────────────────────────────────────────
# ORDERS PAGE
# ─────────────────────────────────────────

@main_bp.route('/orders')
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
            END AS slug
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
                   END AS slug
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
                   END AS slug
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

@main_bp.route('/dashboard')
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

    stats = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_services': total_services,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_revenue': total_revenue,
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

    return render_template('user/dashboard.html', stats=stats, orders=orders)
