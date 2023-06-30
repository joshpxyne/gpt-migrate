import json

def read_items():
    with open('storage/items.json') as f:
        grocery_items = json.load(f)
    return grocery_items

def write_items(grocery_items):
    with open('storage/items.json', 'w') as f:
        json.dump(grocery_items, f)
