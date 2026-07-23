from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

inventory = [
    {
        "id": 1,
        "name": "Unga Maize Flour 2kg",
        "brand": "Unga",
        "ingredients": "Whole maize flour",
        "price": 185.00,
        "stock": 25
    },
    {
        "id": 2,
        "name": "Brookside Fresh Milk 500ml",
        "brand": "Brookside",
        "ingredients": "Fresh cow's milk",
        "price": 75.00,
        "stock": 40
    },
    {
        "id": 3,
        "name": "Kabras Sugar 2kg",
        "brand": "Kabras",
        "ingredients": "Refined sugar",
        "price": 320.00,
        "stock": 18
    },
    {
        "id": 4,
        "name": "Fresh Fry Cooking Oil 1L",
        "brand": "Fresh Fry",
        "ingredients": "Refined vegetable oil",
        "price": 340.00,
        "stock": 15
    },
    {
        "id": 5,
        "name": "Ketepa Pride Tea Bags",
        "brand": "Ketepa",
        "ingredients": "Premium black tea",
        "price": 210.00,
        "stock": 30
    }
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