from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from source.models.model import MongoDB

mongo = MongoDB()
admin_routes = Blueprint("admin_routes", __name__, url_prefix="/api")

@admin_routes.route("/products", methods=["GET"])
def get_products():
    items_collection = mongo.db["items"]
    products = list(items_collection.find())

    formatted_products = []

    for item in products:
        formatted_products.append({
            "_id": str(item.get("_id")),
            "name": item.get("name"),
            "slug": item.get("slug"),
            "hindi_name": item.get("hindi_name"),
            "description": item.get("description"),
            "short_description": item.get("short_description"),
            "category": item.get("category"),
            "subcategory": item.get("subcategory"),
            "store_type": item.get("store_type"),
            "price_100g": item.get("price_100g"),
            "price_250g": item.get("price_250g"),
            "price_500g": item.get("price_500g"),
            "price_1kg": item.get("price_1kg"),
            "in_stock": bool(item.get("in_stock", True)),  # ✅ FORCE BOOLEAN
            "image_url": request.host_url + item.get("image_path", ""),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
        })

    return jsonify({
        "success": True,
        "products": formatted_products
    }), 200
    
@admin_routes.route("/products/<id>/stock", methods=["PUT"])
def update_stock(id):
    items_collection = mongo.db["items"]
    data = request.json

    items_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"in_stock": data.get("in_stock", True)}}
    )

    return jsonify({"success": True}), 200

@admin_routes.route("/products/<id>", methods=["DELETE"])
def delete_product(id):
    items_collection = mongo.db["items"]

    items_collection.delete_one({"_id": ObjectId(id)})

    return jsonify({"success": True}), 200