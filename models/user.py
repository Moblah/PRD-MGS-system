from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_alnum = db.Column(db.String(5), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    username_email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="active")
    team = db.Column(db.String(50))