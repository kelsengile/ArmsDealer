"""
ArmsDealer — Flask Backend Entry Point
Run: python app.py
"""
from backend.server import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
