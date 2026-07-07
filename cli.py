import click
import requests

API_URL = "http://localhost:5000/api"

# Terminal colors
C = {
    'h': '\033[95m', 'b': '\033[94m', 'g': '\033[92m',
    'y': '\033[93m', 'r': '\033[91m', 'e': '\033[0m',
    'bold': '\033[1m'
}

def pheader(text):
    click.echo(f"\n{C['h']}{C['bold']}{'='*60}{C['e']}")
    click.echo(f"{C['h']}{C['bold']}{text.center(60)}{C['e']}")
    click.echo(f"{C['h']}{C['bold']}{'='*60}{C['e']}\n")

def psuccess(text):
    click.echo(f"{C['g']}✓ {text}{C['e']}")

def perror(text):
    click.echo(f"{C['r']}✗ {text}{C['e']}")

def pinfo(text):
    click.echo(f"{C['b']}ℹ {text}{C['e']}")

def show_item(item):
    click.echo(f"\n{C['bold']}ID:{C['e']} {item.get('id', 'N/A')}")
    click.echo(f"{C['bold']}Name:{C['e']} {item.get('name', 'N/A')}")
    click.echo(f"{C['bold']}Price:{C['e']} ${item.get('price', 0):.2f}")
    click.echo(f"{C['bold']}Qty:{C['e']} {item.get('quantity', 0)}")
    for field in ['brand', 'barcode', 'category']:
        if item.get(field):
            click.echo(f"{C['bold']}{field.title()}:{C['e']} {item.get(field)}")

def parse_response(resp):
    try:
        data = resp.json()
        if resp.status_code in [200, 201]:
            return data.get('data'), None
        return None, data.get('message', 'Something went wrong')
    except:
        return None, 'Invalid response'

def handle_error(e):
    if isinstance(e, requests.exceptions.ConnectionError):
        perror("Server not running. Start with: python run.py")
    else:
        perror(str(e))

@click.group()
def cli():
    pass

@cli.command()
@click.option('--id', help='Get specific item')
def view(id):
    """View inventory items"""
    try:
        url = f"{API_URL}/inventory/{id}" if id else f"{API_URL}/inventory"
        resp = requests.get(url)
        data, err = parse_response(resp)
        
        if not data:
            perror(err or "No items found")
            return
            
        if id:
            pheader("Item Details")
            show_item(data)
        else:
            pheader(f"Inventory ({len(data)} items)")
            for item in data:
                click.echo(f"{C['bold']}ID:{C['e']} {item['id'][:8]}... | "
                          f"{C['bold']}Name:{C['e']} {item['name']} | "
                          f"{C['bold']}Price:{C['e']} ${item['price']:.2f} | "
                          f"{C['bold']}Qty:{C['e']} {item['quantity']}")
    except Exception as e:
        handle_error(e)

@cli.command()
@click.option('--name', required=True)
@click.option('--price', required=True, type=float)
@click.option('--quantity', required=True, type=int)
@click.option('--barcode')
@click.option('--brand')
@click.option('--category')
@click.option('--description')
def add(name, price, quantity, barcode, brand, category, description):
    """Add item to inventory"""
    try:
        data = {k: v for k, v in locals().items() if v is not None}
        resp = requests.post(f"{API_URL}/inventory", json=data)
        data, err = parse_response(resp)
        
        if data:
            psuccess("Item added!")
            show_item(data)
        else:
            perror(err or "Failed to add item")
    except Exception as e:
        handle_error(e)

@cli.command()
@click.option('--id', required=True)
@click.option('--name')
@click.option('--price', type=float)
@click.option('--quantity', type=int)
@click.option('--barcode')
@click.option('--brand')
@click.option('--category')
@click.option('--description')
def update(id, **kwargs):
    """Update an item"""
    try:
        data = {k: v for k, v in kwargs.items() if v is not None}
        if not data:
            perror("No fields to update")
            return
            
        resp = requests.patch(f"{API_URL}/inventory/{id}", json=data)
        data, err = parse_response(resp)
        
        if data:
            psuccess("Item updated!")
            show_item(data)
        else:
            perror(err or "Update failed")
    except Exception as e:
        handle_error(e)

@cli.command()
@click.option('--id', required=True)
def delete(id):
    """Delete an item"""
    try:
        resp = requests.get(f"{API_URL}/inventory/{id}")
        data, _ = parse_response(resp)
        
        if not data:
            perror("Item not found")
            return
            
        pheader("Delete Confirmation")
        show_item(data)
        
        if click.confirm('\nDelete this item?'):
            resp = requests.delete(f"{API_URL}/inventory/{id}")
            data, err = parse_response(resp)
            psuccess("Deleted!") if data else perror(err or "Delete failed")
        else:
            pinfo("Cancelled")
    except Exception as e:
        handle_error(e)

@cli.command()
@click.option('--barcode', required=True)
def fetch(barcode):
    """Get product from OpenFoodFacts"""
    try:
        resp = requests.get(f"{API_URL}/openfoodfacts/barcode/{barcode}")
        data, err = parse_response(resp)
        
        if not data:
            perror(err or "Product not found")
            return
            
        pheader("OpenFoodFacts Product")
        click.echo(f"{C['bold']}Name:{C['e']} {data.get('name', 'N/A')}")
        click.echo(f"{C['bold']}Brand:{C['e']} {data.get('brand', 'N/A')}")
        click.echo(f"{C['bold']}Category:{C['e']} {data.get('category', 'N/A')}")
        click.echo(f"{C['bold']}Description:{C['e']} {data.get('description', 'N/A')}")
        
        if click.confirm('\nAdd to inventory?'):
            qty = click.prompt('Quantity', type=int, default=1)
            price = click.prompt('Price ($)', type=float, default=9.99)
            
            resp = requests.post(f"{API_URL}/inventory/from-barcode", 
                                json={'barcode': barcode, 'quantity': qty, 'price': price})
            data, err = parse_response(resp)
            
            if data:
                psuccess("Added to inventory!")
                show_item(data)
            else:
                perror(err or "Failed to add")
    except Exception as e:
        handle_error(e)

@cli.command()
@click.option('--query', required=True)
def search(query):
    """Search OpenFoodFacts"""
    try:
        resp = requests.get(f"{API_URL}/openfoodfacts/search?q={query}")
        data, err = parse_response(resp)
        
        if not data:
            pinfo("No products found")
            return
            
        pheader(f"Results ({len(data)})")
        for i, p in enumerate(data, 1):
            click.echo(f"\n{C['bold']}{i}. {C['e']}{p.get('name', 'Unknown')}")
            click.echo(f"   Brand: {p.get('brand', 'N/A')}")
            click.echo(f"   Category: {p.get('category', 'N/A')}")
            if p.get('barcode'):
                click.echo(f"   Barcode: {p.get('barcode')}")
    except Exception as e:
        handle_error(e)

@cli.command()
def help():
    """Show help"""
    pheader("Inventory CLI Help")
    click.echo("""
Commands:
  view [--id ID]           List all or specific item
  add --name N --price P --quantity Q [options]
  update --id ID [options]
  delete --id ID
  fetch --barcode CODE     Get product from OpenFoodFacts
  search --query TERM      Search OpenFoodFacts

Examples:
  python cli.py add --name "Milk" --price 3.99 --quantity 100
  python cli.py view
  python cli.py fetch --barcode 1234567890123
""")

if __name__ == '__main__':
    cli()