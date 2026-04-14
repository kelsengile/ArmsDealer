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
    discount      REAL    DEFAULT 0,
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
    discount      REAL    DEFAULT 0,
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



-- ─── Language and Currency ─────────────────────────────────────────────────────

-- ─── LANGUAGES ───────────────────────────────────────────────────
-- Source of truth for supported locales.
-- lang_code matches your JS translations object keys exactly.
CREATE TABLE IF NOT EXISTS languages (
    code        TEXT    PRIMARY KEY,               -- 'english', 'filipino', 'japanese', etc.
    label       TEXT    NOT NULL,                  -- 'English', 'Filipino', displayed in <select>
    locale      TEXT    NOT NULL,                  -- 'en', 'fil', 'ja' — for html lang attr
    is_active   INTEGER NOT NULL DEFAULT 1,
    sort_order  INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO languages (code, label, locale, sort_order) VALUES
    ('english',  'English',  'en',  1),
    ('filipino', 'Filipino', 'fil', 2),
    ('japanese', 'Japanese', 'ja',  3),
    ('spanish',  'Spanish',  'es',  4),
    ('mandarin', 'Mandarin', 'zh',  5);


-- ─── PRODUCT TRANSLATIONS ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS product_translations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    lang_code   TEXT    NOT NULL REFERENCES languages(code),
    name        TEXT    NOT NULL,
    description TEXT,
    tags        TEXT,                              -- translated JSON tag array, e.g. '["Sniper","Bolt-action"]'
    UNIQUE (product_id, lang_code)
);


-- ─── SERVICE TRANSLATIONS ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS service_translations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id  INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    lang_code   TEXT    NOT NULL REFERENCES languages(code),
    name        TEXT    NOT NULL,
    description TEXT,
    tags        TEXT,
    UNIQUE (service_id, lang_code)
);


-- ─── CATEGORY TRANSLATIONS ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS category_translations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    lang_code   TEXT    NOT NULL REFERENCES languages(code),
    name        TEXT    NOT NULL,
    description TEXT,
    UNIQUE (category_id, lang_code)
);


-- ─── CURRENCIES ──────────────────────────────────────────────────
-- PHP is your base; all rates are PHP → foreign.
-- Update rate_to_php periodically from an exchange rate API.
CREATE TABLE IF NOT EXISTS currencies (
    code        TEXT    PRIMARY KEY,               -- 'PHP', 'USD', 'EUR'
    symbol      TEXT    NOT NULL,                  -- '₱', '$', '€'
    label       TEXT    NOT NULL,                  -- 'PHP (₱)', shown in <select>
    rate_to_php REAL    NOT NULL DEFAULT 1.0,      -- 1 PHP = X of this currency
    is_active   INTEGER NOT NULL DEFAULT 1,
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO currencies (code, symbol, label, rate_to_php) VALUES
    ('PHP', '₱', 'PHP (₱)', 1.0),
    ('USD', '$', 'USD ($)', 0.0175),              -- update regularly
    ('EUR', '€', 'EUR (€)', 0.0162);


-- ─── UI STRINGS (optional DB override) ───────────────────────────
-- Lets you edit navbar/homepage copy from an admin panel
-- without touching translations.js. Your JS file stays
-- as the fallback; rows here take priority at render time.
CREATE TABLE IF NOT EXISTS ui_strings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lang_code   TEXT    NOT NULL REFERENCES languages(code),
    key         TEXT    NOT NULL,                  -- matches data-translate values, e.g. 'navbarproducts'
    value       TEXT    NOT NULL,
    UNIQUE (lang_code, key)
);

CREATE INDEX IF NOT EXISTS idx_ui_strings_lang ON ui_strings (lang_code);