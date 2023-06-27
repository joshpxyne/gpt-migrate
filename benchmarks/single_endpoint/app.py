from flask import Flask, request, jsonify

app = Flask(__name__)

grocery_items = [
    {"id": 1, "name": "Milk", "price": 2.50},
    {"id": 2, "name": "Eggs", "price": 3.00},
    {"id": 3, "name": "Bread", "price": 1.50}
]

@app.route('/grocery_items', methods=['GET'])
def get_grocery_items():
    return jsonify(grocery_items)