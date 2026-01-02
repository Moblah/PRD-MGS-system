@admin_payments.route("/api/employee/bonuses/<string:user_alnum>/<int:year>/<int:month>", methods=["GET"])
@cross_origin()
def get_employee_bonuses(user_alnum, year, month):
    try:
        # 1. Fetch all detailed activities for the breakdown table
        activities = Activity.query.filter(
            Activity.created_by == user_alnum,
            extract('year', Activity.time_date) == year,
            extract('month', Activity.time_date) == month
        ).order_by(Activity.time_date.desc()).all()

        # 2. Calculate Total Earned (Sum of activities)
        total_earned = sum(a.amount for a in activities) or 0

        # 3. Calculate Total Paid (From payment_transactions table)
        total_paid = db.session.query(func.sum(PaymentTransaction.amount_paid)).filter(
            PaymentTransaction.user_alnum == user_alnum,
            PaymentTransaction.batch_month == f"{month}-{year}"
        ).scalar() or 0

        breakdown = [{
            "date": a.time_date.strftime("%m-%d"),
            "activity": a.activity_type,
            "quantity": 1, # Adjust if your schema has a qty field
            "rate": f"{a.amount}/item",
            "amount": float(a.amount)
        } for a in activities]

        return jsonify({
            "totalEarned": float(total_earned),
            "totalPaid": float(total_paid),
            "balance": float(total_earned - total_paid),
            "breakdown": breakdown
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500