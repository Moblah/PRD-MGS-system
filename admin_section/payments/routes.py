from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import func, cast, String
from datetime import datetime

# Import your database and models
from models.user import db, User
from models.activity import Activity
from models.payment import PaymentBatch, PaymentAdjustment, PaymentTransaction

# 1. FIX: Use Blueprint from Flask, not db
admin_payments = Blueprint('admin_payments', __name__)

@admin_payments.route("/api/admin/payments/batches", methods=["GET"])
@cross_origin()
def get_batches():
    active_months = db.session.query(
        func.distinct(func.to_char(Activity.time_date, 'Mon YYYY'))
    ).all()

    results = []
    for m in active_months:
        month_str = m[0]
        batch_record = PaymentBatch.query.filter_by(batch_month=month_str).first()
        results.append({
            "month": month_str,
            "status": batch_record.status if batch_record else "Draft",
            "total": f"{batch_record.total_amount:,.2f}" if batch_record else "Pending"
        })
    return jsonify(results), 200

@admin_payments.route("/api/admin/payments/calculate/<string:month_name>", methods=["GET"])
@cross_origin()
def calculate_payouts(month_name):
    try:
        date_obj = datetime.strptime(month_name, "%b %Y")
        search_pattern = date_obj.strftime("%Y-%m")
    except ValueError:
        return jsonify({"error": "Invalid month format"}), 400

    # Only include employees
    employees = User.query.filter_by(role='Employee').all()
    report = []

    for emp in employees:
        earned = db.session.query(func.sum(Activity.amount)).filter(
            Activity.created_by == emp.user_alnum,
            cast(Activity.time_date, String).like(f"{search_pattern}%")
        ).scalar() or 0

        adjs = db.session.query(func.sum(PaymentAdjustment.amount)).filter(
            PaymentAdjustment.user_alnum == emp.user_alnum,
            PaymentAdjustment.batch_month == month_name
        ).scalar() or 0

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
                "total_due": float(total_due),
                "paid": float(paid),
                "balance": float(remaining),
                "status": "Paid" if remaining <= 0 else "Unpaid" if paid == 0 else "Partial"
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