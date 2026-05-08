from flask import Blueprint, jsonify, request
from datetime import datetime
from bson.objectid import ObjectId
from source.models.model import MongoDB
import uuid

mongo = MongoDB()
cart_routes = Blueprint("cart_routes", __name__, url_prefix="/api")

@cart_routes.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    try:
        cart_collection = mongo.cart

        data = request.json

        if not data:
            return jsonify({"success": False, "message": "No data received"}), 400

        # Validate required fields
        required_fields = ["product_id", "email"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "message": f"{field} is required"}), 400

        # Prepare cart document
        cart_item = {
            "product_id": data.get("product_id"),
            "name": data.get("name"),
            "slug": data.get("slug"),
            "hindi_name": data.get("hindi_name"),
            "category": data.get("category"),
            "subcategory": data.get("subcategory"),
            "store_type": data.get("store_type"),
            "price": float(data.get("price", 0)),
            "selected_weight": data.get("selected_weight"),
            "image_url": data.get("image_url"),
            "in_stock": bool(data.get("in_stock", True)),
            "email": data.get("email"),
            "quantity": int(data.get("quantity", 1)),
            "added_to_cart": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Check if product already exists in cart
        existing_item = cart_collection.find_one({
            "product_id": data.get("product_id"),
            "email": data.get("email")
        })

        if existing_item:
            # Increase quantity instead of duplicate insert
            cart_collection.update_one(
                {"_id": existing_item["_id"]},
                {
                    "$inc": {"quantity": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        else:
            cart_collection.insert_one(cart_item)

        return jsonify({
            "success": True,
            "message": "Product added to cart"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
        
@cart_routes.route("/cart_info", methods=["POST"])
def cart_info():
    try:
        cart_collection = mongo.cart
        email = request.json.get("email")

        if not email:
            return jsonify({
                "success": False,
                "message": "Email is required"
            }), 400

        cart_items = list(cart_collection.find({"email": email}))

        formatted_items = []

        for item in cart_items:
            item["_id"] = str(item["_id"])

            # Ensure correct numeric types
            quantity = int(item.get("quantity", 1))
            price = float(item.get("price", 0))

            # Add total field
            item["total"] = quantity * price

            formatted_items.append(item)

        return jsonify({
            "success": True,
            "cart_items": formatted_items
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@cart_routes.route("/increase_quantity", methods=["POST"])
def increase_quantity():
    try:
        cart_collection = mongo.cart

        data = request.json
        email = data.get("email")
        item_id = data.get("item_id")

        if not email or not item_id:
            return jsonify({
                "success": False,
                "message": "Email and item_id are required"
            }), 400

        result = cart_collection.update_one(
            {
                "_id": ObjectId(item_id),
                "email": email
            },
            {
                "$inc": {"quantity": 1}
            }
        )

        if result.modified_count == 0:
            return jsonify({
                "success": False,
                "message": "Item not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Quantity increased"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@cart_routes.route("/decrease_quantity", methods=["POST"])
def decrease_quantity():
    try:
        cart_collection = mongo.cart

        data = request.json
        email = data.get("email")
        item_id = data.get("item_id")

        if not email or not item_id:
            return jsonify({
                "success": False,
                "message": "Email and item_id are required"
            }), 400

        item = cart_collection.find_one({
            "_id": ObjectId(item_id),
            "email": email
        })

        if not item:
            return jsonify({
                "success": False,
                "message": "Item not found"
            }), 404

        if item["quantity"] <= 1:
            return jsonify({
                "success": False,
                "message": "Quantity cannot be less than 1"
            }), 400

        cart_collection.update_one(
            {
                "_id": ObjectId(item_id),
                "email": email
            },
            {
                "$inc": {"quantity": -1}
            }
        )

        return jsonify({
            "success": True,
            "message": "Quantity decreased"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
        
@cart_routes.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    try:
        cart_collection = mongo.cart

        data = request.json
        email = data.get("email")
        item_id = data.get("item_id")

        if not email or not item_id:
            return jsonify({
                "success": False,
                "message": "Email and item_id are required"
            }), 400

        result = cart_collection.delete_one({
            "_id": ObjectId(item_id),
            "email": email
        })

        if result.deleted_count == 0:
            return jsonify({
                "success": False,
                "message": "Item not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Item removed from cart"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
        
@cart_routes.route("/clear_cart", methods=["POST"])
def clear_cart():
    try:
        email = request.json.get("email")

        mongo.cart.delete_many({"email": email})

        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
@cart_routes.route("/place_order", methods=["POST"])
def place_order():
    try:
        data = request.json

        email = data.get("email")
        address = data.get("address")
        payment_method = data.get("payment_method")

        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400

        # Fetch cart items
        cart_items = list(mongo.cart.find({"email": email}))

        if not cart_items:
            return jsonify({"success": False, "message": "Cart is empty"}), 400

        # Generate Order ID
        order_id = f"SDF{int(datetime.utcnow().timestamp())}"

        # Calculate totals
        subtotal = sum(item["price"] * item["quantity"] for item in cart_items)
        shipping_fee = 0 if subtotal >= 500 else 50
        total = subtotal + shipping_fee

        # Prepare order items
        order_items = []
        for item in cart_items:
            order_items.append({
                "product_id": item.get("product_id"),
                "product_name": item.get("name"),
                "quantity": item.get("quantity"),
                "price": item.get("price"),
                "weight": item.get("selected_weight"),
                "total": item.get("price") * item.get("quantity")
            })

        # Create order document
        order_doc = {
            "order_id": order_id,
            "email": email,
            "items": order_items,
            "subtotal": subtotal,
            "shipping_fee": shipping_fee,
            "total": total,
            "shipping_details": address,
            "payment_method": payment_method,
            "payment_status": "pending",
            "order_status": "placed",
            "created_at": datetime.utcnow()
        }

        # Insert into orders collection
        mongo.orders.insert_one(order_doc)

        # Clear cart after order
        mongo.cart.delete_many({"email": email})

        return jsonify({
            "success": True,
            "order_id": order_id
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500