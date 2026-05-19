# ArmsDealer

**Flask + SQLite E-commerce Web Application**

ArmsDealer.com is an e-commerce platform for arms, equipment, and related services — offering browsing, purchasing, and order management for firearms, accessories, and other tactical products. With a focus on usability, security, and compliance, the platform provides a seamless shopping experience for users and robust management tools for administrators.

---

## Features

- **Product Catalog** — Browse a wide range of weapons, equipment, and tactical gear organized by categories and brands
- **Category & Brand Filtering** — Filter products by main categories, subcategories, and manufacturer brands with dedicated pages for each
- **Specific Product Pages** — Detailed individual product views with descriptions, ratings, and purchasing options
- **User Authentication** — Secure registration, login, and password change system with session management
- **Shopping Cart** — Add, update, and remove items with a persistent cart tied to user sessions
- **Checkout & Orders** — Full checkout flow with order creation and order history tracking per user
- **Admin Dashboard** — Dedicated admin panel for managing users, products, orders, and platform data
- **User Account Settings** — Manage account details, appearance preferences, notifications, privacy, language & region, and system actions
- **Multi-language Support** — Built-in translations system supporting multiple languages
- **Multi-currency Support** — Dynamic currency switching for international users
- **Search Panel** — Global product search accessible from the navbar across all pages
- **Secure Connection Indicator (Blinker)** — Visual HTTPS/connection status indicator in the top bar
- **Toast Notifications** — Non-intrusive user feedback messages throughout the interface
- **Responsive UI** — Clean, tactical-themed interface with global styles, page-specific styles, and reusable partials
- **TOTP / 2FA Support** — Two-factor authentication via `pyotp` for enhanced account security
- **Environment-based Configuration** — Uses `.env` file for secrets and environment variables

---

## Tech Stack

- **Backend:** Flask (Python 3.x)
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Templating:** Jinja2
- **Auth / Security:** Flask sessions, Werkzeug, pyotp (TOTP)
- **Configuration:** python-dotenv

---

## Project Structure

```
ArmsDealer.com/
│
├── armsdealer.py                  # App entry point, Flask app factory, route registration
├── db_helpers.py                  # Database connection helpers (get_db, get_locale, get_currency)
├── models.py                      # Data models and query logic
├── email_service.py               # Email sending service
├── init_db.py                     # Database initialization script
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (SECRET_KEY, etc.) — not committed
├── .gitignore
│
├── database/
│   ├── schema.sql                 # Full database schema definition
│   └── armsdealer.db.sql          # Seed data / database export
│
├── routes/
│   ├── api_routes.py              # REST API endpoints (products, cart, orders, etc.)
│   ├── auth_routes.py             # Authentication routes (login, register, password change)
│   ├── cart_routes.py             # Cart management routes
│   └── main_routes.py             # Main page routes (home, products, services, settings, etc.)
│
├── templates/
│   ├── homepage.html
│   ├── products.html
│   ├── services.html
│   ├── about.html
│   ├── contacts.html
│   ├── legal.html
│   ├── settings.html
│   ├── auth/
│   │   ├── authbase.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── changepassword.html
│   ├── partials/
│   │   ├── base.html              # Global base layout
│   │   ├── subbase.html           # Sub-layout for inner pages
│   │   ├── accountpanel.html      # Sliding account panel partial
│   │   ├── searchpanel.html       # Sliding search panel partial
│   │   ├── settingspanel.html     # Sliding settings panel partial
│   │   └── toast.html             # Toast notification partial
│   ├── specific/
│   │   ├── specificproduct.html   # Individual product detail page
│   │   └── specificservice.html   # Individual service detail page
│   └── user/
│       ├── account.html           # User account page
│       ├── checkout.html          # Checkout page
│       ├── dashboard.html         # Admin dashboard
│       └── orders.html            # User orders page
│
├── static/
│   ├── css/
│   │   ├── globalstyles.css
│   │   ├── navbarstyles.css
│   │   ├── auth.css
│   │   ├── toast.css
│   │   ├── pagestyles/            # Per-page stylesheets
│   │   ├── partialstyles/         # Styles for panel partials
│   │   ├── specific/              # Styles for specific product page
│   │   └── user/                  # Styles for user account pages
│   ├── js/
│   │   ├── appearance.js
│   │   ├── navbarfunctions.js
│   │   ├── toast.js
│   │   ├── translations.js        # Client-side translation strings
│   │   ├── pagefunctions/         # Per-page JS logic
│   │   ├── partialfunctions/      # JS for panel partials
│   │   └── specific/              # JS for specific product page
│   └── assets/
│       ├── icons/
│       │   ├── brandslogo/        # Brand logo images
│       │   └── categoriesicons/   # Category icon images
│       └── images/
│           ├── pageimages/        # Hero and page-specific images
│           ├── productsimages/    # Product listing images
│           ├── serviceimages/     # Service listing images
│           └── userimages/        # User profile images
```

---

## Setup Instructions

Follow these steps to run the project locally:

```bash
# 1. Create a virtual environment folder named 'env'
python -m venv env

# 2. Activate the virtual environment
# On Linux/macOS
source env/bin/activate
# On Windows (PowerShell)
.\env\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize the database (creates instance/armsdealer.db)
python init_db.py

# 5. Run the seed SQL in DB Browser for SQLite (or equivalent)
Open: database/armsdealer.db.sql
Execute it against your armsdealer.db to populate data

# 6. Run the development server
python armsdealer.py

# 7. Open your browser and go to:
http://127.0.0.1:5000
```

---


> **⚠️ Note:** This project is not yet finished. Additional features are planned and actively being worked on with no set release date.
