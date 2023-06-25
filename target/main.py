from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

grocery_items = [
    {"id": 1, "name": "Milk", "price": 2.50},
    {"id": 2, "name": "Eggs", "price": 3.00},
    {"id": 3, "name": "Bread", "price": 1.50}
]

class GroceryItem(BaseModel):
    id: int
    name: str
    price: float

@app.get('/grocery_items', response_model=List[GroceryItem])
def get_grocery_items():
    return grocery_items

@app.post('/grocery_items', response_model=GroceryItem, status_code=201)
def add_grocery_item(item: GroceryItem):
    grocery_items.append(item.dict())
    return item

@app.put('/grocery_items/{item_id}', response_model=GroceryItem)
def update_grocery_item(item_id: int, updated_item: GroceryItem):
    item = next((item for item in grocery_items if item["id"] == item_id), None)
    if item:
        index = grocery_items.index(item)
        grocery_items[index] = updated_item.dict()
        return updated_item
    return {"message": "Item not found"}, 404

@app.delete('/grocery_items/{item_id}')
def delete_grocery_item(item_id: int):
    global grocery_items
    grocery_items = [item for item in grocery_items if item["id"] != item_id]
    return {"message": "Item deleted"}, 200