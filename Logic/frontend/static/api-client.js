/**
 * ArmsDealer — API Client
 * Drop this script into any page to talk to the Flask backend.
 * Usage: import or include before your page scripts.
 */

const API_BASE = 'http://localhost:5000';

const Api = {

    _fetch(method, path, body = null) {
        const opts = {
            method,
            credentials: 'include',        // send session cookie
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) opts.body = JSON.stringify(body);
        return fetch(API_BASE + path, opts).then(async res => {
            const data = await res.json();
            if (!res.ok) throw { status: res.status, ...data };
            return data;
        });
    },

    get:    (path)        => Api._fetch('GET',    path),
    post:   (path, body)  => Api._fetch('POST',   path, body),
    put:    (path, body)  => Api._fetch('PUT',    path, body),
    delete: (path)        => Api._fetch('DELETE', path),

    // ── AUTH ────────────────────────────────────────────────────────────────
    auth: {
        register:       (data)    => Api.post('/api/auth/register', data),
        login:          (data)    => Api.post('/api/auth/login', data),
        logout:         ()        => Api.post('/api/auth/logout'),
        me:             ()        => Api.get('/api/auth/me'),
        updateProfile:  (data)    => Api.put('/api/auth/me', data),
        changePassword: (data)    => Api.post('/api/auth/change-password', data),
    },

    // ── PRODUCTS ────────────────────────────────────────────────────────────
    products: {
        list:   (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return Api.get(`/api/products${qs ? '?' + qs : ''}`);
        },
        get:    (id)   => Api.get(`/api/products/${id}`),
        create: (data) => Api.post('/api/products', data),
        update: (id, data) => Api.put(`/api/products/${id}`, data),
        delete: (id)   => Api.delete(`/api/products/${id}`),
        subcategories: () => Api.get('/api/products/subcategories'),
    },

    // ── SERVICES ────────────────────────────────────────────────────────────
    services: {
        list:   (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return Api.get(`/api/services${qs ? '?' + qs : ''}`);
        },
        get:    (id)   => Api.get(`/api/services/${id}`),
        create: (data) => Api.post('/api/services', data),
        update: (id, data) => Api.put(`/api/services/${id}`, data),
        delete: (id)   => Api.delete(`/api/services/${id}`),
        categories: () => Api.get('/api/services/categories'),
    },

    // ── CART ────────────────────────────────────────────────────────────────
    cart: {
        get:    ()          => Api.get('/api/cart'),
        add:    (data)      => Api.post('/api/cart', data),
        update: (id, qty)   => Api.put(`/api/cart/${id}`, { quantity: qty }),
        remove: (id)        => Api.delete(`/api/cart/${id}`),
        clear:  ()          => Api.delete('/api/cart/clear'),
    },

    // ── ORDERS ──────────────────────────────────────────────────────────────
    orders: {
        place:        (data) => Api.post('/api/orders', data),
        list:         ()     => Api.get('/api/orders'),
        get:          (id)   => Api.get(`/api/orders/${id}`),
        updateStatus: (id, status) => Api.put(`/api/orders/${id}/status`, { status }),
    },
};

// ── Session state helper ─────────────────────────────────────────────────────
const AuthState = {
    user: null,

    async load() {
        try {
            this.user = await Api.auth.me();
        } catch {
            this.user = null;
        }
        this._notify();
        return this.user;
    },

    isLoggedIn()    { return !!this.user; },
    isAdmin()       { return this.user?.user_type === 'admin'; },
    isDeveloper()   { return ['admin', 'developer'].includes(this.user?.user_type); },

    _callbacks: [],
    onChange(fn) { this._callbacks.push(fn); },
    _notify()    { this._callbacks.forEach(fn => fn(this.user)); },

    async login(identifier, password) {
        const res = await Api.auth.login({ identifier, password });
        this.user = res.user;
        this._notify();
        return res;
    },

    async logout() {
        await Api.auth.logout();
        this.user = null;
        this._notify();
    },
};

// ── Cart badge helper ────────────────────────────────────────────────────────
const CartState = {
    async refreshBadge() {
        if (!AuthState.isLoggedIn()) return;
        try {
            const { items } = await Api.cart.get();
            const total = items.reduce((s, i) => s + i.quantity, 0);
            document.querySelectorAll('.cart-badge').forEach(el => {
                el.textContent = total > 0 ? total : '';
                el.style.display = total > 0 ? 'block' : 'none';
            });
        } catch { /* silently ignore if not authenticated */ }
    }
};

// Auto-load auth state on page load
document.addEventListener('DOMContentLoaded', async () => {
    await AuthState.load();
    await CartState.refreshBadge();
});

// Expose globally
window.Api        = Api;
window.AuthState  = AuthState;
window.CartState  = CartState;
