"""
ArmsDealer — Cart & Orders Blueprint
Routes: /api/cart/* and /api/orders/*
"""
from flask import Blueprint, request, jsonify, session
from .database import get_db
from .auth import login_required, role_required

orders_bp = Blueprint('orders', __name__)


# ══════════════════════════════════════════════════════════════════════════════
# CART
# ══════════════════════════════════════════════════════════════════════════════

def _enrich_cart(items, db):
    """Add name, price, discounted_price to each cart item."""
    enriched = []
    for item in items:
        d = dict(item)
        if d['item_type'] == 'product':
            row = db.execute(
                "SELECT name, price, discount_pct FROM products WHERE id = ?", (d['item_id'],)
            ).fetchone()
        else:
            row = db.execute(
                "SELECT name, price, discount_pct FROM services WHERE id = ?", (d['item_id'],)
            ).fetchone()

        if row:
            disc = row['discount_pct'] or 0
            unit_price = round(row['price'] * (1 - disc / 100), 2)
            d.update({
                'name':        row['name'],
                'unit_price':  unit_price,
                'line_total':  round(unit_price * d['quantity'], 2),
            })
        enriched.append(d)
    return enriched


@orders_bp.route('/api/cart', methods=['GET'])
@login_required
def get_cart():
    db   = get_db()
    items = db.execute(
        "SELECT * FROM cart_items WHERE user_id = ? ORDER BY added_at DESC",
        (session['user_id'],)
    ).fetchall()
    enriched = _enrich_cart(items, db)
    grand_total = sum(i.get('line_total', 0) for i in enriched)
    db.close()
    return jsonify({'items': enriched, 'grand_total': round(grand_total, 2)})


@orders_bp.route('/api/cart', methods=['POST'])
@login_required
def add_to_cart():
    data      = request.get_json() or {}
    item_type = data.get('item_type')
    item_id   = data.get('item_id')
    quantity  = int(data.get('quantity', 1))

    if item_type not in ('product', 'service') or not item_id:
        return jsonify({'error': 'item_type (product|service) and item_id required'}), 400
    if quantity < 1:
        return jsonify({'error': 'quantity must be ≥ 1'}), 400

    db = get_db()
    existing = db.execute(
        "SELECT id, quantity FROM cart_items WHERE user_id=? AND item_type=? AND item_id=?",
        (session['user_id'], item_type, item_id)
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE cart_items SET quantity = quantity + ? WHERE id = ?",
            (quantity, existing['id'])
        )
    else:
        db.execute(
            "INSERT INTO cart_items (user_id, item_type, item_id, quantity) VALUES (?,?,?,?)",
            (session['user_id'], item_type, item_id, quantity)
        )
    db.commit()
    db.close()
    return jsonify({'message': 'Item added to cart'}), 201


@orders_bp.route('/api/cart/<int:cart_item_id>', methods=['PUT'])
@login_required
def update_cart_item(cart_item_id):
    data     = request.get_json() or {}
    quantity = int(data.get('quantity', 1))

    if quantity < 1:
        return jsonify({'error': 'quantity must be ≥ 1'}), 400

    db = get_db()
    db.execute(
        "UPDATE cart_items SET quantity = ? WHERE id = ? AND user_id = ?",
        (quantity, cart_item_id, session['user_id'])
    )
    db.commit()
    db.close()
    return jsonify({'message': 'Cart updated'})


@orders_bp.route('/api/cart/<int:cart_item_id>', methods=['DELETE'])
@login_required
def remove_cart_item(cart_item_id):
    db = get_db()
    db.execute(
        "DELETE FROM cart_items WHERE id = ? AND user_id = ?",
        (cart_item_id, session['user_id'])
    )
    db.commit()
    db.close()
    return jsonify({'message': 'Item removed from cart'})


@orders_bp.route('/api/cart/clear', methods=['DELETE'])
@login_required
def clear_cart():
    db = get_db()
    db.execute("DELETE FROM cart_items WHERE user_id = ?", (session['user_id'],))
    db.commit()
    db.close()
    return jsonify({'message': 'Cart cleared'})


# ══════════════════════════════════════════════════════════════════════════════
# ORDERS
# ══════════════════════════════════════════════════════════════════════════════

@orders_bp.route('/api/orders', methods=['POST'])
@login_required
def place_order():
    """Convert current cart into an order."""
    data = request.get_json() or {}
    db   = get_db()

    cart_items = db.execute(
        "SELECT * FROM cart_items WHERE user_id = ?",
        (session['user_id'],)
    ).fetchall()

    if not cart_items:
        db.close()
        return jsonify({'error': 'Cart is empty'}), 400

    enriched    = _enrich_cart(cart_items, db)
    grand_total = sum(i.get('line_total', 0) for i in enriched)

    # Create order
    cur = db.execute(
        """INSERT INTO orders (user_id, total_amount, shipping_address, notes)
           VALUES (?,?,?,?)""",
        (session['user_id'], grand_total,
         data.get('shipping_address', ''),
         data.get('notes', ''))
    )
    order_id = cur.lastrowid

    # Create order items
    for item in enriched:
        db.execute(
            """INSERT INTO order_items
               (order_id, item_type, item_id, item_name, unit_price, quantity)
               VALUES (?,?,?,?,?,?)""",
            (order_id, item['item_type'], item['item_id'],
             item.get('name', 'Unknown'), item.get('unit_price', 0), item['quantity'])
        )

    # Clear the cart
    db.execute("DELETE FROM cart_items WHERE user_id = ?", (session['user_id'],))
    db.commit()
    db.close()

    return jsonify({
        'message': 'Order placed successfully',
        'order_id': order_id,
        'total':    grand_total
    }), 201


@orders_bp.route('/api/orders', methods=['GET'])
@login_required
def list_orders():
    db     = get_db()
    user_type = session.get('user_type', 'user')

    if user_type in ('admin', 'developer'):
        rows = db.execute(
            "SELECT o.*, u.username FROM orders o "
            "JOIN users u ON o.user_id = u.id ORDER BY o.created_at DESC"
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
            (session['user_id'],)
        ).fetchall()

    db.close()
    return jsonify([dict(r) for r in rows])


@orders_bp.route('/api/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

    if not order:
        db.close()
        return jsonify({'error': 'Order not found'}), 404

    # Non-admins can only see their own orders
    if session.get('user_type') not in ('admin', 'developer') \
            and order['user_id'] != session['user_id']:
        db.close()
        return jsonify({'error': 'Forbidden'}), 403

    items = db.execute(
        "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
    ).fetchall()
    db.close()

    result = dict(order)
    result['items'] = [dict(i) for i in items]
    return jsonify(result)


@orders_bp.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@role_required('admin', 'developer')
def update_order_status(order_id):
    data   = request.get_json() or {}
    status = data.get('status')
    valid  = ('pending', 'verified', 'processing', 'shipped', 'delivered', 'cancelled')

    if status not in valid:
        return jsonify({'error': f'status must be one of {valid}'}), 400

    db = get_db()
    db.execute(
        "UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (status, order_id)
    )
    db.commit()
    db.close()
    return jsonify({'message': f'Order status updated to "{status}"'})
