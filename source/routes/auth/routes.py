from flask import (
    send_file,
    Blueprint,
    request,
    jsonify,
    current_app,
    session,
    make_response,
)
from source.models.model import MongoDB
from werkzeug.security import generate_password_hash, check_password_hash
from source.utils import utils
from flask_jwt_extended import create_access_token
from io import BytesIO
import openpyxl
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter, quote_sheetname
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl import load_workbook
from datetime import datetime, timedelta
import jwt, random
import io
import io
import random
import string
import base64
from io import BytesIO

mongo = MongoDB()

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return (
            jsonify({"success": False, "message": "Email and password required."}),
            400,
        )

    user = mongo.users.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Invalid credentials."}), 401

    payload = {
        "email": email,
        "role": user.get("role", "customer"),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

    # access_token = create_access_token(identity=email)
    return (
        jsonify(
            {
                "success": True,
                "message": "Login successful.",
                "token": token,
                "user": {
                    "email": user["email"],
                    "name": user.get("name", ""),
                    "role": user.get("role", ""),
                },
            }
        ),
        200,
    )


@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")

        # Basic validation
        if not name or not email or not password:
            return jsonify({"error": "Required fields missing"}), 400

        # Check if user already exists
        existing_user = mongo.users.find_one({"email": email})
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create user object
        new_user = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": hashed_password,
            "role": "customer",
            "created_at": datetime.utcnow(),
        }

        # Insert into DB
        result = mongo.users.insert_one(new_user)

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user_id": str(result.inserted_id),
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @auth_bp.route("/forgot_password", methods=["POST"])
# def forgot_password():
#     data = request.get_json()
#     email = data.get("email")
#     new_password = data.get("new_password")

#     user = mongo.users.find_one({"email": email})

#     if not user:
#         return jsonify(success=False, message="Email not found"), 404

#     if new_password:
#         print(".....new_password..............")
#         hashed_password = generate_password_hash(new_password)
#         mongo.users.update_one(
#             {"email": email}, {"$set": {"password": hashed_password}}
#         )
#         return jsonify(success=True, message="Password updated successfully")

#     return jsonify(success=True, message="Email exists")
