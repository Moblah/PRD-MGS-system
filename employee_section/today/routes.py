from flask import Blueprint, request, jsonify
from models.user import db
from models.activity import Activity
import string
import random

employee_today = Blueprint('employee_today', __name__)

# ADD THESE 2 ROUTES TO YOUR BACKEND

@employee_today.route("/api/abr", methods=["GET"])
def get_abr_data():
    """Temporary hardcoded data - replace with database query later"""
    try:
        # For now, return hardcoded data
        abr_data = [
            {"name": "Survey Drawing", "rate": 100, "applies_to": "D2"},
            {"name": "Survey Verification", "rate": 80, "applies_to": "D2"},
            {"name": "Survey Masterfile", "rate": 120, "applies_to": "D2"},
            {"name": "Registration D2", "rate": 150, "applies_to": "D2"},
            {"name": "Registration PN", "rate": 180, "applies_to": "PN"},
            {"name": "Uploading Bulk", "rate": 90, "applies_to": "D2"},
            {"name": "Uploading single file", "rate": 50, "applies_to": "D2"}
        ]
        return jsonify(abr_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@employee_today.route("/api/users/<string:user_alnum>", methods=["GET"])
def get_user_by_alnum(user_alnum):
    """Get user details - return basic info for now"""
    try:
        # For now, just return the alnum as the name
        # Later you can query your User table
        return jsonify({
            'user_alnum': user_alnum,
            'full_name': user_alnum,  # Just use alnum as name for now
            'email': 'user@example.com',
            'role': 'employee'
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500