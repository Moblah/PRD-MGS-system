# admin_section/payments/routes.py

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import func, extract
from models.user import db, User
from models.activity import Activity
from models.payment import PaymentTransaction

# CORRECT: Blueprint comes from 'flask', not 'db'
admin_payments = Blueprint('admin_payments', __name__)

@admin_payments.route("/api/admin/payouts/<int:year>/<int:month>", methods=["GET"])
@cross_origin()
def get_payouts(year, month):
    try:
        # Fetch only employees
        employees = User.query.filter(User.role.ilike('employee')).all()
        report = []

        for emp in employees:
            # Calculate Total Earned (Debt)
            earned = db.session.query(func.sum(Activity.amount)).filter(
                Activity.created_by == emp.user_alnum,
                extract('year', Activity.time_date) == year,
                extract('month', Activity.time_date) == month
            ).scalar() or 0

            # Calculate Total Paid
            paid = db.session.query(func.sum(PaymentTransaction.amount_paid)).filter(
                PaymentTransaction.user_alnum == emp.user_alnum,
                PaymentTransaction.batch_period == f"{month}-{year}"
            ).scalar() or 0

            if earned > 0 or paid > 0:
                report.append({
                    "name": emp.name,
                    "user_alnum": emp.user_alnum,
                    "earned": float(earned),
                    "paid": float(paid),
                    "balance": float(earned - paid)
                })

        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_payments.route("/api/admin/record-payment", methods=["POST"])
@cross_origin()
def record_payment():
    data = request.json
    try:
        new_pay = PaymentTransaction(
            user_alnum=data['user_alnum'],
            amount_paid=float(data['amount']),
            batch_period=data['period'],
            reference=data.get('reference', 'Admin Payout')
        )
        db.session.add(new_pay)
        db.session.commit()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400