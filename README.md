# ArmsDealer — Tactical Supply Co.

A Flask-based e-commerce web application for a tactical arms dealer, featuring a product catalog, services, cart, and user authentication.

---

## Project Structure

```
ArmsDealer/
├── app.py               # Flask app + all routes
├── init_db.py           # One-time database initialization script
├── models.py            # Data-access helpers (User, Product, Order, etc.)
├── requirements.txt     # Python dependencies
│
├── database/
│   ├── schema.sql       # SQL table definitions
│   └── armsdealer.db    # SQLite database (created by init_db.py)
│
├── static/
│   ├── css/
│   │   ├── globalstyles.css
│   │   ├── navbarstyles.css
│   │   └── pagestyles/
│   │       └── homepagestyles.css
│   │
│   ├── js/
│   │   ├── navbarfunctions.js
│   │   └── pagefunctions/
│   │       └── homepagefuntions.js
│   │
│   └── assets/
│       ├── fonts/
│       ├── icons/
│       │   └── categoriesicons/     # Category PNG icons
│       └── images/
│           ├── productsimages/      # Product photo uploads
│           ├── serviceimages/       # Service photo uploads
│           └── pageimages/
│               ├── homepageimages/
│               │   └── featuredimages/
│               └── imbeddedimages/
│                   ├── globalimbeddedimages/   # Logo, backgrounds
│                   └── pageimbeddedimages/
│                       └── homepageimbeddedimages/
│                           └── herocarouselimages/
│
└── templates/
    ├── base.html          # Shared layout (navbar, header, blocks)
    ├── homepage.html      # Home page
    ├── products.html      # Products listing (to be built)
    ├── services.html      # Services listing (to be built)
    ├── about.html         # About page (to be built)
    ├── contacts.html      # Contact page (to be built)
    ├── legal.html         # Legal page (to be built)
    ├── cart.html          # Shopping cart (to be built)
    ├── checkout.html      # Checkout (to be built)
    └── auth/
        ├── login.html     # Login (to be built)
        └── register.html  # Registration (to be built)
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize the database
```bash
python init_db.py
```

### 3. Run the development server
```bash
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Routes

| URL | Template | Description |
|-----|----------|-------------|
| `/` or `/home` | `homepage.html` | Landing page |
| `/products` | `products.html` | Product catalog |
| `/services` | `services.html` | Services catalog |
| `/about` | `about.html` | About Us |
| `/contacts` | `contacts.html` | Contact / Inquiry |
| `/legal` | `legal.html` | Legal & Compliance |
| `/login` | `auth/login.html` | User login |
| `/register` | `auth/register.html` | User registration |
| `/logout` | — | Clears session, redirects home |
| `/cart` | `cart.html` | Shopping cart |
| `/checkout` | `checkout.html` | Checkout flow |

---

## Database Tables

| Table | Description |
|-------|-------------|
| `users` | Registered accounts (customer / admin) |
| `categories` | Product & service categories |
| `products` | Firearm and gear listings |
| `services` | Gunsmith & consulting services |
| `orders` | Customer orders with status tracking |
| `order_items` | Line items for each order |
| `cart_items` | Per-user shopping cart |
| `inquiries` | Contact form submissions |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-change-in-production` | Flask session secret key |

Create a `.env` file to override defaults:
```
SECRET_KEY=your-strong-secret-key-here
```

---

## Tech Stack
- **Backend:** Python / Flask
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, Vanilla JS (Jinja2 templates)
- **Fonts:** Google Fonts (Oswald, Share Tech Mono)
