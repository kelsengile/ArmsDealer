# ArmsDealer.com

**Flask + SQLite E-commerce Web Application**

ArmsDealer.com is a full-stack e-commerce platform built for the sale, browsing, and management of arms, tactical equipment, and related professional services. It covers the entire retail lifecycle — from product discovery to order fulfillment — with a built-in administration system for complete backend control. The platform is designed for organizations and individuals operating in the arms and security industry who require a private, secure storefront with support for both civilian-authorized and restricted product listings.

The interface follows a military aesthetic with a dark color scheme, customizable accent colors, scanline overlays, monospace typography, and configurable background imagery. All visual elements are applied server-side on every request, eliminating any flash of unstyled content.

> **⚠️ Note:** This project is actively under development. Core commerce and account features are complete. Some planned features (promotions, services browsing page, tools section, news) are still in progress with no fixed release date.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Default Accounts](#default-accounts)
- [Database Maintenance](#database-maintenance)
- [Project Status](#project-status)

---

## Features

### Commerce

- **Product Catalogue** — Browse weapons, equipment, and tactical gear organized by categories, subcategories, and brands
- **Authorized / Restricted Listings** — Products are tiered by authorization level; restricted items are hidden from guests and visible only to logged-in users
- **Product Detail Pages** — Full individual product views with multi-image galleries, descriptions, ratings, related products, and brand information
- **Services Catalogue** — Browse professional services including training, maintenance, transport, consulting, and more
- **Shopping Cart** — Persistent database-backed cart supporting both products and services; survives session expiry
- **Checkout** — Full checkout flow supporting cash on delivery and internal wallet payment
- **Order Management** — Order lifecycle tracking through five stages: Order Placed → Packing → Shipping → Delivered → Cancelled
- **Wallet System** — Internal PHP balance usable at checkout; auto-refunds on eligible cancellations
- **Product Ratings** — Verified star ratings (1–5) submitted only by users with a delivered order containing that item

### Search and Discovery

- **Global Search Panel** — Product and brand search accessible from the navbar across all pages; respects authorization level
- **Category and Brand Filtering** — Dedicated browsing pages filtered by category slug or brand slug
- **Multi-currency Pricing** — Dynamic currency switching across PHP, USD, EUR, GBP, SGD, JPY, and CNY; persisted in a browser cookie

### Administration

- **Admin Dashboard** — Centralized management panel for inventory, orders, users, inquiries, and platform analytics
- **Product / Service / Brand CRUD** — Full add, edit, and delete operations with image upload support (up to 5 images per product)
- **Order Status Management** — Update any order's status; triggers automatic stock deduction and sales count update
- **User Management** — View all users, change roles between customer and admin, delete accounts
- **Inquiry Management** — View, status-update, and email-reply to customer support inquiries from the dashboard
- **Sales Analytics** — 7-day revenue chart, top products by sales and revenue, category breakdown, low stock alerts, recent user activity

### Account and Security

- **User Authentication** — Email-verified registration (OTP), login by username or email, logout, forgot password via OTP
- **Two-Factor Authentication (2FA)** — Optional TOTP-based 2FA via any authenticator app, with backup code generation
- **Active Session Management** — View and remotely revoke active browser sessions per device
- **Login History** — Full audit log of login attempts including timestamp, IP address, user agent, and success status
- **Change Password** — Inline password change for logged-in users with current password verification
- **Login Notifications** — Email alert sent on every successful login (configurable per user)

### Personalization and Settings

- **Appearance Customization** — Color mode, accent color, background image, opacity, font size, scanlines, compact mode, animations; applied server-side on every request
- **Notification Preferences** — Per-user control over which email categories are sent (order updates, security alerts, promotions)
- **Account Profile** — Username, email, contact number, bio, country, delivery address, payment method, wallet balance, profile image, social links
- **Multi-language Support** — Translation tables for products, services, brands, categories, and UI strings

### Privacy

- **Account Data Export** — Download complete account data as a plain text file, or receive it as a formatted HTML email
- **Account Deactivation** — Soft-disable account without permanent deletion
- **Account Deletion** — Permanent deletion of the account and all associated data

### Platform

- **Email Notification System** — Transactional emails for registration OTP, login alerts, order confirmation, order status updates, inquiry replies, and data exports; multi-port SMTP with automatic fallback (443 → 465 → 587)
- **Toast Notifications** — Non-intrusive in-page feedback messages for all user actions
- **Secure Connection Indicator** — Visual HTTPS/connection status indicator in the top bar
- **Environment-based Configuration** — All secrets and SMTP credentials managed via a `.env` file

---

## Tech Stack

| Layer          | Technology                           |
| -------------- | ------------------------------------ |
| Backend        | Python 3.13, Flask 3.1               |
| Database       | SQLite 3 (via Python stdlib sqlite3) |
| Frontend       | HTML5, CSS3, Vanilla JavaScript      |
| Templating     | Jinja2                               |
| Auth / Hashing | Flask sessions, Werkzeug             |
| 2FA            | pyotp (TOTP / RFC 6238)              |
| Email          | Python smtplib + email.mime          |
| Configuration  | python-dotenv                        |

---

## Project Structure

```
ArmsDealer.com/
│
├── armsdealer.py              # App entry point — Flask factory, blueprint registration,
│                              # appearance context processor, session refresh hook
├── db_helpers.py              # Shared DB utilities — get_db(), get_locale(), get_currency()
├── models.py                  # Data model helpers (User, Category, Product static methods)
├── email_service.py           # Centralised email sending — SMTP config, HTML wrapper,
│                              # notification functions (login, order, status, export)
├── init_db.py                 # Database initialisation script — runs schema.sql
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables — not committed to version control
├── .gitignore
│
├── database/
│   ├── schema.sql             # Full database schema, indexes, and triggers
│   └── armsdealer.db.sql      # Seed data export — products, brands, categories, currencies
│
├── routes/
│   ├── auth_routes.py         # Authentication — register, login, logout, change/forgot password
│   ├── main_routes.py         # Page routes — home, products, product detail, services,
│   │                          # about, contacts, settings, account, orders, dashboard
│   ├── cart_routes.py         # Cart — add/remove items, checkout, place order,
│   │                          # cancel order, admin order status update
│   └── api_routes.py          # JSON API — search, pricing, settings save, 2FA, sessions,
│                              # admin CRUD, ratings, inquiries, data export, account actions
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
│   │   ├── authbase.html          # Auth layout base
│   │   ├── login.html
│   │   ├── register.html
│   │   └── changepassword.html
│   ├── partials/
│   │   ├── base.html              # Global base layout (all pages)
│   │   ├── subbase.html           # Sub-layout for inner pages
│   │   ├── accountpanel.html      # Sliding account panel
│   │   ├── searchpanel.html       # Sliding search panel
│   │   ├── settingspanel.html     # Sliding settings panel
│   │   └── toast.html             # Toast notification partial
│   ├── specific/
│   │   ├── specificproduct.html   # Individual product detail page
│   │   └── specificservice.html   # Individual service detail page
│   └── user/
│       ├── account.html           # User profile page
│       ├── checkout.html          # Checkout page
│       ├── dashboard.html         # Admin dashboard
│       └── orders.html            # Orders, cart, and order history page
│
└── static/
    ├── css/
    │   ├── globalstyles.css
    │   ├── navbarstyles.css
    │   ├── auth.css
    │   ├── toast.css
    │   ├── pagestyles/            # Per-page stylesheets
    │   ├── partialstyles/         # Styles for panel partials
    │   ├── specific/              # Styles for product/service detail pages
    │   └── user/                  # Styles for account pages
    ├── js/
    │   ├── appearance.js
    │   ├── navbarfunctions.js
    │   ├── toast.js
    │   ├── translations.js        # Client-side i18n strings
    │   ├── pagefunctions/         # Per-page JS logic
    │   ├── partialfunctions/      # JS for panel partials
    │   └── specific/              # JS for product/service detail pages
    └── assets/
        ├── icons/
        │   ├── brandslogo/        # Brand logo images
        │   └── categoriesicons/   # Category icon images
        └── images/
            ├── pageimages/        # Hero and background images
            ├── productsimages/    # Product listing images
            ├── serviceimages/     # Service listing images
            └── userimages/        # User profile photos
```

---

## Requirements

- Python 3.10 or later (developed on Python 3.13)
- pip
- A Gmail account (or any SMTP server) for transactional email — optional but required for OTP registration
- DB Browser for SQLite or equivalent — for running the seed data script

**Python packages** (see `requirements.txt`):

```
flask>=3.0.0
Werkzeug>=3.0.0
python-dotenv>=1.0.0
pyotp>=2.9.0          # optional — required only for 2FA endpoints
```

---

## Setup Instructions

```bash
# 1. Create and activate a virtual environment
python -m venv env

# On Linux / macOS
source env/bin/activate

# On Windows (PowerShell)
.\env\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
#    Copy the .env.example or create a new .env file in the project root
#    (see Environment Variables section below)

# 4. Initialise the database
python init_db.py
#    Creates database/armsdealer.db and runs schema.sql

# 5. Seed the database
#    Open database/armsdealer.db.sql in DB Browser for SQLite
#    Execute the entire script against armsdealer.db
#    This populates products, brands, categories, currencies, and languages

# 6. Start the development server
python armsdealer.py

# 7. Open in browser
http://127.0.0.1:5000
```

---

## Environment Variables

Create a `.env` file in the project root with the following keys:

```env
# Flask
SECRET_KEY=your-long-random-secret-key-here

# SMTP (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASS=your-gmail-app-password
MAIL_FROM=your.email@gmail.com
SMTP_USE_TLS=true
```

**Notes:**

- `SECRET_KEY` must be a long, random string in production. Never use the development placeholder on a live server.
- For Gmail, generate an App Password from your Google Account under Security → 2-Step Verification → App Passwords. Do not use your main Gmail password.
- If SMTP is not configured, the application runs normally but OTP codes are shown as browser flash messages instead of being emailed, and all other email notifications are silently skipped.
- The `.env` file is listed in `.gitignore` and must never be committed to version control.

---

## Default Accounts

The seed data includes the following test accounts. **Remove all of these before any production deployment.**

| Role     | Username     | Email                             | Password           |
| -------- | ------------ | --------------------------------- | ------------------ |
| Admin    | mrcrabs      | eugene.crabs@thekrustykrab.com    | MoneyM0ney!        |
| Customer | spongebob    | spongebob@bikini.bottom           | Krabby1234!        |
| Customer | patrickstar  | patrick.star@bikini.bottom        | IAmStupid!23       |
| Customer | squidward    | squidward.tentacles@bikini.bottom | IHateEveryone!23   |
| Customer | sandycheeks  | sandy.cheeks@texas.com            | YeeHawTexas!23     |
| Customer | plankton     | sheldon.plankton@chumbucket.com   | SecretFormula!23   |
| Customer | ricksanchez  | rick.sanchez@c137.dim             | Wubbalubbadubdub!2 |
| Customer | mortysmith   | morty.smith@c137.dim              | Oh_Geez_Rick!23    |
| Customer | ben10        | ben.tennyson@plumber.net          | Omnitrix!2310      |
| Customer | gwentennyson | gwen.tennyson@plumber.net         | Anodite!Magic23    |
| Customer | grandpamax   | max.tennyson@plumber.net          | PlumberMax!2326    |

---

## Database Maintenance

### Reset transactional data (cart, orders, ratings, inquiries)

Run the following SQL in DB Browser for SQLite to wipe transactional data without dropping the full database. Useful during development and testing.

```sql
PRAGMA foreign_keys = OFF;

DELETE FROM cart_items;
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM product_ratings;
DELETE FROM inquiries;

DELETE FROM sqlite_sequence WHERE name='cart_items';
DELETE FROM sqlite_sequence WHERE name='order_items';
DELETE FROM sqlite_sequence WHERE name='orders';
DELETE FROM sqlite_sequence WHERE name='product_ratings';
DELETE FROM sqlite_sequence WHERE name='inquiries';

PRAGMA foreign_keys = ON;
```

### Rebuild from scratch

```bash
python init_db.py
```

Then re-run the seed script from `database/armsdealer.db.sql`.

---

## Project Status

### Complete

- User authentication (registration with OTP, login, logout, forgot password, change password)
- Product catalogue with category, subcategory, and brand browsing
- Product detail pages with multi-image gallery and related products
- Shopping cart and checkout (cash on delivery + wallet payment)
- Order lifecycle and admin order management
- Admin dashboard (analytics, inventory CRUD, user management, inquiry management)
- Full user account settings (7 tabs: account, appearance, security, notifications, help, privacy, login history)
- Appearance customization system (server-side CSS injection)
- Multi-currency support (PHP, USD, EUR, GBP, SGD, JPY, CNY)
- Global search panel
- Two-factor authentication (TOTP)
- Active session management and remote revocation
- Login history audit log
- Email notification system (OTP, login alerts, order confirmation, status updates, inquiry replies, data export)
- Contact and support inquiry system with admin reply
- Account data export (download and email)
- Account deactivation and permanent deletion
- Legal, about, and contacts static pages

### In Progress / Planned

- Promotions system (bundles, vouchers, seasonal sales, exclusive drops, rankings)
- Services browsing page with authorized/restricted filtering
- Specific service detail pages
- Tools section in the navigation
- News and updates section
- Homepage best sellers and trusted brands sections
- Product sorting and filtering controls on the products page
- Payment gateway integration
- Mobile layout refinements for the admin dashboard

---
