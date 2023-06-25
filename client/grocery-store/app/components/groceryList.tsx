import { useState, useEffect } from 'react';

const GroceryList = () => {
  const [groceryItems, setGroceryItems] = useState([]);

  useEffect(() => {
    fetch('/api/groceryItems')
      .then(response => response.json())
      .then(data => setGroceryItems(data));
  }, []);

  return (
    <div>
      <h2>Grocery List</h2>
      <ul>
        {groceryItems.map(item => (
          <li key={item.id}>
            {item.name} - ${item.price.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GroceryList;