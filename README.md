# ArmsDealer

**Flask + SQLite E-commerce Web Application**

ArmsDealer.com is a e-commerce platform for arms and related services, offering browsing, purchasing, and order management for firearms, accessories, and other related products. With a focus on usability, security, and compliance, the platform provides a seamless shopping experience for users and robust management tools for administrators.

---

## Features

- ***

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML5, CSS, JavaScript

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

# 5. Run SQL excecution on SQL Browser
armsdealer.db.sql

# 6. Run the development server
python armsdealer.py

# 7. Open your browser and go to:
http://127.0.0.1:5000
```
