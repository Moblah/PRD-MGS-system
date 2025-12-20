from datetime import datetime
from models.user import db

class Abr(db.Model):
    __tablename__ = 'abr'
    
    id = db.Column(db.Integer, primary_key=True)
    abr_id = db.Column(db.String(20), unique=True, nullable=False) # e.g., OPR-123
    name = db.Column(db.String(100), nullable=False)
    applies_to = db.Column(db.String(50), nullable=False) # e.g., D2, PN, All
    rule = db.Column(db.String(50), nullable=False)      # e.g., per entry
    rate = db.Column(db.Float, nullable=False)
    from_date = db.Column(db.String(20), nullable=False) # Effective Date
    created_by = db.Column(db.String(20), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "abr_id": self.abr_id,
            "name": self.name,
            "applies_to": self.applies_to,
            "rule": self.rule,
            "rate": self.rate,
            "from_date": self.from_date,
            "created_by": self.created_by,
            "time": self.time.strftime("%Y-%m-%d %H:%M:%S")
        }