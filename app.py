from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

inventory = [
    {"id": 1, "name": "Organic Almond Milk", "brand": "Silk", "ingredients": "Filtered water, almonds, cane sugar", "price": 3.99, "stock": 10},
    {"id": 2, "name": "Whole Wheat Bread", "brand": "Nature's Own", "ingredients": "Whole wheat flour, water, yeast", "price": 2.49, "stock": 5}
]

def fetch_product_details(barcode_or_name):
    if barcode_or_name.isdigit():
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_or_name}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                product = data.get("product", {})
                return {
                    "name": product.get("product_name", "Unknown"),
                    "brand": product.get("brands", "Unknown"),
                    "ingredients": product.get("ingredients_text", "")
                }
    else:
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": barcode_or_name,
            "search_simple": 1,
            "json": 1,
            "page_size": 1
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            if products:
                product = products[0]
                return {
                    "name": product.get("product_name", "Unknown"),
                    "brand": product.get("brands", "Unknown"),
                    "ingredients": product.get("ingredients_text", "")
                }
    return None

# ---- CRUD endpoints ----

@app.route('/inventory', methods=['GET'])
def get_all_items():
    return jsonify(inventory)

@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((i for i in inventory if i["id"] == item_id), None)
    if item:
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

@app.route('/inventory', methods=['POST'])
def add_item():
    data = request.get_json()
    required = ["name", "price", "stock"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    new_id = max([i["id"] for i in inventory], default=0) + 1
    new_item = {
        "id": new_id,
        "name": data["name"],
        "brand": data.get("brand", ""),
        "ingredients": data.get("ingredients", ""),
        "price": data["price"],
        "stock": data["stock"]
    }
    inventory.append(new_item)
    return jsonify(new_item), 201

@app.route('/inventory/<int:item_id>', methods=['PATCH'])
def update_item(item_id):
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    data = request.get_json()
    allowed = ["name", "brand", "ingredients", "price", "stock"]
    for key in allowed:
        if key in data:
            item[key] = data[key]
    return jsonify(item)

@app.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global inventory
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    inventory = [i for i in inventory if i["id"] != item_id]
    return jsonify({"message": "Item deleted"}), 200

# ---- NEW: External API endpoint ----

@app.route('/fetch', methods=['POST'])
def fetch_and_add():
    data = request.get_json()
    if "barcode" not in data and "name" not in data:
        return jsonify({"error": "Provide 'barcode' or 'name'"}), 400
    query = data.get("barcode") or data.get("name")
    details = fetch_product_details(query)
    if not details:
        return jsonify({"error": "Product not found"}), 404
    new_id = max([i["id"] for i in inventory], default=0) + 1
    new_item = {
        "id": new_id,
        "name": details["name"],
        "brand": details["brand"],
        "ingredients": details["ingredients"],
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0)
    }
    inventory.append(new_item)
    return jsonify(new_item), 201

if __name__ == "__main__":
    app.run(debug=True)