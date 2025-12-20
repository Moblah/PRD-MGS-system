from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models.user import User

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    # Querying by username_email as per your model
    user = User.query.filter_by(username_email=username).first()

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    if user.status.lower() != "active":
        return jsonify({"message": "Account inactive"}), 403

    # We wrap user details in a 'user' key so React's data.user works
    return jsonify({
        "message": "Login successful",
        "role": user.role,
        "user": {
            "user_alnum": user.user_alnum,
            "name": user.name,
            "username": user.username_email
        }
    }), 200