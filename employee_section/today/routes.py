from flask import Blueprint, request, jsonify
from models.user import db, User
from models.activity import Activity
from sqlalchemy import text
import string
import random

employee_today = Blueprint('employee_today', __name__)

def generate_act_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@employee_today.route("/api/employee/today/<string:user_alnum>", methods=["GET"])
def get_activities(user_alnum):
    target_date = request.args.get('date')
    query = Activity.query.filter_by(created_by=user_alnum)
    
    if target_date:
        # Matches your DB column 'time_date'
        query = query.filter(db.func.date(Activity.time_date) == target_date)
    
    activities = query.order_by(Activity.time_date.desc()).all()
    return jsonify([a.to_dict() for a in activities]), 200

@employee_today.route("/api/employee/today", methods=["POST"])
def add_activity():
    data = request.get_json()
    try:
        new_act = Activity(
            activity_id=f"ACT-{generate_act_id()}",
            activity=data.get('activity'),
            qty=data.get('qty'),
            items=data.get('items', ''),
            rate_rule=data.get('rate_rule', 'per quantity'),
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

@employee_today.route("/api/users/<string:user_alnum>", methods=["GET"])
def get_user_by_alnum(user_alnum):
    try:
        user = User.query.filter_by(user_alnum=user_alnum).first()
        if user:
            return jsonify({
                'user_alnum': user.user_alnum,
                'name': user.name, # Matches your 'name' column
                'role': user.role
            }), 200
    except:
        pass
    return jsonify({'name': user_alnum}), 200

@employee_today.route("/api/abr", methods=["GET"])
def get_abr_data():
    try:
        result = db.session.execute(text("SELECT name, rate, applies_to FROM abr"))
        return jsonify([{'name': r.name, 'rate': float(r.rate), 'applies_to': r.applies_to} for r in result]), 200
    except:
        return jsonify([]), 200