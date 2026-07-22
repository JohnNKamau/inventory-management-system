import pytest
import json
from app import app, inventory
import requests
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_all_items(client):
    resp = client.get('/inventory')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2

def test_get_item(client):
    resp = client.get('/inventory/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['name'] == 'Organic Almond Milk'

def test_get_item_not_found(client):
    resp = client.get('/inventory/999')
    assert resp.status_code == 404

def test_add_item(client):
    payload = {"name": "Test", "price": 1.99, "stock": 5}
    resp = client.post('/inventory', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['id'] == 3
    assert data['name'] == 'Test'
    assert len(inventory) == 3

def test_add_item_missing_fields(client):
    resp = client.post('/inventory', json={"name": "Test"})
    assert resp.status_code == 400

def test_update_item(client):
    resp = client.patch('/inventory/1', json={"price": 4.99})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['price'] == 4.99

def test_update_item_not_found(client):
    resp = client.patch('/inventory/999', json={"price": 1.99})
    assert resp.status_code == 404

def test_delete_item(client):
    resp = client.delete('/inventory/1')
    assert resp.status_code == 200
    assert len(inventory) == 2

def test_delete_item_not_found(client):
    resp = client.delete('/inventory/999')
    assert resp.status_code == 404

@patch('app.requests.get')
def test_fetch_and_add_by_barcode(mock_get, client):
    mock_response = {
        "status": 1,
        "product": {
            "product_name": "Mock Product",
            "brands": "MockBrand",
            "ingredients_text": "Mock ingredients"
        }
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    payload = {"barcode": "1234567890", "price": 5.99, "stock": 3}
    resp = client.post('/fetch', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['name'] == 'Mock Product'
    assert data['brand'] == 'MockBrand'

@patch('app.requests.get')
def test_fetch_and_add_by_name(mock_get, client):
    mock_response = {
        "products": [
            {"product_name": "Search Product", "brands": "SearchBrand", "ingredients_text": "Search ingredients"}
        ]
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    payload = {"name": "search term", "price": 2.99, "stock": 8}
    resp = client.post('/fetch', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['name'] == 'Search Product'
    assert data['brand'] == 'SearchBrand'