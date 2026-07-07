import requests
import json
from app import inventory_db, InventoryItem


class OpenFoodFactsService:
    BASE_URL = "https://world.openfoodfacts.org/api/v0"
    
    @staticmethod
    def get_product_by_barcode(barcode):
        try:
            url = f"{OpenFoodFactsService.BASE_URL}/product/{barcode}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 1 and data.get('product'):
                p = data['product']
                categories = p.get('categories', '')
                return {
                    'name': p.get('product_name', ''),
                    'brand': p.get('brands', ''),
                    'description': p.get('ingredients_text', ''),
                    'category': categories.split(',')[0].strip() if categories else '',
                    'barcode': barcode
                }
            return None
            
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"OpenFoodFacts error: {e}")
            return None
    
    @staticmethod
    def search_products_by_name(name):
        try:
            params = {'search_terms': name, 'page_size': 5}
            response = requests.get(
                f"{OpenFoodFactsService.BASE_URL}/search", 
                params=params, 
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if data.get('products'):
                for p in data['products'][:5]:
                    categories = p.get('categories', '')
                    results.append({
                        'name': p.get('product_name', ''),
                        'brand': p.get('brands', ''),
                        'description': p.get('ingredients_text', ''),
                        'category': categories.split(',')[0].strip() if categories else '',
                        'barcode': p.get('code', '')
                    })
            
            return results
            
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Search error: {e}")
            return []


class InventoryService:
    
    @staticmethod
    def get_all_items():
        return [item.to_dict() for item in inventory_db]
    
    @staticmethod
    def get_item_by_id(item_id):
        for item in inventory_db:
            if item.id == item_id:
                return item.to_dict()
        return None
    
    @staticmethod
    def create_item(data):
        item = InventoryItem(
            name=data.get('name'),
            price=data.get('price', 0),
            quantity=data.get('quantity', 0),
            barcode=data.get('barcode'),
            brand=data.get('brand'),
            description=data.get('description'),
            category=data.get('category')
        )
        inventory_db.append(item)
        return item.to_dict()
    
    @staticmethod
    def update_item(item_id, data):
        for item in inventory_db:
            if item.id == item_id:
                item.update(**data)
                return item.to_dict()
        return None
    
    @staticmethod
    def delete_item(item_id):
        for idx, item in enumerate(inventory_db):
            if item.id == item_id:
                return inventory_db.pop(idx).to_dict()
        return None
    
    @staticmethod
    def add_product_from_barcode(barcode, quantity=1, price=None):
        product = OpenFoodFactsService.get_product_by_barcode(barcode)
        if not product:
            return None
        
        item_data = {
            'name': product.get('name', 'Unknown'),
            'price': price if price else 9.99,
            'quantity': quantity,
            'barcode': barcode,
            'brand': product.get('brand', ''),
            'description': product.get('description', ''),
            'category': product.get('category', '')
        }
        
        return InventoryService.create_item(item_data)