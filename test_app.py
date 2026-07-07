import pytest
import json
from unittest.mock import patch
from click.testing import CliRunner
from app import create_app, inventory_db, InventoryItem
from services import InventoryService, OpenFoodFactsService
from cli import cli

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        inventory_db.clear()
        inventory_db.append(InventoryItem("Test", 10.99, 5, "123"))
        yield client

@pytest.fixture
def runner():
    return CliRunner()

def test_api_crud(client):
    r = client.post('/api/inventory', json={'name': 'New', 'price': 15.99, 'quantity': 10})
    assert r.status_code == 201
    id = json.loads(r.data)['data']['id']
    
    assert json.loads(client.get(f'/api/inventory/{id}').data)['data']['name'] == 'New'
    r = client.patch(f'/api/inventory/{id}', json={'price': 20.99})
    assert json.loads(r.data)['data']['price'] == 20.99
    assert client.delete(f'/api/inventory/{id}').status_code == 200

def test_search_and_barcode(client):
    inventory_db.append(InventoryItem("Apple", 1.99, 10))
    r = client.get('/api/inventory/search?q=Apple')
    assert json.loads(r.data)['count'] == 1
    
    with patch('services.requests.get') as mock:
        mock.return_value.json.return_value = {'status': 1, 'product': {'product_name': 'Milk'}}
        r = client.get('/api/openfoodfacts/barcode/123')
        assert json.loads(r.data)['data']['name'] == 'Milk'

@patch('services.requests.get')
def test_services(mock_get):
    inventory_db.clear()
    item = InventoryService.create_item({'name': 'Test', 'price': 9.99, 'quantity': 2})
    assert item['name'] == 'Test'
    
    updated = InventoryService.update_item(item['id'], {'price': 7.99})
    assert updated['price'] == 7.99
    
    mock_get.return_value.json.return_value = {'status': 1, 'product': {'product_name': 'Chocolate'}}
    result = OpenFoodFactsService.get_product_by_barcode('789')
    assert result['name'] == 'Chocolate'

def test_cli(runner):
    # Test view command with proper mock data
    with patch('cli.requests.get') as mock:
        mock.return_value.status_code = 200
        mock.return_value.json.return_value = {
            'status': 'success', 
            'data': [{'id': '123', 'name': 'CLI Test', 'price': 4.99, 'quantity': 5}]
        }
        result = runner.invoke(cli, ['view'])
        assert 'CLI Test' in result.output
        assert 'Inventory' in result.output
    
    # Test add command
    with patch('cli.requests.post') as mock:
        mock.return_value.status_code = 201
        mock.return_value.json.return_value = {
            'status': 'success', 
            'data': {'id': '456', 'name': 'Added', 'price': 12.99, 'quantity': 5}
        }
        r = runner.invoke(cli, ['add', '--name', 'Added', '--price', '12.99', '--quantity', '5'])
        assert 'added' in r.output.lower()
        assert 'Added' in r.output

def test_model():
    item = InventoryItem("Test", 8.99, 3)
    assert item.name == "Test"
    item.update(name="New", price=9.99)
    assert item.name == "New" and item.price == 9.99
    assert 'id' in item.to_dict()