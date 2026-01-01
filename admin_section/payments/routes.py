from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import func, cast, String
from datetime import datetime

# Import db and Models
from models.user import db, User
from models.activity import Activity
from models.payment import PaymentTransaction, PaymentAdjustment

# FIX: Changed 'db.Blueprint' to 'Blueprint' (imported from flask above)
admin_payments = Blueprint('admin_payments', __name__)

@admin_payments.route("/api/admin/payments/calculate/<string:month_name>", methods=["GET"])
@cross_origin()
def calculate_payouts(month_name):
    try:
        date_obj = datetime.strptime(month_name, "%b %Y")
        search_pattern = date_obj.strftime("%Y-%m")
    except:
        return jsonify({"error": "Invalid month format"}), 400

    # Ensure role is 'employee'
    employees = User.query.filter_by(role='employee').all()
    report = []

    for emp in employees:
        # 1. EARNINGS: Sum from activities table
        earned = db.session.query(func.sum(Activity.amount)).filter(
            Activity.created_by == emp.user_alnum,
            cast(Activity.time_date, String).like(f"{search_pattern}%")
        ).scalar() or 0

        # 2. ADJUSTMENTS: Bonuses/Penalties
        adjs = db.session.query(func.sum(PaymentAdjustment.amount)).filter(
            PaymentAdjustment.user_alnum == emp.user_alnum,
            PaymentAdjustment.batch_month == month_name
        ).scalar() or 0

        # 3. BALANCE: Real-time subtraction of recorded payments
        paid = db.session.query(func.sum(PaymentTransaction.amount_paid)).filter(
            PaymentTransaction.user_alnum == emp.user_alnum,
            PaymentTransaction.batch_month == month_name
        ).scalar() or 0

        total_due = earned + adjs
        remaining = total_due - paid

        if total_due > 0 or paid > 0:
            report.append({
                "name": emp.name,
                "user_alnum": emp.user_alnum,
                "total_earned": float(total_due),
                "amount_paid": float(paid),
                "balance": float(remaining)
            })

    return jsonify(report), 200

@admin_payments.route("/api/admin/payments/record", methods=["POST"])
@cross_origin()
def record_payment():
    data = request.json
    new_pay = PaymentTransaction(
        user_alnum=data['user_alnum'],
        batch_month=data['batch_month'],
        amount_paid=float(data['amount']),
        reference=data.get('reference', 'Cash')
    )
    db.session.add(new_pay)
    db.session.commit()
    return jsonify({"message": "Payment recorded"}), 201