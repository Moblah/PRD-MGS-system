from flask import Blueprint, jsonify
from flask_cors import cross_origin
from sqlalchemy import func, extract
# Replace with your actual model import paths
from models.user import db
from models.activity import Activity
from models.payment import PaymentTransaction

# Named specifically for employee access
employee_portal = Blueprint('employee_portal', __name__)

@employee_portal.route("/api/employee/bonuses/<string:user_alnum>/<int:year>/<int:month>", methods=["GET"])
@cross_origin()
def get_my_bonuses(user_alnum, year, month):
    """
    Private route for employees to view their own breakdown and payout status.
    """
    try:
        # 1. Fetch detailed activities for the table
        activities = Activity.query.filter(
            Activity.created_by == user_alnum,
            extract('year', Activity.time_date) == year,
            extract('month', Activity.time_date) == month
        ).order_by(Activity.time_date.desc()).all()

        # 2. Sum Total Earned
        total_earned = sum(a.amount for a in activities) if activities else 0

        # 3. Sum Total Paid (Matches your Admin batch format "M-YYYY")
        total_paid = db.session.query(func.sum(PaymentTransaction.amount_paid)).filter(
            PaymentTransaction.user_alnum == user_alnum,
            PaymentTransaction.batch_month == f"{month}-{year}"
        ).scalar() or 0

        # 4. Map the activities for the React frontend table
        breakdown = [{
            "date": a.time_date.strftime("%d-%b"), # e.g., 02-Jan
            "activity": getattr(a, 'activity', 'System Task'),
            "quantity": 1,
            "rate": f"KES {float(a.amount):,.0f}",
            "amount": float(a.amount)
        } for a in activities]

        return jsonify({
            "totalEarned": float(total_earned),
            "totalPaid": float(total_paid),
            "balance": float(total_earned - total_paid),
            "breakdown": breakdown,
            "month_name": activities[0].time_date.strftime("%B") if activities else "Selected Period"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500