from flask import Blueprint, request, jsonify
from models.user import db, User
from models.activity import Activity
from models.payment import PaymentBatch
from flask_cors import cross_origin

admin_payments = Blueprint('admin_payments', __name__)

@admin_payments.route("/api/admin/payments/batches", methods=["GET"])
@cross_origin()
def get_batches():
    # Fetch existing batches
    batches = PaymentBatch.query.order_by(PaymentBatch.id.desc()).all()
    return jsonify([b.to_dict() for b in batches]), 200

@admin_payments.route("/api/admin/payments/calculate/<string:month_year>", methods=["GET"])
@cross_origin()
def calculate_payouts(month_year):
    """
    Logic: Sum activities for each user for the given month.
    month_year format: '2025-12'
    """
    users = User.query.filter_by(status='Active').all()
    report = []

    for user in users:
        # Sum activities where created_by matches user_alnum
        # and date matches the month
        total = db.session.query(db.func.sum(Activity.amount)).filter(
            Activity.created_by == user.user_alnum,
            Activity.time_date.contains(month_year)
        ).scalar() or 0

        report.append({
            "name": user.name,
            "user_alnum": user.user_alnum,
            "base": total,
            "adjustment": 0,
            "final": total
        })

    return jsonify(report), 200