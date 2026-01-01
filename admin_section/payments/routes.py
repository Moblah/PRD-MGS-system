from flask import Blueprint, jsonify
from models.user import db, User
from models.activity import Activity
from models.payment import PaymentTransaction, PaymentAdjustment
from sqlalchemy import func
from flask_cors import cross_origin

admin_reports = Blueprint('admin_reports', __name__)

@admin_reports.route("/api/admin/reports/summary", methods=["GET"])
@cross_origin()
def get_financial_summary():
    # 1. Total Gross Liabilities (Activities + Manual Adjustments)
    total_earned = db.session.query(func.sum(Activity.amount)).scalar() or 0
    total_adj = db.session.query(func.sum(PaymentAdjustment.amount)).scalar() or 0
    gross_debt = total_earned + total_adj

    # 2. Total Cash Disbursed (Actual payments made)
    total_paid = db.session.query(func.sum(PaymentTransaction.amount_paid)).scalar() or 0

    # 3. Remaining Company Liability
    remaining_balance = gross_debt - total_paid

    # 4. Top 5 Earners (Filter: Only Employees)
    # Joins Users and Activities to find who generated the most value
    top_earners = db.session.query(
        User.name, 
        func.sum(Activity.amount).label('total')
    ).join(Activity, User.user_alnum == Activity.created_by)\
     .filter(User.role == 'Employee')\
     .group_by(User.name)\
     .order_by(func.sum(Activity.amount).desc()).limit(5).all()

    return jsonify({
        "metrics": {
            "gross_liabilities": float(gross_debt),
            "total_paid": float(total_paid),
            "outstanding_balance": float(remaining_balance),
            "payment_ratio": round((total_paid / gross_debt * 100), 2) if gross_debt > 0 else 0
        },
        "top_earners": [{"name": e[0], "amount": float(e[1])} for e in top_earners]
    }), 200