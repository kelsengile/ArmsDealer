"""
init_db.py
Run this once to initialize the ArmsDealer database.
Usage: python init_db.py
"""

import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'armsdealer.db')
SCHEMA   = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')


def init_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    with sqlite3.connect(DATABASE) as conn:
        with open(SCHEMA, 'r') as f:
            conn.executescript(f.read())
    print(f"Database initialized at: {DATABASE}")


if __name__ == '__main__':
    init_db()
