from .user import db
from datetime import datetime

class PaymentBatch(db.Model):
    __tablename__ = 'payment_batches'
    id = db.Column(db.Integer, primary_key=True)
    batch_month = db.Column(db.String(20), nullable=False, unique=True) # e.g., "Dec 2025"
    status = db.Column(db.String(20), default='Draft') # Draft, Paid
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "month": self.batch_month,
            "status": self.status,
            "total": f"{self.total_amount:,.2f}"
        }

class PaymentAdjustment(db.Model):
    __tablename__ = 'payment_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    user_alnum = db.Column(db.String(50), nullable=False)
    batch_month = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)