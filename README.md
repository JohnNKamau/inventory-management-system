# Inventory Management System

## About

This project is a Flask REST API for managing inventory items. It allows users to create, view, update and delete products. It also connects to the OpenFoodFacts API so products can be searched using a barcode or product name.

A command line interface (CLI) is included to make it easier to interact with the API without using Postman.



## Features

- View all inventory items
- View a single inventory item
- Add a new inventory item
- Update an inventory item
- Delete an inventory item
- Search inventory items
- Get product information from OpenFoodFacts
- Add products from OpenFoodFacts into the inventory
- Run tests using pytest



## Technologies Used

- Python
- Flask
- Flask-CORS
- Requests
- Click
- Pytest
- OpenFoodFacts API



## Project Structure


inventory-management-system/
│
├── app.py
├── services.py
├── cli.py
├── requirements.txt
├── README.md
└── tests/
    └── test_app.py




## Installation

Clone the repository.

```bash
git clone <repository-url>
```

Move into the project folder.

```bash
cd inventory-management-system
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate it.

Linux/macOS

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the Flask server.

```bash
python app.py
```

The API runs on:

```
http://localhost:5000
```

---

## API Endpoints

| Method | Endpoint |
|--------|----------|
| GET | /api/inventory |
| GET | /api/inventory/<id> |
| POST | /api/inventory |
| PATCH | /api/inventory/<id> |
| DELETE | /api/inventory/<id> |
| GET | /api/inventory/search?q=value |
| GET | /api/openfoodfacts/barcode/<barcode> |
| GET | /api/openfoodfacts/search?q=value |
| POST | /api/inventory/from-barcode |

---

## CLI Commands

View all items

```bash
python cli.py view
```

Add an item

```bash
python cli.py add --name "Milk" --price 3.99 --quantity 20
```

Update an item

```bash
python cli.py update --id ITEM_ID --price 4.99
```

Delete an item

```bash
python cli.py delete --id ITEM_ID
```

Find a product by barcode

```bash
python cli.py fetch --barcode 737628064502
```

Search OpenFoodFacts

```bash
python cli.py search --query milk
```

---

## Running Tests

Run all tests.

```bash
pytest
```

or

```bash
pytest -v
```

---

## Notes

The project stores inventory in memory using a Python list, so data is cleared whenever the application is restarted. This was done to keep the project simple and focus on learning Flask APIs, CRUD operations, API integration and testing.

---

## Author

John Kamau