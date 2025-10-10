from flask import Blueprint, request, jsonify
from models import User
from app import db
from datetime import datetime

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    provider = data.get("provider")
    username = data.get("username")

    user = User.query.filter_by(email=email).first()
    if user:
        user.created_at = datetime.utcnow()
        db.session.commit()
    else:
        new_user = User(email=email, username=username, provider=provider)
        db.session.add(new_user)
        db.session.commit()

    return jsonify({"message": "Login successfull"}), 200
