from flask import Blueprint, request, jsonify
from models.user import db
from models.activity import Activity
import string
import random

employee_today = Blueprint('employee_today', __name__)
@employee_today.route("/api/abr", methods=["GET"])
def get_abr_data():
    """Get activity rates from ABR table"""
    try:
        # Make sure you have an ABR model
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