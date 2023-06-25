const http = require('http');
const url = require('url');
const { parse } = require('querystring');

const groceryItems = [
  { id: 1, name: 'Milk', price: 2.50 },
  { id: 2, name: 'Eggs', price: 3.00 },
  { id: 3, name: 'Bread', price: 1.50 }
];

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const id = parseInt(parsedUrl.pathname.split('/')[2]);
  let body = '';

  if (parsedUrl.pathname === '/grocery_items') {
    if (req.method === 'GET') {
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify(groceryItems));
    }
    else if (req.method === 'POST') {
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        const newItem = JSON.parse(body);
        groceryItems.push(newItem);
        res.setHeader('Content-Type', 'application/json');
        res.statusCode = 201;
        res.end(JSON.stringify(newItem));
      });
    }
  }
  else if (id && parsedUrl.pathname.startsWith('/grocery_items/')) {
    const item = groceryItems.find(item => item.id === id);

    if (req.method === 'PUT') {
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        const update = JSON.parse(body);
        if (item) {
          Object.assign(item, update);
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify(item));
        }
        else {
          res.setHeader('Content-Type', 'application/json');
          res.statusCode = 404;
          res.end(JSON.stringify({ message: 'Item not found' }));
        }
      });
    }
    else if (req.method === 'DELETE') {
      if (item) {
        const index = groceryItems.indexOf(item);
        groceryItems.splice(index, 1);
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ message: 'Item deleted' }));
      }
      else {
        res.setHeader('Content-Type', 'application/json');
        res.statusCode = 404;
        res.end(JSON.stringify({ message: 'Item not found' }));
      }
    }
  }
});

const port = process.env.PORT || 3000;
server.listen(port, () => {
  console.log(`Server running on port ${port}`);
});