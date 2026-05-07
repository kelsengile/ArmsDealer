# ──────────────────────────────────────────────────────────────────────────────────
# CART & CHECKOUT ROUTES
# ──────────────────────────────────────────────────────────────────────────────────
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from db_helpers import get_db, get_currency

cart_bp = Blueprint('cart', __name__)


# ─────────────────────────────────────────
# ADD TO CART (POST /api/cart/add)
# ─────────────────────────────────────────

@cart_bp.route('/api/cart/add', methods=['POST'])
def api_cart_add():
    """Add a product (or service) to the current user's cart.

    Expects JSON body:
        { "item_type": "product", "item_id": <int>, "quantity": <int> }

    Returns JSON:
        { "ok": true, "cart_count": <int> }   on success
        { "ok": false, "error": "..." }        on failure
    """
    if not session.get('user_id'):
        return jsonify(ok=False, error='Not authenticated'), 401

    data = request.get_json(silent=True) or {}
    item_type = data.get('item_type', 'product')
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))

    if item_type not in ('product', 'service'):
        return jsonify(ok=False, error='Invalid item_type'), 400
    if not item_id:
        return jsonify(ok=False, error='Missing item_id'), 400
    if quantity < 1:
        quantity = 1

    db = get_db()
    user_id = session['user_id']

    # Verify the item exists
    if item_type == 'product':
        item = db.execute(
            'SELECT id FROM products WHERE id = ?', (item_id,)).fetchone()
    else:
        item = db.execute(
            'SELECT id FROM services WHERE id = ?', (item_id,)).fetchone()

    if not item:
        return jsonify(ok=False, error='Item not found'), 404

    # Upsert: if already in cart, increment quantity; otherwise insert
    existing = db.execute(
        'SELECT id, quantity FROM cart_items WHERE user_id = ? AND item_type = ? AND item_id = ?',
        (user_id, item_type, item_id)
    ).fetchone()

    if existing:
        new_qty = existing['quantity'] + quantity
        db.execute(
            'UPDATE cart_items SET quantity = ? WHERE id = ?',
            (new_qty, existing['id'])
        )
    else:
        db.execute(
            'INSERT INTO cart_items (user_id, item_type, item_id, quantity) VALUES (?, ?, ?, ?)',
            (user_id, item_type, item_id, quantity)
        )

    db.commit()

    # Return fresh cart count for this user
    row = db.execute(
        'SELECT COALESCE(SUM(quantity), 0) AS cnt FROM cart_items WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    cart_count = int(row['cnt']) if row else 0

    # Keep session in sync
    session['cart_count'] = cart_count

    return jsonify(ok=True, cart_count=cart_count)


# ─────────────────────────────────────────
# CHECKOUT PAGE (GET)
# ─────────────────────────────────────────

@cart_bp.route('/checkout')
def checkout():
    """Checkout page — shows cart items and cost breakdown."""
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    db = get_db()
    user_id = session['user_id']
    currency = get_currency(db)

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
            END AS image_file
        FROM cart_items ci
        LEFT JOIN products p ON ci.item_type = 'product' AND ci.item_id = p.id
        LEFT JOIN services s ON ci.item_type = 'service' AND ci.item_id = s.id
        WHERE ci.user_id = ?
        ORDER BY ci.id DESC
    """, (user_id,)).fetchall()

    cart_items = [dict(row) for row in cart_rows]
    cart_total_php = sum((item['price'] or 0) * item['quantity']
                         for item in cart_items)

    rate = currency['rate_to_php'] if currency else 1
    for item in cart_items:
        item['price'] = round((item['price'] or 0) * rate)
    cart_total = round(cart_total_php * rate)

    return render_template(
        'user/checkout.html',
        cart_items=cart_items,
        cart_total=cart_total,
        currency=currency
    )


# ─────────────────────────────────────────
# PLACE ORDER (POST)
# ─────────────────────────────────────────

@cart_bp.route('/checkout/place', methods=['POST'])
def place_order():
    """Convert cart to an order, clear cart, redirect to orders shipping tab."""
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))

    db = get_db()
    user_id = session['user_id']

    cart_rows = db.execute("""
        SELECT
            ci.item_type,
            ci.item_id,
            ci.quantity,
            CASE
                WHEN ci.item_type = 'product' THEN p.price
                WHEN ci.item_type = 'service' THEN s.price
            END AS price
        FROM cart_items ci
        LEFT JOIN products p ON ci.item_type = 'product' AND ci.item_id = p.id
        LEFT JOIN services s ON ci.item_type = 'service' AND ci.item_id = s.id
        WHERE ci.user_id = ?
    """, (user_id,)).fetchall()

    if not cart_rows:
        return redirect(url_for('main.orders'))

    total = sum((row['price'] or 0) * row['quantity'] for row in cart_rows)

    # Create the order with initial status 'order placed'
    cursor = db.execute(
        "INSERT INTO orders (user_id, status, total) VALUES (?, 'order placed', ?)",
        (user_id, total)
    )
    db.commit()
    order_id = cursor.lastrowid

    # Insert order items
    for row in cart_rows:
        db.execute(
            """INSERT INTO order_items (order_id, item_type, item_id, quantity, unit_price)
               VALUES (?, ?, ?, ?, ?)""",
            (order_id, row['item_type'], row['item_id'],
             row['quantity'], row['price'] or 0)
        )

    # Clear the cart
    db.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))
    db.commit()

    # ── Keep session in sync so every page reflects the empty cart ──
    session['cart_count'] = 0

    return redirect(url_for('main.orders') + '?tab=shipping')


# ─────────────────────────────────────────
# ADMIN — UPDATE ORDER STATUS (POST /admin/order/<id>/status)
# ─────────────────────────────────────────

@cart_bp.route('/admin/order/<int:order_id>/status', methods=['POST'])
def admin_update_order_status(order_id):
    """Admin API to update order status. Returns JSON."""
    if not session.get('user_id'):
        return jsonify(ok=False, error='Not authenticated'), 401
    if session.get('role') != 'admin':
        return jsonify(ok=False, error='Forbidden'), 403

    data = request.get_json(silent=True) or {}
    status = data.get('status', '').strip().lower()
    valid = {'order placed', 'packing', 'shipping', 'delivered'}
    if status not in valid:
        return jsonify(ok=False, error='Invalid status'), 400

    db = get_db()
    db.execute(
        "UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (status, order_id)
    )
    db.commit()
    return jsonify(ok=True, status=status)
