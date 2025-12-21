# Add these routes to your existing backend

@employee_today.route("/api/abr", methods=["GET"])
def get_abr_data():
    """Get all ABR (Activity Based Rates) data"""
    try:
        # Assuming you have an ABR model
        from models.abr import ABR
        abr_data = ABR.query.all()
        return jsonify([{
            'name': item.name,
            'rate': item.rate,
            'applies_to': item.applies_to
        } for item in abr_data]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@employee_today.route("/api/users/<string:user_alnum>", methods=["GET"])
def get_user_by_alnum(user_alnum):
    """Get user details by alnum"""
    try:
        from models.user import User
        user = User.query.filter_by(user_alnum=user_alnum).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            'user_alnum': user.user_alnum,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# You also need to modify the add_activity endpoint to include sole_type
@employee_today.route("/api/employee/today", methods=["POST"])
def add_activity():
    data = request.get_json()
    try:
        new_act = Activity(
            activity_id=f"ACT-{generate_act_id()}",
            activity=data.get('activity'),
            qty=data.get('qty'),
            amount=data.get('amount'),
            comment=data.get('comment'),
            created_by=data.get('created_by'),
            sole_type=data.get('sole_type', 'D2')  # Add this line
        )
        db.session.add(new_act)
        db.session.commit()
        return jsonify(new_act.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500