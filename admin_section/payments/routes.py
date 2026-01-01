from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import func, cast, String
from datetime import datetime
from models.user import db, User
from models.activity import Activity
from models.payment import PaymentTransaction

# Fixed Blueprint definition
admin_payments = Blueprint('admin_payments', __name__)

@admin_payments.route("/api/admin/payments/calculate/<string:month_name>", methods=["GET"])
@cross_origin()
def calculate_payouts(month_name):
    try:
        date_obj = datetime.strptime(month_name, "%b %Y")
        search_pattern = date_obj.strftime("%Y-%m")
    except:
        return jsonify({"error": "Invalid date format"}), 400

    # Get employees only
    employees = User.query.filter_by(role='employee').all()
    report = []

    for emp in employees:
        # 1. Fetch WORK DONE from existing activities table
        earned = db.session.query(func.sum(Activity.amount)).filter(
            Activity.created_by == emp.user_alnum,
            cast(Activity.time_date, String).like(f"{search_pattern}%")
        ).scalar() or 0

        # 2. Fetch PAYMENTS RECORDED by admin
        paid = db.session.query(func.sum(PaymentTransaction.amount_paid)).filter(
            PaymentTransaction.user_alnum == emp.user_alnum,
            PaymentTransaction.batch_month == month_name
        ).scalar() or 0

        balance = earned - paid

        if earned > 0 or paid > 0:
            report.append({
                "name": emp.name,
                "user_alnum": emp.user_alnum,
                "total_earned": float(earned),
                "amount_paid": float(paid),
                "balance": float(balance)
            })
            
    return jsonify(report), 200

@admin_payments.route("/api/admin/payments/record", methods=["POST"])
@cross_origin()
def record_payment():
    data = request.json
    try:
        new_pay = PaymentTransaction(
            user_alnum=data['user_alnum'],
            batch_month=data['batch_month'],
            amount_paid=float(data['amount']),
            reference=data.get('reference', 'Cash')
        )
        db.session.add(new_pay)
        db.session.commit()
        return jsonify({"message": "Payment recorded"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500