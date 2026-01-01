from flask import Blueprint, request, jsonify
from models.user import db, User
from models.activity import Activity
from models.payment import PaymentBatch, PaymentAdjustment
from sqlalchemy import func, cast, String
from datetime import datetime
from flask_cors import cross_origin

admin_payments = Blueprint('admin_payments', __name__)

@admin_payments.route("/api/admin/payments/batches", methods=["GET"])
@cross_origin()
def get_batches():
    # Scan activities table to find months where work actually happened
    # This ensures your UI is never empty if there is activity data
    active_months = db.session.query(
        func.distinct(func.to_char(Activity.time_date, 'Mon YYYY'))
    ).all()

    results = []
    for m in active_months:
        month_str = m[0]
        # Check if we have a saved status in the database
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
        # Convert "Dec 2025" to "2025-12" for SQL filtering
        date_obj = datetime.strptime(month_name, "%b %Y")
        search_pattern = date_obj.strftime("%Y-%m")
    except ValueError:
        return jsonify({"error": "Invalid month format"}), 400

    # FILTER: Only users where role is 'Employee'
    employees = User.query.filter_by(role='Employee').all()
    report = []

    for emp in employees:
        # Sum activities for this employee for the selected month
        base_pay = db.session.query(func.sum(Activity.amount)).filter(
            Activity.created_by == emp.user_alnum,
            cast(Activity.time_date, String).like(f"{search_pattern}%")
        ).scalar() or 0

        # Sum manual adjustments
        adj_sum = db.session.query(func.sum(PaymentAdjustment.amount)).filter(
            PaymentAdjustment.user_alnum == emp.user_alnum,
            PaymentAdjustment.batch_month == month_name
        ).scalar() or 0

        if base_pay > 0 or adj_sum != 0:
            report.append({
                "name": emp.name,
                "user_alnum": emp.user_alnum,
                "base": float(base_pay),
                "adjustment": float(adj_sum),
                "final": float(base_pay + adj_sum)
            })

    return jsonify(report), 200

@admin_payments.route("/api/admin/payments/adjust", methods=["POST"])
@cross_origin()
def add_adjustment():
    data = request.json
    new_adj = PaymentAdjustment(
        user_alnum=data['user_alnum'],
        batch_month=data['batch_month'],
        amount=float(data['amount']),
        reason=data['reason']
    )
    db.session.add(new_adj)
    db.session.commit()
    return jsonify({"message": "Adjustment added"}), 201