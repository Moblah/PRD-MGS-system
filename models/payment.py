# models/payment.py
from .user import db
from datetime import datetime

class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_alnum = db.Column(db.String(50), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    batch_month = db.Column(db.String(20), nullable=False) # MUST match DB
    reference = db.Column(db.String(100))
    date_paid = db.Column(db.DateTime, default=datetime.utcnow)