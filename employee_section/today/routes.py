from flask import Blueprint, request, jsonify
from models.user import db
from models.activity import Activity
from models.abr import ABR  # Assuming you have this model
from models.user import User  # Assuming you have this model
import string
import random

# Create the blueprint
employee_today = Blueprint('employee_today', __name__)

# Helper to generate ACT-ID if not using the one from utils
def generate_act_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Existing routes
@employee_today.route("/api/employee/today/<string:user_alnum>", methods=["GET"])
def get_activities(user_alnum):
    """Get today's activities for a specific employee"""
    activities = Activity.query.filter_by(created_by=user_alnum).all()
    return jsonify([a.to_dict() for a in activities]), 200

@employee_today.route("/api/employee/today", methods=["POST"])
def add_activity():
    """Add a new activity"""
    data = request.get_json()
    try:
        new_act = Activity(
            activity_id=f"ACT-{generate_act_id()}",
            activity=data.get('activity'),
            qty=data.get('qty'),
            items=data.get('items', ''),
            rate_rule=data.get('rate_rule', ''),
            amount=data.get('amount'),
            comment=data.get('comment', ''),
            created_by=data.get('created_by'),
            sole_type=data.get('sole_type', 'D2')  # New field
        )
        db.session.add(new_act)
        db.session.commit()
        return jsonify(new_act.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@employee_today.route("/api/employee/today/delete/<string:act_id>", methods=["DELETE"])
def delete_activity(act_id):
    """Delete an activity by ID"""
    activity = Activity.query.filter_by(activity_id=act_id).first()
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    
    db.session.delete(activity)
    db.session.commit()
    return jsonify({"message": "Deleted", "activity_id": act_id}), 200

# NEW ROUTES for the updated frontend

@employee_today.route("/api/abr", methods=["GET"])
def get_abr_data():
    """Get all ABR (Activity Based Rates) data"""
    try:
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