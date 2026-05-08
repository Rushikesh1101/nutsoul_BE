from flask import Blueprint, jsonify, request
from datetime import datetime
from source.models.model import MongoDB
import uuid

mongo = MongoDB()
add_address_routes = Blueprint("add_address_routes", __name__, url_prefix="/api")


@add_address_routes.route("/add_address", methods=["POST"])
def add_address():
    """
    Save a user's address in MongoDB.
    Expects JSON:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "role": "customer",
        "label": "Home",
        "phone": "9876543210",
        "address_line1": "...",
        "address_line2": "...",
        "city": "...",
        "state": "...",
        "pincode": "...",
        "is_default": false
    }
    """
    data = request.get_json()

    required_fields = ["name", "email", "role", "address_line1", "city", "state", "pincode"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing fields: {', '.join(missing)}"}), 400

    address_collection = mongo.db["address"]

    address_doc = {
        "_id": str(uuid.uuid4()),  # unique ID
        "name": data["name"],
        "email": data["email"],
        "role": data["role"],
        "label": data.get("label", "Home"),
        "phone": data.get("phone", ""),
        "address_line1": data["address_line1"],
        "address_line2": data.get("address_line2", ""),
        "city": data["city"],
        "state": data["state"],
        "pincode": data["pincode"],
        "is_default": data.get("is_default", False),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    try:
        address_collection.insert_one(address_doc)
        return jsonify({"success": True, "message": "Address added", "address": address_doc}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
    
@add_address_routes.route("/delete_address/<address_id>", methods=["DELETE"])
def delete_address(address_id):
    """
    Delete a user's address by _id.
    URL param: address_id (the _id of the address to delete)
    """
    address_collection = mongo.db["address"]

    try:
        result = address_collection.delete_one({"_id": address_id})
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Address not found"}), 404

        return jsonify({"success": True, "message": "Address deleted"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@add_address_routes.route("/get_addresses", methods=["GET"])
def get_addresses():
    """
    Fetch all addresses for the logged-in user.
    Expects query param: email
    Example: /api/get_addresses?email=john@example.com
    """
    email = request.args.get("email")
    if not email:
        return jsonify({"success": False, "error": "Email is required"}), 400

    address_collection = mongo.db["address"]

    try:
        user_addresses = list(address_collection.find({"email": email}))
        # Convert MongoDB _id ObjectId to string and match frontend key `id`
        for addr in user_addresses:
            addr["id"] = addr["_id"]
        return jsonify({"success": True, "addresses": user_addresses}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500