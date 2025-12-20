from flask import Blueprint, request, jsonify
from models.user import db
from models.activity import Activity
import string
import random

employee_today = Blueprint('employee_today', __name__)

# Helper to generate ACT-ID if not using the one from utils
def generate_act_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@employee_today.route("/api/employee/today/<string:user_alnum>", methods=["GET"])
def get_activities(user_alnum):
    activities = Activity.query.filter_by(created_by=user_alnum).all()
    return jsonify([a.to_dict() for a in activities]), 200

@employee_today.route("/api/employee/today", methods=["POST"])
def add_activity():
    data = request.get_json()
    try:
        new_act = Activity(
            activity_id=f"ACT-{generate_act_id()}",
            activity=data.get('activity'),
            qty=data.get('qty'),
            items=data.get('items'),
            rate_rule=data.get('rate_rule'),
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

@employee_today.route("/api/employee/today/delete/<string:act_id>", methods=["DELETE"])
def delete_activity(act_id):
    activity = Activity.query.filter_by(activity_id=act_id).first()
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    
    db.session.delete(activity)
    db.session.commit()
    return jsonify({"message": "Deleted", "activity_id": act_id}), 200