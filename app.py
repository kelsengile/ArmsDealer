from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///armsdealer.db'
db = SQLAlchemy(app)


@app.route("/")
def home():
    return render_template('homepage.html')


if __name__ == "__main__":
    app.run(debug=True)
