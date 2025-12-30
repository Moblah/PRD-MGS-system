from flask import Blueprint, request, jsonify
from models.user import db, User  # Ensure User model is imported
from models.activity import Activity
from sqlalchemy import text
import string, random

employee_today = Blueprint('employee_today', __name__)

def generate_act_id():
    return 'ACT-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@employee_today.route("/api/employee/today/<string:user_alnum>", methods=["GET"])
def get_activities(user_alnum):
    # Get date from query string, default to None (all time) or specific date
    target_date = request.args.get('date')
    query = Activity.query.filter_by(created_by=user_alnum)
    
    if target_date:
        # Filter activities by the created_at date part
        query = query.filter(db.func.date(Activity.created_at) == target_date)
    
    activities = query.order_by(Activity.created_at.desc()).all()
    return jsonify([a.to_dict() for a in activities]), 200

@employee_today.route("/api/users/<string:user_alnum>", methods=["GET"])
def get_user_by_alnum(user_alnum):
    # Try to find actual user name from database
    user = User.query.filter_by(user_alnum=user_alnum).first()
    if user:
        return jsonify({
            'user_alnum': user.user_alnum,
            'full_name': user.full_name,
            'role': user.role
        }), 200
    return jsonify({'full_name': user_alnum}), 200 # Fallback

@employee_today.route("/api/employee/today", methods=["POST"])
def add_activity():
    data = request.get_json()
    try:
        new_act = Activity(
            activity_id=generate_act_id(),
            activity=data.get('activity'),
            qty=data.get('qty'),
            amount=data.get('amount'),
            comment=data.get('comment'),
            created_by=data.get('created_by')
        )
        db.session.add(new_act)
        db.session.commit()
        return jsonify(new_act.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500