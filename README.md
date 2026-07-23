# Inventory Management System

## Project Overview

This project is a Flask REST API that allows users to manage inventory items. It also connects to the OpenFoodFacts API to retrieve product information using a barcode or product search. A command-line interface (CLI) is included for interacting with the API from the terminal.

---

## Getting Started

Clone the repository and move into the project directory.

```bash
git clone <repository-url>
cd inventory-management-system
```

Create and activate a virtual environment.

```bash
python -m venv venv
```

Linux

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install the project dependencies.

```bash
pip install -r requirements.txt
```

---

## Starting the Application

Run the Flask application.

```bash
python app.py
```

The server will start on:

```
http://localhost:5000
```

---

## Available API Routes

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/inventory` | Retrieve all inventory items |
| GET | `/api/inventory/<id>` | Retrieve one inventory item |
| POST | `/api/inventory` | Create a new inventory item |
| PATCH | `/api/inventory/<id>` | Update an existing item |
| DELETE | `/api/inventory/<id>` | Remove an inventory item |
| GET | `/api/openfoodfacts/barcode/<barcode>` | Find a product using a barcode |
| GET | `/api/openfoodfacts/search?q=name` | Search products by name |
| POST | `/api/inventory/from-barcode` | Add a product from OpenFoodFacts to the inventory |

---

## Using the CLI

Make sure the Flask server is running before using any CLI commands.

Some common commands are:

```bash
python cli.py view
python cli.py view --id ITEM_ID
python cli.py add --name "Milk" --price 3.99 --quantity 20
python cli.py update --id ITEM_ID --price 4.99
python cli.py delete --id ITEM_ID
python cli.py fetch --barcode 737628064502
python cli.py search --query milk
```

---

## Running Tests

Run all tests with:

```bash
pytest
```

or

```bash
pytest -v
```

---

## OpenFoodFacts Integration

The application connects to the OpenFoodFacts API to retrieve product details such as the product name, brand, category and description. Users can search for products or import them directly into the inventory using a barcode.

---

## Additional Information

- Inventory data is stored in memory, so restarting the application clears all items.
- The CLI communicates with the Flask API using HTTP requests.
- A running Flask server is required before using the CLI commands.