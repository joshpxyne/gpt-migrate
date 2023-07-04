from flask import Flask, request, jsonify
from bcrypt import hashpw, gensalt
from db import read_items, write_items

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello World!"

@app.route('/grocery_items', methods=['GET'])
def get_grocery_items():
    try:
        #read grocery items from database
        grocery_items = read_items()
        items = [{"id": item["id"], "name": item["name"], "price": item["price"]} for item in grocery_items]
        #return response as json
        return jsonify(items)
    except Exception as e:
        return e, 500

@app.route('/grocery_items', methods=['POST'])
def add_grocery_item():
    try:
        #extract item data from request payload 
        new_item = request.json
        print(new_item["id"],new_item,flush=True)
        #read existing grocery items from database
        grocery_items = read_items()
        #check if new item already exists in database
        if new_item not in grocery_items:
            #item dosen't already exist in db, so add it to db
            grocery_items.append(new_item)
            #write updated grocery list back to database
            write_items(grocery_items)
        #http message indicating success
        return "Successfully added item", 201
    except Exception as e:
        return e, 500
    
@app.route('/grocery_items/<int:item_id>', methods=['DELETE'])
def delete_grocery_item(item_id):
    try:
        grocery_items = read_items()
        #filter out item with id 
        grocery_items = [item for item in grocery_items if item["id"] != item_id]
        write_items(grocery_items)
        #success message with 200 status code 
        return "Successfully deleted item", 200
    except Exception as e:
        #error returns 500 status code
        return e, 500

@app.route('/hashpassword/<string:password>', methods=['GET'])
def hash_password(password):
    try:
        #hash password with bycrypt
        return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    except Exception as e:
        return e, 500

if __name__ == '__main__':
    app.run(debug=True)
