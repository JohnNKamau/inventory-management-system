import requests
import json
import argparse

BASE_URL = "http://localhost:5000"

def list_items():
    resp = requests.get(f"{BASE_URL}/inventory")
    if resp.status_code == 200:
        items = resp.json()
        for item in items:
            print(f"{item['id']}: {item['name']} - ${item['price']} (stock: {item['stock']})")
    else:
        print("Error fetching items")

def view_item(item_id):
    resp = requests.get(f"{BASE_URL}/inventory/{item_id}")
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=2))
    else:
        print("Item not found")

def add_item(name, price, stock, brand="", ingredients=""):
    payload = {"name": name, "price": price, "stock": stock, "brand": brand, "ingredients": ingredients}
    resp = requests.post(f"{BASE_URL}/inventory", json=payload)
    if resp.status_code == 201:
        print("Item added:", resp.json())
    else:
        print("Error:", resp.json())

def update_item(item_id, **kwargs):
    payload = {k: v for k, v in kwargs.items() if v is not None}
    resp = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)
    if resp.status_code == 200:
        print("Item updated:", resp.json())
    else:
        print("Error:", resp.json())

def delete_item(item_id):
    resp = requests.delete(f"{BASE_URL}/inventory/{item_id}")
    if resp.status_code == 200:
        print("Item deleted")
    else:
        print("Error:", resp.json())

def fetch_and_add(barcode=None, name=None, price=0.0, stock=0):
    payload = {}
    if barcode:
        payload["barcode"] = barcode
    elif name:
        payload["name"] = name
    else:
        print("Provide either barcode or name")
        return
    payload["price"] = price
    payload["stock"] = stock
    resp = requests.post(f"{BASE_URL}/fetch", json=payload)
    if resp.status_code == 201:
        print("Fetched and added:", resp.json())
    else:
        print("Error:", resp.json())

def main():
    parser = argparse.ArgumentParser(description="Inventory CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List all items")

    view_parser = subparsers.add_parser("view", help="View item details")
    view_parser.add_argument("id", type=int, help="Item ID")

    add_parser = subparsers.add_parser("add", help="Add new item")
    add_parser.add_argument("name", help="Product name")
    add_parser.add_argument("price", type=float, help="Price")
    add_parser.add_argument("stock", type=int, help="Stock quantity")
    add_parser.add_argument("--brand", default="", help="Brand")
    add_parser.add_argument("--ingredients", default="", help="Ingredients")

    update_parser = subparsers.add_parser("update", help="Update item")
    update_parser.add_argument("id", type=int, help="Item ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--brand", help="New brand")
    update_parser.add_argument("--ingredients", help="New ingredients")
    update_parser.add_argument("--price", type=float, help="New price")
    update_parser.add_argument("--stock", type=int, help="New stock")

    delete_parser = subparsers.add_parser("delete", help="Delete item")
    delete_parser.add_argument("id", type=int, help="Item ID")

    fetch_parser = subparsers.add_parser("fetch", help="Fetch from OpenFoodFacts and add")
    fetch_parser.add_argument("--barcode", help="Barcode to fetch")
    fetch_parser.add_argument("--name", help="Product name to search")
    fetch_parser.add_argument("--price", type=float, default=0.0, help="Manual price")
    fetch_parser.add_argument("--stock", type=int, default=0, help="Manual stock")

    args = parser.parse_args()

    if args.command == "list":
        list_items()
    elif args.command == "view":
        view_item(args.id)
    elif args.command == "add":
        add_item(args.name, args.price, args.stock, args.brand, args.ingredients)
    elif args.command == "update":
        update_item(args.id, name=args.name, brand=args.brand, ingredients=args.ingredients, price=args.price, stock=args.stock)
    elif args.command == "delete":
        delete_item(args.id)
    elif args.command == "fetch":
        fetch_and_add(args.barcode, args.name, args.price, args.stock)

if __name__ == "__main__":
    main()