"""
ArmsDealer — Flask Application Factory
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from .database import init_db
from .routes_users    import users_bp
from .routes_products import products_bp
from .routes_services import services_bp
from .routes_orders   import orders_bp


def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'),
    )

    # ── Config ────────────────────────────────────────────────────────────────
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'armsdealer-dev-secret-change-in-prod'),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=86400 * 7,  # 7 days
    )

    # ── CORS (allow frontend dev server) ──────────────────────────────────────
    CORS(app, supports_credentials=True, origins=[
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5500',
        'http://127.0.0.1:5500',
    ])

    # ── Initialize DB ─────────────────────────────────────────────────────────
    with app.app_context():
        init_db()

    # ── Register Blueprints ───────────────────────────────────────────────────
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(orders_bp)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'app': 'ArmsDealer API'})

    # ── Generic error handlers ────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app
