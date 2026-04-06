"""
ArmsDealer — Services Blueprint
Routes: /api/services/*
"""
from flask import Blueprint, request, jsonify
from .database import get_db
from .auth import login_required, role_required

services_bp = Blueprint('services', __name__)


def _service_row(row):
    d = dict(row)
    if d.get('discount_pct', 0) > 0:
        d['discounted_price'] = round(d['price'] * (1 - d['discount_pct'] / 100), 2)
    else:
        d['discounted_price'] = d['price']
    return d


# ── LIST SERVICES ─────────────────────────────────────────────────────────────
@services_bp.route('/api/services', methods=['GET'])
def list_services():
    category      = request.args.get('category')
    featured_only = request.args.get('featured')
    search        = request.args.get('q', '').strip()

    sql    = "SELECT * FROM services WHERE is_active = 1"
    params = []

    if category:
        sql += " AND category = ?"
        params.append(category)
    if featured_only in ('1', 'true'):
        sql += " AND is_featured = 1"
    if search:
        sql += " AND (name LIKE ? OR description LIKE ? OR category LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like])

    sql += " ORDER BY is_featured DESC, price ASC"

    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return jsonify([_service_row(r) for r in rows])


# ── GET SINGLE SERVICE ────────────────────────────────────────────────────────
@services_bp.route('/api/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    db = get_db()
    row = db.execute("SELECT * FROM services WHERE id = ? AND is_active = 1", (service_id,)).fetchone()
    db.close()
    if not row:
        return jsonify({'error': 'Service not found'}), 404
    return jsonify(_service_row(row))


# ── CREATE SERVICE ────────────────────────────────────────────────────────────
@services_bp.route('/api/services', methods=['POST'])
@role_required('admin', 'developer')
def create_service():
    data = request.get_json() or {}
    if not data.get('name') or 'price' not in data:
        return jsonify({'error': 'Fields "name" and "price" are required'}), 400

    db = get_db()
    cur = db.execute(
        """INSERT INTO services
           (name, description, price, duration_days, category, is_featured, discount_pct)
           VALUES (?,?,?,?,?,?,?)""",
        (data['name'],
         data.get('description', ''),
         float(data['price']),
         data.get('duration_days'),
         data.get('category', ''),
         int(data.get('is_featured', 0)),
         float(data.get('discount_pct', 0)))
    )
    db.commit()
    new_id = cur.lastrowid
    row = db.execute("SELECT * FROM services WHERE id = ?", (new_id,)).fetchone()
    db.close()
    return jsonify(_service_row(row)), 201


# ── UPDATE SERVICE ────────────────────────────────────────────────────────────
@services_bp.route('/api/services/<int:service_id>', methods=['PUT'])
@role_required('admin', 'developer')
def update_service(service_id):
    data = request.get_json() or {}
    allowed = ['name', 'description', 'price', 'duration_days',
               'category', 'is_featured', 'is_active', 'discount_pct']
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400

    db = get_db()
    set_clause = ', '.join(f"{k} = ?" for k in updates)
    db.execute(
        f"UPDATE services SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
        list(updates.values()) + [service_id]
    )
    db.commit()
    row = db.execute("SELECT * FROM services WHERE id = ?", (service_id,)).fetchone()
    db.close()
    return jsonify(_service_row(row))


# ── DELETE SERVICE (soft) ─────────────────────────────────────────────────────
@services_bp.route('/api/services/<int:service_id>', methods=['DELETE'])
@role_required('admin')
def delete_service(service_id):
    db = get_db()
    db.execute(
        "UPDATE services SET is_active = 0, updated_at = datetime('now') WHERE id = ?",
        (service_id,)
    )
    db.commit()
    db.close()
    return jsonify({'message': 'Service removed'})


# ── CATEGORIES LIST ───────────────────────────────────────────────────────────
@services_bp.route('/api/services/categories', methods=['GET'])
def categories():
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT category FROM services WHERE is_active = 1 "
        "AND category IS NOT NULL AND category != '' ORDER BY category"
    ).fetchall()
    db.close()
    return jsonify([r['category'] for r in rows])
