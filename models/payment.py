from .user import db
from datetime import datetime

class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_alnum = db.Column(db.String(50), nullable=False) # Links to employee
    batch_month = db.Column(db.String(20), nullable=False) # e.g., "Dec 2025"
    amount_paid = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(100)) # M-Pesa Code or "Cash"
    date_paid = db.Column(db.DateTime, default=datetime.utcnow)

class PaymentAdjustment(db.Model):
    __tablename__ = 'payment_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    user_alnum = db.Column(db.String(50), nullable=False)
    batch_month = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False) # Bonuses/Deductions
    reason = db.Column(db.String(255))