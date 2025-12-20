from flask import Blueprint, request, jsonify
from models.user import db, User
from utils.helpers import generate_user_alnum
from werkzeug.security import generate_password_hash

admin_users = Blueprint('admin_users', __name__)

@admin_users.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "user_alnum": u.user_alnum,
        "name": u.name,
        "username": u.username_email,
        "role": u.role,
        "team": u.team,
        "status": u.status
    } for u in users]), 200

@admin_users.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    
    if User.query.filter_by(username_email=data.get("username")).first():
        return jsonify({"error": "User already exists"}), 400

    new_user = User(
        user_alnum=generate_user_alnum(),
        name=data["name"],
        username_email=data["username"],
        password=generate_password_hash(data["name"]),
        role=data["role"],
        status=data.get("status", "Active"),
        team=data.get("team")
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Return the full object so React can update state immediately
    return jsonify({
        "id": new_user.id,
        "user_alnum": new_user.user_alnum,
        "name": new_user.name,
        "username": new_user.username_email,
        "role": new_user.role,
        "team": new_user.team,
        "status": new_user.status
    }), 201

@admin_users.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200