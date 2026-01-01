# models/payment.py
from .user import db
from datetime import datetime

class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'
    
    # This line tells SQLAlchemy to allow re-defining the table if it already exists
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    user_alnum = db.Column(db.String(50), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    batch_period = db.Column(db.String(20), nullable=False) # e.g., '1-2026'
    reference = db.Column(db.String(100))
    date_paid = db.Column(db.DateTime, default=datetime.utcnow)