from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import func, extract
from models.user import db, User
from models.activity import Activity
from models.payment import PaymentTransaction

# THIS IS THE FIX: No "db." before Blueprint
admin_payments = Blueprint('admin_payments', __name__)

@admin_payments.route("/api/admin/payouts/<int:year>/<int:month>", methods=["GET"])
@cross_origin()
def get_payouts(year, month):
    try:
        employees = User.query.filter(User.role.ilike('employee')).all()
        report = []
        for emp in employees:
            earned = db.session.query(func.sum(Activity.amount)).filter(
                Activity.created_by == emp.user_alnum,
                extract('year', Activity.time_date) == year,
                extract('month', Activity.time_date) == month
            ).scalar() or 0

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
        # We get the 'period' directly from the frontend data
        period_value = str(data.get('period', 'unknown'))

        new_pay = PaymentTransaction(
            user_alnum=str(data.get('user_alnum')),
            amount_paid=float(data.get('amount', 0)),
            batch_period=period_value, 
            reference=data.get('reference', 'Admin Payout')
        )
        db.session.add(new_pay)
        db.session.commit()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        db.session.rollback()
        # This will now show the actual error in Render logs if it fails again
        print(f"Deployment Error: {str(e)}") 
        return jsonify({"error": str(e)}), 400