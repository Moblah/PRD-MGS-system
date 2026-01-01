from .user import db
from datetime import datetime

class PaymentBatch(db.Model):
    __tablename__ = 'payment_batches'
    id = db.Column(db.Integer, primary_key=True)
    batch_month = db.Column(db.String(20), nullable=False, unique=True)
    status = db.Column(db.String(20), default='Draft') # Draft, Finalized
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PaymentAdjustment(db.Model):
    __tablename__ = 'payment_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    user_alnum = db.Column(db.String(50), nullable=False)
    batch_month = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255))

class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_alnum = db.Column(db.String(50), nullable=False)
    batch_month = db.Column(db.String(20), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(100)) # e.g. M-Pesa ID or "Cash"
    date_paid = db.Column(db.DateTime, default=datetime.utcnow)