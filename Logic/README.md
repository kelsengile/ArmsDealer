# ArmsDealer — Backend (Flask + SQLite)

## Quick Start

```bash
# 1. Install dependencies
pip install flask flask-cors werkzeug

# 2. Run the server
python app.py
# → Server starts at http://localhost:5000
```

The SQLite database (`armsdealer.db`) is created automatically on first run,
with demo data seeded into all tables.

---

## Project Structure

```
armsdealer/
├── app.py                        ← entry point
├── requirements.txt
├── armsdealer.db                 ← auto-created SQLite file
├── backend/
│   ├── server.py                 ← Flask app factory
│   ├── database.py               ← schema + seed data
│   ├── auth.py                   ← decorators: @login_required, @role_required
│   ├── routes_users.py           ← /api/auth/*, /api/users/*
│   ├── routes_products.py        ← /api/products/*
│   ├── routes_services.py        ← /api/services/*
│   └── routes_orders.py          ← /api/cart/*, /api/orders/*
└── frontend/
    └── static/
        └── api-client.js         ← drop into any HTML page
```

---

## Database Tables

### `users`
| Column        | Type    | Notes                              |
|---------------|---------|------------------------------------|
| id            | INTEGER | Primary key                        |
| username      | TEXT    | Unique                             |
| email         | TEXT    | Unique                             |
| password_hash | TEXT    | bcrypt via werkzeug                |
| user_type     | TEXT    | `admin` \| `developer` \| `user`  |
| first_name    | TEXT    |                                    |
| last_name     | TEXT    |                                    |
| phone         | TEXT    |                                    |
| address       | TEXT    |                                    |
| is_active     | INTEGER | 0 = banned                         |
| created_at    | TEXT    | ISO datetime                       |

### `products`
| Column        | Type    | Notes                              |
|---------------|---------|------------------------------------|
| id            | INTEGER | Primary key                        |
| name          | TEXT    |                                    |
| description   | TEXT    |                                    |
| price         | REAL    | Base price (PHP)                   |
| stock         | INTEGER |                                    |
| category_type | TEXT    | `weapon` \| `equipment`           |
| subcategory   | TEXT    | Firearms, Handguns, Ammunition … |
| caliber       | TEXT    |                                    |
| brand         | TEXT    |                                    |
| model         | TEXT    |                                    |
| image_url     | TEXT    |                                    |
| discount_pct  | REAL    | 0–100                              |
| is_featured   | INTEGER | 1 = show in Featured section       |
| is_active     | INTEGER | 0 = soft-deleted                   |

### `services`
| Column        | Type    | Notes                              |
|---------------|---------|------------------------------------|
| id            | INTEGER | Primary key                        |
| name          | TEXT    |                                    |
| description   | TEXT    |                                    |
| price         | REAL    | Base price (PHP)                   |
| duration_days | INTEGER | Estimated turnaround               |
| category      | TEXT    | Gunsmithing, Customization …      |
| is_featured   | INTEGER |                                    |
| discount_pct  | REAL    |                                    |
| is_active     | INTEGER |                                    |

---

## API Reference

### Auth  `/api/auth/*`

| Method | Endpoint                    | Auth     | Description          |
|--------|-----------------------------|----------|----------------------|
| POST   | /api/auth/register          | Public   | Create account       |
| POST   | /api/auth/login             | Public   | Login (sets cookie)  |
| POST   | /api/auth/logout            | User     | Logout               |
| GET    | /api/auth/me                | User     | Current user profile |
| PUT    | /api/auth/me                | User     | Update profile       |
| POST   | /api/auth/change-password   | User     | Change password      |

### Users  `/api/users/*`
| Method | Endpoint          | Auth      | Description         |
|--------|-------------------|-----------|---------------------|
| GET    | /api/users        | Admin/Dev | List all users      |
| PUT    | /api/users/:id    | Admin     | Update role/status  |

### Products  `/api/products/*`
| Method | Endpoint                       | Auth      | Description              |
|--------|--------------------------------|-----------|--------------------------|
| GET    | /api/products                  | Public    | List / search            |
| GET    | /api/products/:id              | Public    | Single product           |
| GET    | /api/products/subcategories    | Public    | List subcategories       |
| POST   | /api/products                  | Admin/Dev | Create product           |
| PUT    | /api/products/:id              | Admin/Dev | Update product           |
| DELETE | /api/products/:id              | Admin     | Soft-delete              |

Query params for GET /api/products:
- `type` — `weapon` or `equipment`
- `subcategory` — e.g. `Firearms`
- `featured` — `1` to filter featured only
- `q` — keyword search
- `limit` / `offset` — pagination

### Services  `/api/services/*`
| Method | Endpoint                    | Auth      | Description        |
|--------|-----------------------------|-----------|-------------------|
| GET    | /api/services               | Public    | List / search     |
| GET    | /api/services/:id           | Public    | Single service    |
| GET    | /api/services/categories    | Public    | List categories   |
| POST   | /api/services               | Admin/Dev | Create service    |
| PUT    | /api/services/:id           | Admin/Dev | Update service    |
| DELETE | /api/services/:id           | Admin     | Soft-delete       |

### Cart  `/api/cart/*`
| Method | Endpoint          | Auth | Description           |
|--------|-------------------|------|-----------------------|
| GET    | /api/cart         | User | Get cart + totals     |
| POST   | /api/cart         | User | Add item              |
| PUT    | /api/cart/:id     | User | Update quantity       |
| DELETE | /api/cart/:id     | User | Remove item           |
| DELETE | /api/cart/clear   | User | Empty cart            |

### Orders  `/api/orders/*`
| Method | Endpoint                    | Auth      | Description            |
|--------|-----------------------------|-----------|------------------------|
| POST   | /api/orders                 | User      | Place order from cart  |
| GET    | /api/orders                 | User/Admin| List orders            |
| GET    | /api/orders/:id             | User/Admin| Order detail           |
| PUT    | /api/orders/:id/status      | Admin/Dev | Update order status    |

---

## Frontend Integration

Add to any HTML page **before** your page script:

```html
<script src="/static/api-client.js"></script>
```

Then use from JavaScript:

```javascript
// Login
await AuthState.login('admin', 'Admin@1234');

// Load featured products
const { items } = await Api.products.list({ featured: '1', type: 'weapon' });

// Add to cart
await Api.cart.add({ item_type: 'product', item_id: 1, quantity: 1 });
await CartState.refreshBadge();   // update the cart badge

// Place order
await Api.orders.place({ shipping_address: '123 Main St' });
```

---

## Demo Credentials

| Username | Password    | Role      |
|----------|-------------|-----------|
| admin    | Admin@1234  | admin     |
| devuser  | Dev@1234    | developer |
| johndoe  | User@1234   | user      |
