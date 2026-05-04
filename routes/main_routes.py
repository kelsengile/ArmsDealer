# ──────────────────────────────────────────────────────────────────────────────────
# MAIN ROUTES
# ──────────────────────────────────────────────────────────────────────────────────
from flask import Blueprint, render_template, request, g
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
