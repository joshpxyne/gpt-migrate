from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

grocery_items = [
    {"id": 1, "name": "Milk", "price": 2.50},
    {"id": 2, "name": "Eggs", "price": 3.00},
    {"id": 3, "name": "Bread", "price": 1.50}
]

class Item(BaseModel):
    id: int
    name: str
    price: float

@app.get('/grocery_items', response_model=List[Item])
def get_grocery_items():
    return grocery_items

@app.post('/grocery_items', response_model=Item, status_code=201)
def add_grocery_item(item: Item):
    grocery_items.append(item.dict())
    return item

@app.put('/grocery_items/{item_id}', response_model=Item)
def update_grocery_item(item_id: int, item: Item):
    existing_item = next((item for item in grocery_items if item["id"] == item_id), None)
    if existing_item:
        existing_item.update(item.dict())
        return existing_item
    return {"message": "Item not found"}, 404

@app.delete('/grocery_items/{item_id}', status_code=200)
def delete_grocery_item(item_id: int):
    global grocery_items
    grocery_items = [item for item in grocery_items if item["id"] != item_id]
    return {"message": "Item deleted"}