from models.user import db
from datetime import datetime

class PaymentBatch(db.Model):
    __tablename__ = 'payment_batches'
    id = db.Column(db.Integer, primary_key=True)
    batch_month = db.Column(db.String(20), nullable=False) # e.g., "Dec 2025"
    status = db.Column(db.String(20), default='Draft')     # Draft, Paid
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finalized_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "month": self.batch_month,
            "status": self.status,
            "total": f"{self.total_amount:,.2f}",
            "created_at": self.created_at.strftime('%Y-%m-%d')
        }