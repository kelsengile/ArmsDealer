# ──────────────────────────────────────────────────────────────────────────────────
# MODELS
# ──────────────────────────────────────────────────────────────────────────────────
import sqlite3
import os
from app import get_db
# ─────────────────────────────────────────
# USER
# ─────────────────────────────────────────


class User:
    @staticmethod
    def get_by_id(user_id: int):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    @staticmethod
    def get_by_email(email: str):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    @staticmethod
    def get_by_username(username: str):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    @staticmethod
    def create(username: str, email: str, password_hash: str, role: str = 'customer'):
        db = get_db()
        db.execute(
            'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, role)
        )
        db.commit()
# ─────────────────────────────────────────
# CATEGORY
# ─────────────────────────────────────────


class Category:
    @staticmethod
    def get_all(type_filter: str = None):
        db = get_db()
        if type_filter:
            return db.execute('SELECT * FROM categories WHERE type = ?', (type_filter,)).fetchall()
        return db.execute('SELECT * FROM categories').fetchall()

    @staticmethod
    def get_by_slug(slug: str):
        db = get_db()
        return db.execute('SELECT * FROM categories WHERE slug = ?', (slug,)).fetchone()
# ─────────────────────────────────────────
# PRODUCT
# ─────────────────────────────────────────


class Product:
    @staticmethod
    def get_all(category_id: int = None, featured_only: bool = False):
        db = get_db()
        query = 'SELECT * FROM products WHERE 1=1'
        params = []
        if category_id:
            query += ' AND category_id = ?'
            params.append(category_id)
        if featured_only:
            query += ' AND is_featured = 1'
        return db.execute(query, params).fetchall()

    @staticmethod
    def get_by_id(product_id: int):
        db = get_db()
        return db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

    @staticmethod
    def get_by_slug(slug: str):
        db = get_db()
        return db.execute('SELECT * FROM products WHERE slug = ?', (slug,)).fetchone()

    @staticmethod
    def get_featured():
        return Product.get_all(featured_only=True)
# ─────────────────────────────────────────
# SERVICE
# ─────────────────────────────────────────


class Service:
    @staticmethod
    def get_all(category_id: int = None, featured_only: bool = False):
        db = get_db()
        query = 'SELECT * FROM services WHERE 1=1'
        params = []
        if category_id:
            query += ' AND category_id = ?'
            params.append(category_id)
        if featured_only:
            query += ' AND is_featured = 1'
        return db.execute(query, params).fetchall()

    @staticmethod
    def get_by_id(service_id: int):
        db = get_db()
        return db.execute('SELECT * FROM services WHERE id = ?', (service_id,)).fetchone()

    @staticmethod
    def get_featured():
        return Service.get_all(featured_only=True)
# ─────────────────────────────────────────
# ORDER
# ─────────────────────────────────────────


class Order:
    @staticmethod
    def get_by_user(user_id: int):
        db = get_db()
        return db.execute(
            'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC', (
                user_id,)
        ).fetchall()

    @staticmethod
    def create(user_id: int, total: float = 0):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO orders (user_id, total) VALUES (?, ?)', (user_id, total)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update_status(order_id: int, status: str):
        db = get_db()
        db.execute(
            "UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, order_id)
        )
        db.commit()
# ─────────────────────────────────────────
# CART
# ─────────────────────────────────────────


class Cart:
    @staticmethod
    def get_items(user_id: int):
        db = get_db()
        return db.execute(
            'SELECT * FROM cart_items WHERE user_id = ?', (user_id,)
        ).fetchall()

    @staticmethod
    def add_item(user_id: int, item_type: str, item_id: int, quantity: int = 1):
        db = get_db()
        db.execute(
            '''INSERT INTO cart_items (user_id, item_type, item_id, quantity)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, item_type, item_id)
               DO UPDATE SET quantity = quantity + excluded.quantity''',
            (user_id, item_type, item_id, quantity)
        )
        db.commit()

    @staticmethod
    def remove_item(user_id: int, item_type: str, item_id: int):
        db = get_db()
        db.execute(
            'DELETE FROM cart_items WHERE user_id = ? AND item_type = ? AND item_id = ?',
            (user_id, item_type, item_id)
        )
        db.commit()

    @staticmethod
    def clear(user_id: int):
        db = get_db()
        db.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))
        db.commit()
# ─────────────────────────────────────────
# INQUIRY
# ─────────────────────────────────────────


class Inquiry:
    @staticmethod
    def create(name: str, email: str, subject: str, message: str):
        db = get_db()
        db.execute(
            'INSERT INTO inquiries (name, email, subject, message) VALUES (?, ?, ?, ?)',
            (name, email, subject, message)
        )
        db.commit()

    @staticmethod
    def get_all():
        db = get_db()
        return db.execute('SELECT * FROM inquiries ORDER BY created_at DESC').fetchall()
