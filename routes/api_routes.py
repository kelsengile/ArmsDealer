# ──────────────────────────────────────────────────────────────────────────────────
# API ROUTES
# ──────────────────────────────────────────────────────────────────────────────────
from flask import Blueprint, request, jsonify, render_template, session
from db_helpers import get_db, get_locale, get_currency

api_bp = Blueprint('api', __name__)


# ─────────────────────────────────────────
# PRODUCT & SERVICE LISTING API
# ─────────────────────────────────────────

@api_bp.route('/api/products/<category_slug>')
def api_products_by_category(category_slug):
    """Return all products for a given category slug filtered by access level."""
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)
    access = request.args.get('access', 'authorized')
    is_authorized = 1 if access == 'authorized' else 0

    rows = db.execute("""
        SELECT p.id, p.slug, p.price, p.discount, p.image_file, p.tags,
               p.is_authorized, p.rating, p.sales_count,
               p.subcategory_id,
               sc.slug AS subcategory_slug,
               COALESCE(pt.name, p.name)               AS name,
               COALESCE(pt.description, p.description) AS description
        FROM products p
        JOIN categories c ON c.id = p.category_id
        LEFT JOIN subcategories sc ON sc.id = p.subcategory_id
        LEFT JOIN products_translations pt
               ON pt.product_id = p.id AND pt.lang_code = ?
        WHERE c.slug = ?
          AND p.is_authorized = ?
        ORDER BY p.id
    """, (lang, category_slug, is_authorized)).fetchall()

    result = []
    for r in rows:
        discounted = r['price'] - (r['price'] * (r['discount'] / 100))
        result.append({
            'id':               r['id'],
            'slug':             r['slug'],
            'name':             r['name'],
            'description':      r['description'],
            'price':            r['price'],
            'discount':         r['discount'],
            'image_file':       r['image_file'] or '',
            'tags':             r['tags'] or '[]',
            'is_authorized':    r['is_authorized'],
            'rating':           r['rating'],
            'sales_count':      r['sales_count'],
            'subcategory_slug': r['subcategory_slug'] or '',
            'currency_symbol':  currency['symbol'],
            'currency_rate':    currency['rate_to_php'],
            'old_price':        round(r['price'] * currency['rate_to_php']),
            'new_price':        round(discounted * currency['rate_to_php']),
        })
    return jsonify(products=result)


@api_bp.route('/api/services/<category_slug>')
def api_services_by_category(category_slug):
    """Return all services for a given category slug."""
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)
    access = request.args.get('access', 'authorized')
    is_authorized = 1 if access == 'authorized' else 0

    rows = db.execute("""
        SELECT s.id, s.slug, s.price, s.discount, s.image_file, s.tags,
               s.is_authorized, s.rating, s.sales_count,
               s.subcategory_id,
               sc.slug AS subcategory_slug,
               COALESCE(st.name, s.name)               AS name,
               COALESCE(st.description, s.description) AS description
        FROM services s
        JOIN categories c ON c.id = s.category_id
        LEFT JOIN subcategories sc ON sc.id = s.subcategory_id
        LEFT JOIN services_translations st
               ON st.service_id = s.id AND st.lang_code = ?
        WHERE c.slug = ?
          AND s.is_authorized = ?
        ORDER BY s.id
    """, (lang, category_slug, is_authorized)).fetchall()

    result = []
    for r in rows:
        discounted = r['price'] - (r['price'] * (r['discount'] / 100))
        result.append({
            'id':               r['id'],
            'slug':             r['slug'],
            'name':             r['name'],
            'description':      r['description'],
            'price':            r['price'],
            'discount':         r['discount'],
            'image_file':       r['image_file'] or '',
            'tags':             r['tags'] or '[]',
            'is_authorized':    r['is_authorized'],
            'rating':           r['rating'],
            'sales_count':      r['sales_count'],
            'subcategory_slug': r['subcategory_slug'] or '',
            'currency_symbol':  currency['symbol'],
            'currency_rate':    currency['rate_to_php'],
            'old_price':        round(r['price'] * currency['rate_to_php']),
            'new_price':        round(discounted * currency['rate_to_php']),
        })
    return jsonify(products=result)


@api_bp.route('/api/brands/<brand_slug>')
def api_products_by_brand(brand_slug):
    """Return all products for a given brand slug filtered by access level."""
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)
    access = request.args.get('access', 'authorized')
    is_authorized = 1 if access == 'authorized' else 0

    rows = db.execute("""
        SELECT p.id, p.slug, p.price, p.discount, p.image_file, p.tags,
               p.is_authorized, p.rating, p.sales_count,
               p.subcategory_id,
               sc.slug AS subcategory_slug,
               COALESCE(pt.name, p.name)               AS name,
               COALESCE(pt.description, p.description) AS description
        FROM products p
        JOIN brands b ON b.id = p.brand_id
        LEFT JOIN subcategories sc ON sc.id = p.subcategory_id
        LEFT JOIN products_translations pt
               ON pt.product_id = p.id AND pt.lang_code = ?
        WHERE b.slug = ?
          AND p.is_authorized = ?
        ORDER BY p.id
    """, (lang, brand_slug, is_authorized)).fetchall()

    result = []
    for r in rows:
        discounted = r['price'] - (r['price'] * (r['discount'] / 100))
        result.append({
            'id':               r['id'],
            'slug':             r['slug'],
            'name':             r['name'],
            'description':      r['description'],
            'price':            r['price'],
            'discount':         r['discount'],
            'image_file':       r['image_file'] or '',
            'tags':             r['tags'] or '[]',
            'is_authorized':    r['is_authorized'],
            'rating':           r['rating'],
            'sales_count':      r['sales_count'],
            'subcategory_slug': r['subcategory_slug'] or '',
            'currency_symbol':  currency['symbol'],
            'currency_rate':    currency['rate_to_php'],
            'old_price':        round(r['price'] * currency['rate_to_php']),
            'new_price':        round(discounted * currency['rate_to_php']),
        })
    return jsonify(products=result)


# ─────────────────────────────────────────
# PRODUCT DETAIL ROUTE
# ─────────────────────────────────────────

@api_bp.route('/product/<slug>')
def product_detail(slug):
    db = get_db()
    lang = get_locale()
    currency = get_currency(db)

    product = db.execute("""
        SELECT p.id, p.slug, p.price, p.discount, p.image_file, p.tags,
               p.is_authorized, p.rating, p.sales_count, p.stock,
               p.brand_id,
               b.name AS brand_name, b.slug AS brand_slug, b.logo_file,
               c.slug AS category_slug, c.name AS category_name,
               sc.slug AS subcategory_slug, sc.name AS subcategory_name,
               COALESCE(pt.name, p.name)               AS name,
               COALESCE(pt.description, p.description) AS description
        FROM products p
        LEFT JOIN categories c     ON c.id = p.category_id
        LEFT JOIN subcategories sc ON sc.id = p.subcategory_id
        LEFT JOIN brands b         ON b.id = p.brand_id
        LEFT JOIN products_translations pt
               ON pt.product_id = p.id AND pt.lang_code = ?
        WHERE p.slug = ?
    """, (lang, slug)).fetchone()

    if not product:
        return "Product not found", 404

    # ── Additional product images (for the 5-slot gallery) ──────────────
    product_images = db.execute("""
        SELECT image_file, sort_order
        FROM product_images
        WHERE product_id = ?
        ORDER BY sort_order ASC
        LIMIT 4
    """, (product['id'],)).fetchall()

    # ── Brand product count ──────────────────────────────────────────────
    brand_product_count = 0
    if product['brand_id']:
        row = db.execute(
            "SELECT COUNT(*) AS cnt FROM products WHERE brand_id = ?",
            (product['brand_id'],)
        ).fetchone()
        brand_product_count = row['cnt'] if row else 0

    # ── Related products — same subcategory, same access, different slug ─
    related = db.execute("""
        SELECT p.id, p.slug, p.price, p.discount, p.image_file,
               p.rating, p.sales_count,
               COALESCE(pt.name, p.name) AS name
        FROM products p
        LEFT JOIN products_translations pt
               ON pt.product_id = p.id AND pt.lang_code = ?
        WHERE p.subcategory_id = (
                SELECT subcategory_id FROM products WHERE slug = ?
              )
          AND p.slug          != ?
          AND p.is_authorized  = (
                SELECT is_authorized FROM products WHERE slug = ?
              )
        ORDER BY p.sales_count DESC
        LIMIT 6
    """, (lang, slug, slug, slug)).fetchall()

    return render_template(
        'specific/specificproduct.html',
        product=product,
        product_images=product_images,
        brand_product_count=brand_product_count,
        related=related,
        currency=currency
    )


# ─────────────────────────────────────────
# RATING ENDPOINT  POST /api/rate
# ─────────────────────────────────────────

@api_bp.route('/api/rate', methods=['POST'])
def api_rate():
    """Submit a star rating for a product or service.

    Expects JSON:
        { "item_type": "product"|"service", "item_id": <int>, "rating": 1-5 }

    Rating calculation:
        new_avg = (current_rating * sales_count + user_rating) / (sales_count + 1)
        (uses sales_count as a proxy for total number of ratings)

    Returns:
        { "ok": true, "new_rating": <float> }
        { "ok": false, "error": "..." }
    """
    if not session.get('user_id'):
        return jsonify(ok=False, error='Not authenticated'), 401

    data = request.get_json(silent=True) or {}
    item_type = data.get('item_type')
    item_id = data.get('item_id')
    rating = data.get('rating')

    if item_type not in ('product', 'service'):
        return jsonify(ok=False, error='Invalid item_type'), 400
    if not item_id:
        return jsonify(ok=False, error='Missing item_id'), 400
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify(ok=False, error='Rating must be 1–5'), 400

    db = get_db()
    user_id = session['user_id']

    # ── Ensure product_ratings table exists (auto-migrate) ──────────
    db.execute("""
        CREATE TABLE IF NOT EXISTS product_ratings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            item_type  TEXT    NOT NULL CHECK (item_type IN ('product', 'service')),
            item_id    INTEGER NOT NULL,
            rating     INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            created_at TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE (user_id, item_type, item_id)
        )
    """)

    # ── Check for duplicate rating ───────────────────────────────────
    existing = db.execute(
        "SELECT id FROM product_ratings WHERE user_id=? AND item_type=? AND item_id=?",
        (user_id, item_type, int(item_id))
    ).fetchone()

    if existing:
        return jsonify(ok=False, error='already_rated'), 409

    # ── Fetch current aggregate values ──────────────────────────────
    table = 'products' if item_type == 'product' else 'services'
    row = db.execute(
        f"SELECT rating, sales_count FROM {table} WHERE id = ?",
        (int(item_id),)
    ).fetchone()

    if not row:
        return jsonify(ok=False, error='Item not found'), 404

    current_rating = row['rating'] or 0
    sales_count = row['sales_count'] or 0

    # Weighted average: treat sales_count as the proxy for how many people rated
    # new_avg = (current_avg * n + new_rating) / (n + 1)
    n = max(sales_count, 1)  # avoid div-by-zero if nothing sold yet
    new_rating = round((current_rating * n + rating) / (n + 1), 2)
    new_rating = min(5.0, max(0.0, new_rating))  # clamp to [0, 5]

    # ── Persist the rating row ───────────────────────────────────────
    db.execute(
        "INSERT INTO product_ratings (user_id, item_type, item_id, rating) VALUES (?,?,?,?)",
        (user_id, item_type, int(item_id), rating)
    )

    # ── Update aggregate rating on the product/service ──────────────
    db.execute(
        f"UPDATE {table} SET rating = ?, updated_at = datetime('now') WHERE id = ?",
        (new_rating, int(item_id))
    )

    db.commit()
    return jsonify(ok=True, new_rating=new_rating)
