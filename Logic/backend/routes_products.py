"""
ArmsDealer — Products Blueprint
Routes: /api/products/*
"""
from flask import Blueprint, request, jsonify
from .database import get_db
from .auth import login_required, role_required

products_bp = Blueprint('products', __name__)


def _product_row(row):
    d = dict(row)
    if d.get('discount_pct', 0) > 0:
        d['discounted_price'] = round(d['price'] * (1 - d['discount_pct'] / 100), 2)
    else:
        d['discounted_price'] = d['price']
    return d


# ── LIST / SEARCH PRODUCTS ────────────────────────────────────────────────────
@products_bp.route('/api/products', methods=['GET'])
def list_products():
    category_type = request.args.get('type')          # weapon | equipment
    subcategory   = request.args.get('subcategory')
    featured_only = request.args.get('featured')       # "1" or "true"
    search        = request.args.get('q', '').strip()
    limit         = min(int(request.args.get('limit', 50)), 100)
    offset        = int(request.args.get('offset', 0))

    sql    = "SELECT * FROM products WHERE is_active = 1"
    params = []

    if category_type:
        sql += " AND category_type = ?"
        params.append(category_type)
    if subcategory:
        sql += " AND subcategory = ?"
        params.append(subcategory)
    if featured_only in ('1', 'true'):
        sql += " AND is_featured = 1"
    if search:
        sql += " AND (name LIKE ? OR description LIKE ? OR brand LIKE ? OR subcategory LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like, like])

    sql += " ORDER BY is_featured DESC, created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    db = get_db()
    rows = db.execute(sql, params).fetchall()
    total = db.execute(
        "SELECT COUNT(*) FROM products WHERE is_active = 1"
    ).fetchone()[0]
    db.close()

    return jsonify({
        'items': [_product_row(r) for r in rows],
        'total': total,
        'limit': limit,
        'offset': offset
    })


# ── GET SINGLE PRODUCT ────────────────────────────────────────────────────────
@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    db = get_db()
    row = db.execute("SELECT * FROM products WHERE id = ? AND is_active = 1", (product_id,)).fetchone()
    db.close()
    if not row:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(_product_row(row))


# ── CREATE PRODUCT (admin/dev) ────────────────────────────────────────────────
@products_bp.route('/api/products', methods=['POST'])
@role_required('admin', 'developer')
def create_product():
    data = request.get_json() or {}
    required = ['name', 'price', 'category_type']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Field "{field}" is required'}), 400

    if data['category_type'] not in ('weapon', 'equipment'):
        return jsonify({'error': 'category_type must be "weapon" or "equipment"'}), 400

    db = get_db()
    cur = db.execute(
        """INSERT INTO products
           (name, description, price, stock, category_type, subcategory,
            caliber, brand, model, image_url, discount_pct, is_featured)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (data['name'],
         data.get('description', ''),
         float(data['price']),
         int(data.get('stock', 0)),
         data['category_type'],
         data.get('subcategory', ''),
         data.get('caliber', ''),
         data.get('brand', ''),
         data.get('model', ''),
         data.get('image_url', ''),
         float(data.get('discount_pct', 0)),
         int(data.get('is_featured', 0)))
    )
    db.commit()
    new_id = cur.lastrowid
    row = db.execute("SELECT * FROM products WHERE id = ?", (new_id,)).fetchone()
    db.close()
    return jsonify(_product_row(row)), 201


# ── UPDATE PRODUCT ────────────────────────────────────────────────────────────
@products_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@role_required('admin', 'developer')
def update_product(product_id):
    data = request.get_json() or {}
    allowed = ['name', 'description', 'price', 'stock', 'category_type',
               'subcategory', 'caliber', 'brand', 'model', 'image_url',
               'discount_pct', 'is_featured', 'is_active']
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400

    db = get_db()
    set_clause = ', '.join(f"{k} = ?" for k in updates)
    db.execute(
        f"UPDATE products SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
        list(updates.values()) + [product_id]
    )
    db.commit()
    row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    db.close()
    if not row:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(_product_row(row))


# ── DELETE PRODUCT (soft-delete) ──────────────────────────────────────────────
@products_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@role_required('admin')
def delete_product(product_id):
    db = get_db()
    db.execute(
        "UPDATE products SET is_active = 0, updated_at = datetime('now') WHERE id = ?",
        (product_id,)
    )
    db.commit()
    db.close()
    return jsonify({'message': 'Product removed'})


# ── SUBCATEGORY LIST ──────────────────────────────────────────────────────────
@products_bp.route('/api/products/subcategories', methods=['GET'])
def subcategories():
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT subcategory, category_type FROM products "
        "WHERE is_active = 1 AND subcategory IS NOT NULL AND subcategory != '' "
        "ORDER BY category_type, subcategory"
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])
