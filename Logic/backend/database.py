"""
ArmsDealer — Database Schema & Initialization
SQLite via Python's built-in sqlite3
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'armsdealer.db')


def get_db():
    """Return a database connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist, then seed demo data."""
    conn = get_db()
    cur = conn.cursor()

    # ── USERS ─────────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            user_type     TEXT    NOT NULL DEFAULT 'user'
                              CHECK(user_type IN ('admin','developer','user')),
            first_name    TEXT,
            last_name     TEXT,
            phone         TEXT,
            address       TEXT,
            is_active     INTEGER NOT NULL DEFAULT 1,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── PRODUCTS ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            description   TEXT,
            price         REAL    NOT NULL CHECK(price >= 0),
            stock         INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
            category_type TEXT    NOT NULL DEFAULT 'weapon'
                              CHECK(category_type IN ('weapon','equipment')),
            subcategory   TEXT,
            caliber       TEXT,
            brand         TEXT,
            model         TEXT,
            image_url     TEXT,
            discount_pct  REAL    NOT NULL DEFAULT 0 CHECK(discount_pct BETWEEN 0 AND 100),
            is_featured   INTEGER NOT NULL DEFAULT 0,
            is_active     INTEGER NOT NULL DEFAULT 1,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── SERVICES ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            description   TEXT,
            price         REAL    NOT NULL CHECK(price >= 0),
            duration_days INTEGER,
            category      TEXT,
            is_featured   INTEGER NOT NULL DEFAULT 0,
            is_active     INTEGER NOT NULL DEFAULT 1,
            discount_pct  REAL    NOT NULL DEFAULT 0 CHECK(discount_pct BETWEEN 0 AND 100),
            created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── CART ──────────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            item_type    TEXT    NOT NULL CHECK(item_type IN ('product','service')),
            item_id      INTEGER NOT NULL,
            quantity     INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
            added_at     TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── ORDERS ────────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id),
            status          TEXT    NOT NULL DEFAULT 'pending'
                                CHECK(status IN ('pending','verified','processing',
                                                 'shipped','delivered','cancelled')),
            total_amount    REAL    NOT NULL DEFAULT 0,
            shipping_address TEXT,
            notes           TEXT,
            created_at      TEXT   NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT   NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            item_type   TEXT    NOT NULL CHECK(item_type IN ('product','service')),
            item_id     INTEGER NOT NULL,
            item_name   TEXT    NOT NULL,
            unit_price  REAL    NOT NULL,
            quantity    INTEGER NOT NULL DEFAULT 1
        )
    """)

    # ── COMPLIANCE / VERIFICATION ─────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS compliance_verifications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            order_id    INTEGER REFERENCES orders(id),
            status      TEXT NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','approved','rejected')),
            document_url TEXT,
            notes       TEXT,
            reviewed_by INTEGER REFERENCES users(id),
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    conn.commit()

    # ── SEED DEMO DATA (only if tables are empty) ─────────────────────────────
    _seed_demo_data(cur, conn)

    conn.close()
    print(f"[DB] Database initialized at: {os.path.abspath(DB_PATH)}")


def _seed_demo_data(cur, conn):
    """Insert demo rows so the API returns something immediately."""
    from werkzeug.security import generate_password_hash

    # Users
    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ('admin',     'admin@armsdealer.com',     generate_password_hash('Admin@1234'),     'admin',     'Admin',  'User'),
            ('devuser',   'dev@armsdealer.com',       generate_password_hash('Dev@1234'),       'developer', 'Dev',    'User'),
            ('johndoe',   'john@example.com',         generate_password_hash('User@1234'),      'user',      'John',   'Doe'),
        ]
        cur.executemany(
            "INSERT INTO users (username, email, password_hash, user_type, first_name, last_name) VALUES (?,?,?,?,?,?)",
            users
        )

    # Products
    if cur.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            ('M4A1 Carbine — Tactical Edition',
             'Semi-automatic 5.56mm carbine. Cold-hammer-forged barrel, M-LOK handguard, mil-spec trigger group. Trusted in over 80 military forces worldwide.',
             138750, 12, 'weapon', 'Firearms', '5.56mm', 'Colt', 'M4A1',
             '/assets/images/m4a1.jpg', 25, 1),
            ('SR-25 Precision Rifle',
             '7.62mm semi-auto marksman rifle. Match-grade stainless barrel, adjustable stock, Picatinny rail system. Effective range: 800m.',
             195500, 5, 'weapon', 'Firearms', '7.62mm', 'Knight Armament', 'SR-25',
             '/assets/images/sr25.jpg', 15, 1),
            ('AK-103 Assault Rifle',
             '7.62x39mm battle-proven platform. Side-folding stock, chrome-lined barrel, enhanced pistol grip.',
             115000, 8, 'weapon', 'Firearms', '7.62x39mm', 'Kalashnikov', 'AK-103',
             '/assets/images/ak103.jpg', 21, 1),
            ('Glock 17 Gen5',
             '9mm striker-fired duty pistol. Marksman barrel, flared mag well, ambidextrous slide stop.',
             54400, 20, 'weapon', 'Handguns', '9mm', 'Glock', 'G17 Gen5',
             '/assets/images/glock17.jpg', 20, 1),
            ('SIG P320 Compact',
             '9mm modular pistol system. Serialized fire control unit, interchangeable grip modules. US Army M17 basis.',
             72000, 15, 'weapon', 'Handguns', '9mm', 'SIG Sauer', 'P320',
             '/assets/images/sigp320.jpg', 12, 0),
            ('5.56mm NATO — 1,000 Round Case',
             'M855 62gr green-tip penetrator. Lake City production, mil-spec brass, boxer-primed.',
             13875, 50, 'equipment', 'Ammunition', '5.56mm NATO', 'Lake City', 'M855',
             '/assets/images/556ammo.jpg', 25, 1),
            ('9mm FMJ — 500 Round Box',
             '124gr full metal jacket 9mm. Reloadable brass, consistent velocity, clean-burning powder.',
             5270, 80, 'equipment', 'Ammunition', '9mm', 'Federal', 'FMJ124',
             '/assets/images/9mmfmj.jpg', 15, 0),
            ('Plate Carrier — Level IV MOLLE',
             'Certified Level IV ballistic protection. MOLLE webbing, cummerbund, quick-release system.',
             33600, 10, 'equipment', 'Protective', None, 'Crye Precision', 'JPC 2.0',
             '/assets/images/platecarrier.jpg', 20, 1),
        ]
        cur.executemany(
            """INSERT INTO products
               (name, description, price, stock, category_type, subcategory,
                caliber, brand, model, image_url, discount_pct, is_featured)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            products
        )

    # Services
    if cur.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
        services = [
            ('Full Gunsmith Overhaul',
             'Complete weapon inspection, deep clean, barrel crown recutting, trigger job, parts replacement, test fire report.',
             9600, 3, 'Gunsmithing', 1, 20),
            ('Custom Cerakote Refinish',
             'Mil-spec Cerakote application in any color or camo pattern. Surface prep, bead blast, cure. Rated to 1,200°F.',
             6400, 5, 'Customization', 1, 20),
            ('Optics Mounting & Zero Service',
             'Professional scope mounting, torque to spec, lapping, and 100m zeroing session on our range.',
             3375, 1, 'Customization', 0, 25),
            ('Compliance Consultation',
             'One-on-one session with our legal team to review permits, licensing requirements, and purchase compliance.',
             4500, 1, 'Legal', 0, 0),
            ('Secure Weapons Storage (Monthly)',
             'Climate-controlled vault storage with 24/7 CCTV monitoring. Per-firearm monthly rate.',
             2500, None, 'Storage', 0, 0),
        ]
        cur.executemany(
            """INSERT INTO services
               (name, description, price, duration_days, category, is_featured, discount_pct)
               VALUES (?,?,?,?,?,?,?)""",
            services
        )

    conn.commit()
