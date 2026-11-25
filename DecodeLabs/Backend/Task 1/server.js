const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS and JSON body parsing
app.use(cors());
app.use(express.json());

// Serve static frontend files from the public folder
app.use(express.static(path.join(__dirname, 'public')));

// Custom middleware to add demo REST headers
app.use((req, res, next) => {
  res.setHeader('X-Stateless-Server', 'true');
  res.setHeader('X-Project-Name', 'REST-API-Fundamentals');
  next();
});

// Stateless Mock Database (in-memory)
let items = [
  {
    id: 1,
    name: 'GET Request',
    description: 'Used to retrieve representation of a resource without side effects.',
    category: 'HTTP Method'
  },
  {
    id: 2,
    name: 'POST Request',
    description: 'Used to submit an entity to the specified resource, often causing a change in state or side effects on the server.',
    category: 'HTTP Method'
  },
  {
    id: 3,
    name: 'Statelessness',
    description: 'The server does not store any session context about the client connection. Every request contains all information needed to process it.',
    category: 'REST Constraint'
  }
];

// GET: Retrieve all items
app.get('/api/items', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'Successfully retrieved resource items list.',
    data: items
  });
});

// GET: Retrieve specific item by ID
app.get('/api/items/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const item = items.find(i => i.id === id);

  if (!item) {
    return res.status(404).json({
      success: false,
      message: `Resource item with ID ${id} not found.`
    });
  }

  res.status(200).json({
    success: true,
    message: `Successfully retrieved item with ID ${id}.`,
    data: item
  });
});

// POST: Create a new resource item
app.post('/api/items', (req, res) => {
  const { name, description, category } = req.body;

  // Validation
  if (!name || !description || !category) {
    return res.status(400).json({
      success: false,
      message: 'Validation failed. Fields "name", "description", and "category" are all required.',
      requiredFields: ['name', 'description', 'category'],
      receivedData: req.body
    });
  }

  const newItem = {
    id: items.length > 0 ? Math.max(...items.map(i => i.id)) + 1 : 1,
    name,
    description,
    category
  };

  items.push(newItem);

  res.status(201).json({
    success: true,
    message: 'Resource item created successfully.',
    data: newItem
  });
});

// GET: Server health/status
app.get('/api/status', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
    serverInfo: {
      framework: 'Express',
      nodeVersion: process.version,
      stateless: true
    }
  });
});

// Handle malformed JSON body errors gracefully
app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({
      success: false,
      message: 'Invalid JSON in request body. Please check your syntax.',
      error: err.message
    });
  }
  next(err);
});

// Handle 404 for API routes
app.use('/api', (req, res) => {
  res.status(404).json({
    success: false,
    message: `API Route ${req.method} ${req.originalUrl} not found.`
  });
});

app.listen(PORT, () => {
  console.log(`=========================================`);
  console.log(` REST API Fundamentals Playground Running`);
  console.log(` URL: http://localhost:${PORT}`);
  console.log(`=========================================`);
});
