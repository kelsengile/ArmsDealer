# ──────────────────────────────────────────────────────────────────────────────────
# MAIN ROUTES
# ──────────────────────────────────────────────────────────────────────────────────
from flask import Blueprint, render_template, request, g, session, redirect, url_for, jsonify, make_response, abort
from db_helpers import get_db, get_locale, get_currency

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/home')
def homepage():
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)
    product_rows = db.execute("""
    SELECT p.id, p.slug, p.price, p.discount, p.image_file, p.tags, p.rating, p.sales_count,
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


@main_bp.route('/product/<slug>')
def product_detail(slug):
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)

    product = db.execute(
        """
        SELECT p.*, c.slug AS category_slug, c.name AS category_name,
               sc.slug AS subcategory_slug, sc.name AS subcategory_name,
               b.slug AS brand_slug, b.name AS brand_name, b.logo_file AS logo_file,
               COALESCE(pt.name, p.name)               AS name,
               COALESCE(pt.description, p.description) AS description
        FROM products p
        LEFT JOIN products_translations pt
               ON pt.product_id = p.id AND pt.lang_code = ?
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN subcategories sc ON sc.id = p.subcategory_id
        LEFT JOIN brands b ON b.id = p.brand_id
        WHERE p.slug = ?
    """, (lang, slug)).fetchone()
    if not product:
        abort(404)

    product_images = db.execute(
        'SELECT image_file FROM product_images WHERE product_id = ? ORDER BY id ASC',
        (product['id'],)
    ).fetchall()
    brand_product_count = 0
    if product['brand_id']:
        count_row = db.execute(
            'SELECT COUNT(*) AS cnt FROM products WHERE brand_id = ?',
            (product['brand_id'],)
        ).fetchone()
        brand_product_count = int(count_row['cnt']) if count_row else 0

    related = []
    if product['subcategory_id'] and product['brand_id']:
        # Priority 1: same brand + same subcategory
        related_rows = db.execute(
            """
            SELECT p.*, COALESCE(pt.name, p.name) AS name,
                   COALESCE(pt.description, p.description) AS description
            FROM products p
            LEFT JOIN products_translations pt
                   ON pt.product_id = p.id AND pt.lang_code = ?
            WHERE p.brand_id = ?
              AND p.subcategory_id = ?
              AND p.id != ?
              AND p.is_authorized = ?
            ORDER BY p.sales_count DESC
            LIMIT 6
            """, (lang, product['brand_id'], product['subcategory_id'],
                  product['id'], product['is_authorized'])).fetchall()
        related = [dict(row) for row in related_rows]

    if len(related) < 6 and product['subcategory_id']:
        # Priority 2: same subcategory (any brand), fill up to 6
        seen_ids = {r['id'] for r in related} | {product['id']}
        placeholders = ','.join('?' for _ in seen_ids)
        fill_rows = db.execute(
            f"""
            SELECT p.*, COALESCE(pt.name, p.name) AS name,
                   COALESCE(pt.description, p.description) AS description
            FROM products p
            LEFT JOIN products_translations pt
                   ON pt.product_id = p.id AND pt.lang_code = ?
            WHERE p.subcategory_id = ?
              AND p.id NOT IN ({placeholders})
              AND p.is_authorized = ?
            ORDER BY p.sales_count DESC
            LIMIT ?
            """, (lang, product['subcategory_id'], *seen_ids,
                  product['is_authorized'], 6 - len(related))).fetchall()
        related += [dict(row) for row in fill_rows]

    if len(related) < 6 and product['category_id']:
        # Priority 3: same category (any subcategory), fill up to 6
        seen_ids = {r['id'] for r in related} | {product['id']}
        placeholders = ','.join('?' for _ in seen_ids)
        fill_rows = db.execute(
            f"""
            SELECT p.*, COALESCE(pt.name, p.name) AS name,
                   COALESCE(pt.description, p.description) AS description
            FROM products p
            LEFT JOIN products_translations pt
                   ON pt.product_id = p.id AND pt.lang_code = ?
            WHERE p.category_id = ?
              AND p.id NOT IN ({placeholders})
              AND p.is_authorized = ?
            ORDER BY p.sales_count DESC
            LIMIT ?
            """, (lang, product['category_id'], *seen_ids,
                  product['is_authorized'], 6 - len(related))).fetchall()
        related += [dict(row) for row in fill_rows]

    return render_template(
        'specific/specificproduct.html',
        product=product,
        product_images=[dict(img) for img in product_images],
        brand_product_count=brand_product_count,
        related=related,
        currency=currency
    )


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

    # ── Login history (most-recent 50 entries) ─────────────────────
    login_history = []
    if user:
        try:
            from datetime import datetime as _dt
            rows = db.execute(
                '''SELECT login_at, ip_address, user_agent, success
                   FROM login_history
                   WHERE user_id = ?
                   ORDER BY login_at DESC
                   LIMIT 50''',
                (user['id'],)
            ).fetchall()
            parsed = []
            for r in rows:
                entry = dict(r)
                raw = entry.get('login_at')
                if isinstance(raw, str):
                    # SQLite stores datetimes as strings; parse the two common formats
                    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f'):
                        try:
                            entry['login_at'] = _dt.strptime(raw, fmt)
                            break
                        except ValueError:
                            continue
                parsed.append(entry)
            login_history = parsed
        except Exception:
            pass  # Table may not exist on older DBs — fail gracefully

    return render_template('settings.html', user=user, currency=currency,
                           wallet_display=wallet_display,
                           login_history=login_history)


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

    currency = get_currency(db)
    rate = currency['rate_to_php'] if currency else 1.0
    wallet_php = float(user['wallet_balance'] or 0)
    wallet_display = wallet_php * rate
    return render_template('user/account.html', user=user, currency=currency,
                           wallet_display=wallet_display)


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
               p.category_id, p.subcategory_id, p.brand_id,
               p.description, p.image_file,
               c.name  AS category_name,
               b.name  AS brand_name
        FROM products p
        LEFT JOIN categories  c ON c.id = p.category_id
        LEFT JOIN brands      b ON b.id = p.brand_id
        ORDER BY p.id
    """).fetchall()
    # Fetch product_images for each product (up to 5)
    product_images_map = {}
    img_rows = db.execute(
        'SELECT product_id, image_file FROM product_images ORDER BY product_id, sort_order ASC'
    ).fetchall()
    for img in img_rows:
        pid = img['product_id']
        product_images_map.setdefault(pid, [])
        if len(product_images_map[pid]) < 5:
            product_images_map[pid].append(img['image_file'])
    products = []
    for row in product_rows:
        d = dict(row)
        imgs = product_images_map.get(d['id'], [])
        # Fall back to legacy image_file if product_images table is empty
        if not imgs and d.get('image_file'):
            imgs = [d['image_file']]
        d['images_json'] = __import__('json').dumps(imgs)
        products.append(d)

    # ── Services: all services with category name ───────────────────
    service_rows = db.execute("""
        SELECT s.id, s.name, s.slug, s.price, s.discount,
               s.rating, s.sales_count, s.is_authorized,
               s.category_id, s.subcategory_id, s.brand_id,
               s.description, s.image_file,
               c.name AS category_name
        FROM services s
        LEFT JOIN categories c ON c.id = s.category_id
        ORDER BY s.id
    """).fetchall()
    services = []
    for row in service_rows:
        d = dict(row)
        imgs = [d['image_file']] if d.get('image_file') else []
        d['images_json'] = __import__('json').dumps(imgs)
        services.append(d)

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
# SET CURRENCY (POST) — saves cookie
# ─────────────────────────────────────────

# ─────────────────────────────────────────
# SET APPEARANCE (POST) — saves cookie
# ─────────────────────────────────────────

@main_bp.route('/set-appearance', methods=['POST'])
def set_appearance():
    """Persist chosen appearance settings as a cookie so every page load
    can inject the right CSS directly from the server — no JS race."""
    import json as _json
    data = request.get_json(silent=True) or {}

    VALID_COLORS = {'olive', 'steel', 'red', 'amber', 'violet'}
    VALID_MODES = {'Dark (Default)', 'Light', 'High Contrast'}
    VALID_FONTS = {'Small (10px)', 'Default (12px)', 'Large (14px)'}

    settings = {
        'colorMode':     data.get('colorMode',     'Dark (Default)') if data.get('colorMode') in VALID_MODES else 'Dark (Default)',
        'accentColor':   data.get('accentColor',   'olive') if data.get('accentColor') in VALID_COLORS else 'olive',
        'bgImage':       data.get('bgImage',       'camobackground'),
        'bgOpacity':     max(0, min(100, int(data.get('bgOpacity', 38)))),
        'fontScale':     data.get('fontScale',     'Default (12px)') if data.get('fontScale') in VALID_FONTS else 'Default (12px)',
        'scanlines':     bool(data.get('scanlines',     True)),
        'monospaceBody': bool(data.get('monospaceBody', True)),
        'compactMode':   bool(data.get('compactMode',   False)),
        'animations':    bool(data.get('animations',    True)),
    }

    resp = make_response(jsonify({'ok': True}))
    resp.set_cookie(
        'armsdealer_appearance',
        _json.dumps(settings, separators=(',', ':')),
        max_age=60 * 60 * 24 * 365,
        samesite='Lax'
    )
    return resp


# ─────────────────────────────────────────
# SET CURRENCY (POST) — saves cookie
# ─────────────────────────────────────────

@main_bp.route('/set-currency', methods=['POST'])
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
