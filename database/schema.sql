-- ─────────────────────────────────────────────────────────────────
-- ArmsDealer Database Schema
-- ─────────────────────────────────────────────────────────────────

PRAGMA foreign_keys = ON;

-- ─── USERS ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'customer',   -- 'customer' | 'admin'
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ─── CATEGORIES ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    slug        TEXT    NOT NULL UNIQUE,
    type        TEXT    NOT NULL DEFAULT 'product',     -- 'product' | 'service'
    icon_file   TEXT,                                   -- filename inside categoriesicons/
    description TEXT
);

-- ─── PRODUCTS ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    slug          TEXT    NOT NULL UNIQUE,
    category_id   INTEGER NOT NULL REFERENCES categories(id),
    description   TEXT,
    price         REAL    NOT NULL,
    sale_price    REAL,
    stock         INTEGER NOT NULL DEFAULT 0,
    image_file    TEXT,                                 -- filename inside productsimages/
    tags          TEXT,                                 -- JSON array string
    is_featured   INTEGER NOT NULL DEFAULT 0,           -- 0 | 1
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ─── SERVICES ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS services (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    slug          TEXT    NOT NULL UNIQUE,
    category_id   INTEGER NOT NULL REFERENCES categories(id),
    description   TEXT,
    price         REAL    NOT NULL,
    sale_price    REAL,
    image_file    TEXT,                                 -- filename inside serviceimages/
    tags          TEXT,
    is_featured   INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ─── ORDERS ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    status      TEXT    NOT NULL DEFAULT 'pending',     -- 'pending' | 'verified' | 'paid' | 'shipped' | 'completed' | 'cancelled'
    total       REAL    NOT NULL DEFAULT 0,
    notes       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ─── ORDER ITEMS ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    item_type   TEXT    NOT NULL DEFAULT 'product',     -- 'product' | 'service'
    item_id     INTEGER NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 1,
    unit_price  REAL    NOT NULL
);

-- ─── CART ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cart_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    item_type   TEXT    NOT NULL DEFAULT 'product',
    item_id     INTEGER NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 1,
    added_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, item_type, item_id)
);

-- ─── CONTACTS / INQUIRIES ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inquiries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    subject     TEXT,
    message     TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'new',            -- 'new' | 'read' | 'resolved'
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
