from flask import Blueprint, request, jsonify
from models.user import db, User
from models.activity import Activity
from models.payment import PaymentBatch, PaymentAdjustment
from flask_cors import cross_origin

admin_payments = db.Blueprint('admin_payments', __name__)

@admin_payments.route("/api/admin/payments/batches", methods=["GET"])
@cross_origin()
def get_batches():
    batches = PaymentBatch.query.order_by(PaymentBatch.id.desc()).all()
    return jsonify([b.to_dict() for b in batches]), 200

@admin_payments.route("/api/admin/payments/calculate/<string:month_name>", methods=["GET"])
@cross_origin()
def calculate_payouts(month_name):
    # Mapping for your activity date format (2026-01-01 -> Jan 2026)
    # For now, we filter activities that contain the year-month part
    # Example: If month_name is "Jan 2026", we look for "2026-01"
    
    users = User.query.filter_by(status='Active').all()
    report = []

    for user in users:
        # 1. Sum activity amounts
        base_pay = db.session.query(db.func.sum(Activity.amount)).filter(
            Activity.created_by == user.user_alnum
        ).scalar() or 0

        # 2. Get adjustments
        adj_sum = db.session.query(db.func.sum(PaymentAdjustment.amount)).filter(
            PaymentAdjustment.user_alnum == user.user_alnum,
            PaymentAdjustment.batch_month == month_name
        ).scalar() or 0

        report.append({
            "name": user.name,
            "user_alnum": user.user_alnum,
            "base": base_pay,
            "adjustment": adj_sum,
            "final": base_pay + adj_sum
        })

    return jsonify(report), 200