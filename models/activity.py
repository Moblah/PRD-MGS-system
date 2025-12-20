from datetime import datetime
from .user import db

class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.String(20), unique=True, nullable=False) # e.g., ACT-X123
    activity = db.Column(db.String(255), nullable=False)
    qty = db.Column(db.Float, default=0.0)
    items = db.Column(db.String(255))
    rate_rule = db.Column(db.String(100))
    amount = db.Column(db.Float, default=0.0)
    comment = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.String(20), db.ForeignKey('users.user_alnum'), nullable=False)
    time_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "activity_id": self.activity_id,
            "activity": self.activity,
            "qty": self.qty,
            "items": self.items,
            "rate_rule": self.rate_rule,
            "amount": self.amount,
            "comment": self.comment,
            "created_by": self.created_by,
            "time_date": self.time_date.strftime("%Y-%m-%d %H:%M:%S")
        }