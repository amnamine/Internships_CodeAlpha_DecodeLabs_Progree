const express = require('express');
const path = require('path');
const db = require('./database');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// API: Get all products
app.get('/api/products', (req, res) => {
  db.getProducts((err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Database error occurred while fetching products.' });
    }
    res.json(rows);
  });
});

// API: Get single product details
app.get('/api/products/:id', (req, res) => {
  const productId = parseInt(req.params.id, 10);
  db.getProductById(productId, (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Database error occurred.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Product not found.' });
    }
    res.json(row);
  });
});

// API: Place order
app.post('/api/orders', (req, res) => {
  const { customerName, customerEmail, shippingAddress, items } = req.body;

  if (!customerName || !customerEmail || !shippingAddress || !items || !Array.isArray(items) || items.length === 0) {
    return res.status(400).json({ error: 'Missing required checkout information or empty cart.' });
  }

  // We need to run checks and insertions. Since sqlite3 runs asynchronously, we must handle this carefully.
  // Validate stock of all products first
  const productIds = items.map(item => item.productId);
  const placeholders = productIds.map(() => '?').join(',');

  db.db.all(`SELECT * FROM products WHERE id IN (${placeholders})`, productIds, (err, dbProducts) => {
    if (err) {
      return res.status(500).json({ error: 'Error validating products.' });
    }

    const productMap = {};
    dbProducts.forEach(p => {
      productMap[p.id] = p;
    });

    let totalAmount = 0;
    const itemsToProcess = [];

    for (const item of items) {
      const dbProd = productMap[item.productId];
      if (!dbProd) {
        return res.status(400).json({ error: `Product with ID ${item.productId} not found.` });
      }
      if (dbProd.stock < item.quantity) {
        return res.status(400).json({ error: `Insufficient stock for ${dbProd.name}. Available: ${dbProd.stock}.` });
      }
      totalAmount += dbProd.price * item.quantity;
      itemsToProcess.push({
        productId: item.productId,
        quantity: item.quantity,
        price: dbProd.price
      });
    }

    // Begin Order creation
    db.createOrder(customerName, customerEmail, shippingAddress, totalAmount, (err, orderId) => {
      if (err) {
        return res.status(500).json({ error: 'Failed to create order.' });
      }

      // Insert all order items and update stock
      let completedItems = 0;
      let orderError = null;

      itemsToProcess.forEach(item => {
        db.createOrderItem(orderId, item.productId, item.quantity, item.price, (err) => {
          if (err) {
            orderError = 'Error recording order items.';
          }
          
          db.updateProductStock(item.productId, item.quantity, (err) => {
            if (err) {
              orderError = 'Error updating inventory.';
            }

            completedItems++;
            if (completedItems === itemsToProcess.length) {
              if (orderError) {
                return res.status(500).json({ error: orderError });
              }
              return res.json({
                success: true,
                orderId: orderId,
                message: 'Order processed successfully!',
                totalAmount: totalAmount
              });
            }
          });
        });
      });
    });
  });
});

// Serve frontend paths for nice clean routing or single pages
app.get('*', (req, res, next) => {
  // If requesting api or static files with extensions, continue
  if (req.url.startsWith('/api') || req.url.includes('.')) {
    return next();
  }
  // Default to index page
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
