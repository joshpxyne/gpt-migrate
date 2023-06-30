from flask import Flask, request, jsonify
from bcrypt import hashpw, gensalt
from db import mongo

app = Flask(__name__)

grocery_items = [
    {"id": 1, "name": "Milk", "price": 2.50},
    {"id": 2, "name": "Eggs", "price": 3.00},
    {"id": 3, "name": "Bread", "price": 1.50}
]

@app.route('/grocery_items', methods=['GET'])
def get_grocery_items():
    return jsonify(grocery_items)

@app.route('/grocery_items', methods=['POST'])
def add_grocery_item():
    new_item = request.json
    grocery_items.append(new_item)
    return jsonify(new_item), 201

@app.route('/grocery_items/<int:item_id>', methods=['PUT'])
def update_grocery_item(item_id):
    item = next((item for item in grocery_items if item["id"] == item_id), None)
    if item:
        item.update(request.json)
        return jsonify(item)
    return jsonify({"message": "Item not found"}), 404

@app.route('/grocery_items/<int:item_id>', methods=['DELETE'])
def delete_grocery_item(item_id):
    global grocery_items
    grocery_items = [item for item in grocery_items if item["id"] != item_id]
    return jsonify({"message": "Item deleted"}), 200

# function to intake a password, salt and hash it
def hash_password(password):
    mongo.write("passwords", {"password": hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')})
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

if __name__ == '__main__':
    app.run(debug=True)