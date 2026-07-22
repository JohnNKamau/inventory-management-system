from flask import Flask, request, jsonify

app = Flask(__name__)

inventory = [
    {"id": 1, "name": "Organic Almond Milk", "brand": "Silk", "ingredients": "Filtered water, almonds, cane sugar", "price": 3.99, "stock": 10},
    {"id": 2, "name": "Whole Wheat Bread", "brand": "Nature's Own", "ingredients": "Whole wheat flour, water, yeast", "price": 2.49, "stock": 5}
]

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

if __name__ == "__main__":
    app.run(debug=True)