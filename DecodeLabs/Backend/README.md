# DecodeLabs Backend Development Internship Track (Batch 2026)

Welcome to the **DecodeLabs Backend Development Internship Project Workspace**. This repository contains four comprehensive backend engineering projects demonstrating core web server architecture, persistent database integrations (CRUD), JWT-based zero-trust authentication, and resilient third-party API integration.

---

## 🚀 Quick Start (Run All Projects Concurrently)

Launch all backend and frontend services simultaneously in separate terminal windows using the master startup script:

```bash
# Double-click or run from terminal:
.\start_all.bat
```

### 📡 Master Port & Service Map

| Project / Task | Service Type | Port / URL | Description |
| :--- | :--- | :--- | :--- |
| **Task 1: REST API Fundamentals** | REST API + Web UI | [`http://localhost:3000`](http://localhost:3000) | Stateless HTTP methods & JSON endpoints |
| **Task 2: Database (Backend)** | Express + SQLite | [`http://localhost:5000`](http://localhost:5000) | User Management CRUD REST API |
| **Task 2: Database (Frontend)** | React + Vite UI | [`http://localhost:5173`](http://localhost:5173) | Modern Glassmorphism Admin Dashboard |
| **Task 3: Auth System** | Express + JWT + Bcrypt | [`http://localhost:3003`](http://localhost:3003) | Zero-Trust Authentication & Protected Routes |
| **Task 4: 3rd Party API** | Weather Dashboard | [`http://localhost:4000`](http://localhost:4000) | External Weather API Integration & Search History |

---

## 🛠️ Project Summaries

### 1️⃣ Project 1: REST API Fundamentals
- **Location:** [`./Task 1`](./Task%201)
- **Goal:** Build a stateless HTTP server exposing RESTful endpoints.
- **Port:** `3000`
- **Key Concepts:** HTTP status codes, stateless routing, standard JSON responses, request body validation.
- **Endpoints:**
  - `GET /api/items` - Retrieve resource list
  - `GET /api/items/:id` - Retrieve item by ID
  - `POST /api/items` - Create new resource
  - `GET /api/status` - Server health check
- **Manual Launch:** `cd "Task 1" && npm install && node server.js` (or run `run.bat`)

---

### 2️⃣ Project 2: Database Integration (CRUD)
- **Location:** [`./Task 2`](./Task%202)
- **Goal:** Connect Express API to persistent SQLite database using Sequelize ORM with a React Admin UI.
- **Backend Port:** `5000` | **Frontend Port:** `5173`
- **Key Concepts:** ORM models, relational database schemas, unique constraints, full CRUD operations.
- **Backend Endpoints:**
  - `POST /api/users` - Create user
  - `GET /api/users` - List all users
  - `GET /api/users/:id` - Get user by ID
  - `PUT /api/users/:id` - Update user details
  - `DELETE /api/users/:id` - Delete user
- **Manual Launch:**
  - Backend: `cd "Task 2/backend" && npm install && node server.js`
  - Frontend: `cd "Task 2/frontend" && npm install && npm run dev`

---

### 3️⃣ Project 3: Secure Authentication System
- **Location:** [`./Task 3`](./Task%203)
- **Goal:** Secure API endpoints with Bcrypt password hashing and JSON Web Tokens (JWT).
- **Port:** `3003`
- **Key Concepts:** Password hashing (Bcrypt 10 rounds), JWT sign & verify middleware, Zero-Trust protected routes.
- **Endpoints:**
  - `POST /api/register` - Register new account
  - `POST /api/login` - Authenticate user & return JWT token
  - `GET /api/protected` - Access protected route (Requires `Authorization: Bearer <token>`)
- **Test Credentials:**
  - `username: admin` | `password: admin`
  - `username: amine` | `password: securePass2026`
  - `username: guest` | `password: guestAccess`
- **Manual Launch:** `cd "Task 3" && npm install && node server.js` (or run `start_server.bat`)

---

### 4️⃣ Project 4: Third-Party API Integration (Weather Dashboard)
- **Location:** [`./Task 4`](./Task%204)
- **Goal:** Integrate external third-party API data (OpenWeatherMap / Open-Meteo fallback) with search history persistence.
- **Port:** `4000`
- **Key Concepts:** Asynchronous `async/await` fetch, API key environment variables (`.env`), fallback providers, air quality & forecast payloads.
- **Endpoints:**
  - `GET /api/weather?city={cityName}` - Fetch current weather, hourly & 7-day forecast
  - `GET /api/history` - Retrieve recent search history
- **Manual Launch:** `cd "Task 4" && npm install && node server.js` (or run `start_server.bat`)

---

## 📋 Prerequisites & Setup

- **Node.js**: v18.x or higher installed.
- **Git**: Installed for version control.

### Installation

To set up dependencies across all projects manually:

```bash
cd "Task 1" && npm install && cd ..
cd "Task 2/backend" && npm install && cd ..\..
cd "Task 2/frontend" && npm install && cd ..\..
cd "Task 3" && npm install && cd ..
cd "Task 4" && npm install && cd ..
```

---

## 🗂️ Workspace Directory Structure

```
.
├── Task 1/                       # Project 1: REST API Fundamentals
│   ├── public/                   # Static Playground Web UI
│   ├── server.js                 # Express server (Port 3000)
│   └── run.bat                   # Task 1 startup script
├── Task 2/                       # Project 2: Database Integration (CRUD)
│   ├── backend/                  # Sequelize + SQLite backend (Port 5000)
│   ├── frontend/                 # React + Vite Admin Dashboard (Port 5173)
│   └── start_app.bat             # Task 2 startup script
├── Task 3/                       # Project 3: Secure Auth System
│   ├── database.sqlite           # SQLite DB (Users table)
│   ├── public/                   # Auth Portal Web UI
│   ├── seed_users.js             # User seeding utility script
│   ├── server.js                 # JWT + Bcrypt Auth server (Port 3003)
│   └── start_server.bat          # Task 3 startup script
├── Task 4/                       # Project 4: Third-Party Weather API
│   ├── .env                      # Weather API keys & PORT configuration
│   ├── public/                   # Weather Dashboard Web UI
│   ├── server.js                 # Weather & Search History Server (Port 4000)
│   └── start_server.bat          # Task 4 startup script
├── start_all.bat                 # Master launch script for all 4 tasks
├── .gitignore                    # Git ignore file for node_modules, SQLite DBs & envs
└── README.md                     # Comprehensive project documentation
```
