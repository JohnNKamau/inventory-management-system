from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import uuid
from datetime import datetime
from services import InventoryService, OpenFoodFactsService


class InventoryItem:
    def __init__(self, name, price, quantity, barcode=None, 
                 brand=None, description=None, category=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.price = float(price)
        self.quantity = int(quantity)
        self.barcode = barcode
        self.brand = brand
        self.description = description
        self.category = category
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'barcode': self.barcode,
            'brand': self.brand,
            'description': self.description,
            'category': self.category,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                if key == 'price':
                    setattr(self, key, float(value))
                elif key == 'quantity':
                    setattr(self, key, int(value))
                else:
                    setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
        return self


inventory_db = []

def initialize_sample_data():
    if not inventory_db:
        items = [
            InventoryItem("Organic Almond Milk", 4.99, 50, "1234567890123", 
                         "Silk", "Unsweetened organic almond milk", "Beverages"),
            InventoryItem("Whole Wheat Bread", 3.49, 30, "9876543210987", 
                         "Nature's Own", "100% whole wheat bread", "Bakery"),
            InventoryItem("Greek Yogurt", 5.99, 25, "4567890123456", 
                         "Chobani", "Plain Greek yogurt, 32oz", "Dairy")
        ]
        inventory_db.extend(items)


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    bp = Blueprint('inventory', __name__)
    
    @bp.route('/inventory', methods=['GET'])
    def get_all_items():
        items = InventoryService.get_all_items()
        return jsonify({'status': 'success', 'data': items, 'count': len(items)}), 200
    
    @bp.route('/inventory/<item_id>', methods=['GET'])
    def get_item(item_id):
        item = InventoryService.get_item_by_id(item_id)
        if not item:
            return jsonify({'status': 'error', 'message': 'Item not found'}), 404
        return jsonify({'status': 'success', 'data': item}), 200
    
    @bp.route('/inventory', methods=['POST'])
    def create_item():
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'status': 'error', 'message': 'Name is required'}), 400
        try:
            item = InventoryService.create_item(data)
            return jsonify({'status': 'success', 'data': item, 
                          'message': 'Item created'}), 201
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @bp.route('/inventory/<item_id>', methods=['PATCH'])
    def update_item(item_id):
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        item = InventoryService.update_item(item_id, data)
        if not item:
            return jsonify({'status': 'error', 'message': 'Item not found'}), 404
        return jsonify({'status': 'success', 'data': item, 
                      'message': 'Item updated'}), 200
    
    @bp.route('/inventory/<item_id>', methods=['DELETE'])
    def delete_item(item_id):
        deleted = InventoryService.delete_item(item_id)
        if not deleted:
            return jsonify({'status': 'error', 'message': 'Item not found'}), 404
        return jsonify({'status': 'success', 'data': deleted, 
                      'message': 'Item deleted'}), 200
    
    @bp.route('/inventory/search', methods=['GET'])
    def search_items():
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({'status': 'error', 'message': 'Search query required'}), 400
        
        results = []
        for item in inventory_db:
            if (query in item.name.lower() or 
                (item.barcode and query in item.barcode) or
                (item.brand and query in item.brand.lower())):
                results.append(item.to_dict())
        
        return jsonify({'status': 'success', 'data': results, 'count': len(results)}), 200
    
    @bp.route('/openfoodfacts/barcode/<barcode>', methods=['GET'])
    def get_product_by_barcode(barcode):
        product = OpenFoodFactsService.get_product_by_barcode(barcode)
        if not product:
            return jsonify({'status': 'error', 'message': 'Product not found'}), 404
        return jsonify({'status': 'success', 'data': product}), 200
    
    @bp.route('/openfoodfacts/search', methods=['GET'])
    def search_openfoodfacts():
        query = request.args.get('q', '')
        if not query:
            return jsonify({'status': 'error', 'message': 'Search query required'}), 400
        products = OpenFoodFactsService.search_products_by_name(query)
        return jsonify({'status': 'success', 'data': products, 'count': len(products)}), 200
    
    @bp.route('/inventory/from-barcode', methods=['POST'])
    def add_item_from_barcode():
        data = request.get_json()
        if not data or not data.get('barcode'):
            return jsonify({'status': 'error', 'message': 'Barcode required'}), 400
        
        item = InventoryService.add_product_from_barcode(
            data.get('barcode'), 
            data.get('quantity', 1), 
            data.get('price')
        )
        if not item:
            return jsonify({'status': 'error', 'message': 'Failed to add item'}), 404
        return jsonify({'status': 'success', 'data': item, 
                      'message': 'Item added from OpenFoodFacts'}), 201
    
    app.register_blueprint(bp, url_prefix='/api')
    return app