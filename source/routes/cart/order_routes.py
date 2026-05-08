from flask import Blueprint, jsonify, request
from datetime import datetime
from bson.objectid import ObjectId
from source.models.model import MongoDB
import uuid

mongo = MongoDB()
ordered_routes = Blueprint("ordered_routes", __name__, url_prefix="/api")

@ordered_routes.route("/order_confirm", methods=["GET"])
def get_order():
    """
    Fetch order details by order_id (or _id) and user email.
    Example: /api/order_confirm?order_id=123&email=john@example.com
    """
    order_id = request.args.get("order_id")
    email = request.args.get("email")

    if not order_id or not email:
        return jsonify({"success": False, "error": "order_id and email are required"}), 400

    try:
        orders_collection = mongo.db["orders"]

        # Check if order_id looks like ObjectId
        try:
            obj_id = ObjectId(order_id)
            query = {"_id": obj_id, "email": email}
        except:
            # Fallback if order_id is not an ObjectId (like a custom order_id string)
            query = {"order_id": order_id, "email": email}

        order = orders_collection.find_one(query)

        if not order:
            return jsonify({"success": False, "error": "Order not found"}), 404

        # Convert ObjectId to string
        order["_id"] = str(order["_id"])

        # Optional: rename _id to id for frontend consistency
        order["id"] = order["_id"]

        return jsonify({"success": True, "order": order}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500