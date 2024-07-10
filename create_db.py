from flask import Flask
from models import db

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///market.db"

db.init_app(app)

with app.app_context():
    db.create_all()
    print("Database and tables created successfully.")
