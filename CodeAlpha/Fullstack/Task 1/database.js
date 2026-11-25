const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'ecommerce.db');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
  } else {
    console.log('Connected to the SQLite database.');
  }
});

// Initialize database schema
db.serialize(() => {
  // Products table
  db.run(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT NOT NULL,
      price REAL NOT NULL,
      image TEXT NOT NULL,
      category TEXT NOT NULL,
      stock INTEGER DEFAULT 10,
      rating REAL DEFAULT 4.5,
      reviews_count INTEGER DEFAULT 0
    )
  `);

  // Orders table
  db.run(`
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      customer_name TEXT NOT NULL,
      customer_email TEXT NOT NULL,
      shipping_address TEXT NOT NULL,
      total_amount REAL NOT NULL,
      status TEXT DEFAULT 'Pending',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Order items table
  db.run(`
    CREATE TABLE IF NOT EXISTS order_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      price REAL NOT NULL,
      FOREIGN KEY (order_id) REFERENCES orders(id),
      FOREIGN KEY (product_id) REFERENCES products(id)
    )
  `);

  // Seed products if table is empty
  db.get('SELECT COUNT(*) as count FROM products', [], (err, row) => {
    if (err) {
      console.error('Error checking product count:', err.message);
      return;
    }

    if (row.count === 0) {
      console.log('Seeding initial products data...');
      const sampleProducts = [
        {
          name: 'Aether 75 Mechanical Keyboard',
          description: 'A premium 75% hot-swappable mechanical keyboard featuring hand-lubed linear switches, custom PBT keycaps, and a solid anodized aluminum chassis for an unmatched typing sound and feel.',
          price: 189.99,
          image: '/images/keyboard.jpg',
          category: 'Keyboards',
          stock: 15,
          rating: 4.9,
          reviews_count: 142
        },
        {
          name: 'Vortex Precision Wireless Mouse',
          description: 'High-performance wireless gaming and productivity mouse with 26,000 DPI optical sensor, ultra-lightweight 58g body, and 120 hours of battery life over 2.4GHz hyperspeed connection.',
          price: 99.50,
          image: '/images/mouse.jpg',
          category: 'Mice',
          stock: 25,
          rating: 4.8,
          reviews_count: 88
        },
        {
          name: 'Minimalist Merino Desk Mat',
          description: 'Luxurious desk felt pad crafted from 100% natural Merino wool. Provides a soft, warm surface for hands, shields your desk from scratches, and dampens keyboard resonance.',
          price: 49.00,
          image: '/images/deskmat.jpg',
          category: 'Accessories',
          stock: 40,
          rating: 4.7,
          reviews_count: 215
        },
        {
          name: 'Lumina RGB Ambient Lightbar',
          description: 'Monitor-mounted light bar with customizable dual-zone RGB backlighting and front-facing asymmetrical light path to reduce eye strain without screen glare. Smart dial controller included.',
          price: 79.99,
          image: '/images/lightbar.jpg',
          category: 'Lighting',
          stock: 20,
          rating: 4.6,
          reviews_count: 67
        },
        {
          name: 'Nimbus Studio Monitors (Pair)',
          description: 'Compact high-fidelity active desktop speakers with Bluetooth 5.0, optical and RCA inputs. Clear highs, robust mids, and punchy bass for studio-quality music production or desktop enjoyment.',
          price: 249.99,
          image: '/images/speakers.jpg',
          category: 'Audio',
          stock: 8,
          rating: 4.9,
          reviews_count: 53
        },
        {
          name: 'Apex Ergo Aluminum Laptop Stand',
          description: 'Ergonomic, fully adjustable laptop riser machined from aircraft-grade aluminum. Improves cooling airflow and elevates screens to eye level to promote better neck and back posture.',
          price: 59.99,
          image: '/images/stand.jpg',
          category: 'Accessories',
          stock: 30,
          rating: 4.5,
          reviews_count: 104
        }
      ];

      const stmt = db.prepare(`
        INSERT INTO products (name, description, price, image, category, stock, rating, reviews_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `);

      sampleProducts.forEach((p) => {
        stmt.run(p.name, p.description, p.price, p.image, p.category, p.stock, p.rating, p.reviews_count);
      });

      stmt.finalize();
      console.log('Product seeding completed.');
    }
  });
});

module.exports = {
  db,
  getProducts: (callback) => {
    db.all('SELECT * FROM products', [], callback);
  },
  getProductById: (id, callback) => {
    db.get('SELECT * FROM products WHERE id = ?', [id], callback);
  },
  updateProductStock: (id, quantity, callback) => {
    db.run('UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?', [quantity, id, quantity], callback);
  },
  createOrder: (name, email, address, total, callback) => {
    db.run(
      'INSERT INTO orders (customer_name, customer_email, shipping_address, total_amount) VALUES (?, ?, ?, ?)',
      [name, email, address, total],
      function (err) {
        if (err) return callback(err);
        callback(null, this.lastID);
      }
    );
  },
  createOrderItem: (orderId, productId, quantity, price, callback) => {
    db.run(
      'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
      [orderId, productId, quantity, price],
      callback
    );
  }
};
