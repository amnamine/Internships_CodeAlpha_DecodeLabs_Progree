# 🚀 CodeAlpha Full-Stack Development Internship Portfolio

Welcome to my **CodeAlpha Full-Stack Development Internship** repository! This project serves as a comprehensive portfolio showcasing four distinct, feature-rich web applications built using modern web development stacks. Each project is designed to address a real-world use case, incorporating frontend interfaces, responsive styling, secure backend systems, and database integrations.

---

## 📂 Repository Structure

The repository is organized into four distinct tasks:

```text
Full Stack/
├── Task 1/               # Simple E-commerce Store (Express.js & SQLite)
│   ├── public/           # Frontend pages (index.html, product.html, cart.html, styling, app.js)
│   ├── database.js       # SQLite database configuration & helper methods
│   ├── server.js         # Backend REST API and routing
│   └── package.json      # Node.js dependencies
│
├── Task 2/               # Social Media Platform (Express.js, Session Auth & SQLite)
│   ├── public/           # Single-page interface (index.html, style.css, app.js)
│   ├── db.js             # SQLite database setup with promises
│   ├── server.js         # User auth, posts, comments, likes & follows API
│   └── package.json      # Node.js dependencies
│
├── Task 3/               # Project Management Tool (Flask & WebSockets)
│   ├── static/           # Styling & frontend socket communication logic
│   ├── templates/        # Jinja2 template index page
│   ├── app.py            # Flask app initialization & Socket.IO config
│   ├── models.py         # SQLAlchemy schemas (User, Project, Task, Comment)
│   ├── routes.py         # HTTP blueprints and auth logic
│   └── sockets.py        # Real-time WebSocket event handlers
│
└── Task 4/               # Real-Time Communication App (Django & WebRTC)
    ├── collaboration/    # Django App containing views, models, and URLs
    │   ├── templates/    # Templates for dashboard, login, register, and video room
    │   ├── models.py     # Room models
    │   └── views.py      # Room management and authentication views
    ├── rtc_project/      # Main Django project configuration settings
    ├── static/           # WebRTC peer connections, UI interaction scripts, whiteboard drawing logic
    └── manage.py         # Django execution utility
```

---

## 🛠️ Detailed Task Breakdowns

---

### 🛒 [Task 1: Simple E-commerce Store](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Full%20Stack/Task%201)

A responsive, lightweight online storefront with product browsing, full shopping cart features, stock control, and checkout operations.

#### 🌟 Key Features
- **Product Directory**: Dynamic fetch and layout of available products with search & filter categories.
- **Product Details Page**: Dedicated view displaying descriptive details, pricing, and stock status.
- **Persistent Shopping Cart**: Session-based/local-storage cart allowing item adjustment and automatic total calculation.
- **Order Processing & Inventory Management**: Safe transactional logic validating stock availability before creating orders, inserting order items, and updating warehouse inventory.

#### 🔧 Technology Stack
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Node.js, Express.js
- **Database**: SQLite3

#### ⚙️ How to Setup & Run Task 1
1. Navigate to the task directory:
   ```bash
   cd "Task 1"
   ```
2. Install the dependencies:
   ```bash
   npm install
   ```
3. Run the server:
   ```bash
   npm start
   ```
4. Access the web app at: `http://localhost:3000`

---

### 👥 [Task 2: Social Media Platform](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Full%20Stack/Task%202)

A interactive mini social network enabling user registration, content creation, social engagements, and dynamic user updates.

#### 🌟 Key Features
- **Secure Authentication**: Registration and login using `bcryptjs` for secure password hashing and `express-session` for session state persistence.
- **Interactive Newsfeed**: Create new posts with markdown formatting, view, delete, or comment on other posts.
- **Profiles & Avatars**: Customizable user bios and random cool profile avatars dynamically sourced from Dicebear APIs.
- **Engagement Mechanics**: Real-time asynchronous Like/Unlike button toggles and Follow/Unfollow systems to personalize individual feeds.

#### 🔧 Technology Stack
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+ with CSS Grid & Flexbox)
- **Backend**: Node.js, Express.js, Express Session
- **Database**: SQLite3 (with Promisified queries)

#### ⚙️ How to Setup & Run Task 2
1. Navigate to the task directory:
   ```bash
   cd "Task 2"
   ```
2. Install the dependencies:
   ```bash
   npm install
   ```
3. Start the application:
   ```bash
   npm start
   ```
4. Access the web app at: `http://localhost:3000`

---

### 📋 [Task 3: Project Management Tool](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Full%20Stack/Task%203)

A Trello/Asana-style collaborative task board designed to sync group projects in real-time across multiple logged-in clients.

#### 🌟 Key Features
- **Project Boards**: Group tasks by custom workspace projects with individual member permissions.
- **Kanban-Style Task Cards**: Organize tasks by statuses (`To Do`, `In Progress`, `Review`, `Done`).
- **Interactive Comments & Assignments**: Assign cards to specific users, write updates, and view action logs.
- **Real-Time Synchronization (WebSockets)**: Instant visual updates whenever someone moves a card, posts a comment, or edits details, powered by `Flask-SocketIO`.

#### 🔧 Technology Stack
- **Frontend**: Jinja2 Templates, Vanilla CSS3, Socket.io Client
- **Backend**: Python, Flask, Flask-Login, Flask-SocketIO
- **Database**: SQLite, SQLAlchemy ORM

#### ⚙️ How to Setup & Run Task 3
1. Navigate to the task directory:
   ```bash
   cd "Task 3"
   ```
2. Create and activate a python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install the required Python libraries:
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-socketio eventlet
   ```
4. Run the Flask App:
   ```bash
   python app.py
   ```
5. Access the web app at: `http://127.0.0.1:5000`

---

### 📹 [Task 4: Real-Time Communication App](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Full%20Stack/Task%204)

A highly secure video conferencing and screen-sharing collaboration dashboard equipped with interactive widgets.

#### 🌟 Key Features
- **P2P Video & Audio Calling**: Multi-user high-quality audio and video connection utilizing WebRTC APIs.
- **Screen Sharing**: Dynamic sharing of windows or screen displays mid-call.
- **Collaborative Whiteboard**: Interactive Canvas drawing workspace for drawing, writing, and diagramming together.
- **End-to-End Encryption**: Encrypted media and signals ensuring privacy using WebRTC DTLS/SRTP protocols.
- **Dashboard Management**: User profile rooms dashboard to initialize, schedule, and join secure workspaces.

#### 🔧 Technology Stack
- **Frontend**: WebRTC APIs, HTML5 Canvas API, Vanilla CSS3
- **Backend**: Python, Django, SQLite
- **Communication Protocols**: WebRTC, Secure Signal Exchanges

#### ⚙️ How to Setup & Run Task 4
1. Navigate to the task directory:
   ```bash
   cd "Task 4"
   ```
2. Install Django:
   ```bash
   pip install django
   ```
3. Make migrations and migrate the SQLite database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
5. Access the web app at: `http://127.0.0.1:8000`

---

## 🎓 Internship Perks & Requirements

According to the official [CodeAlpha M1 PDF instructions](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Full%20Stack/Full%20Stack%20Development%20Tasks%20%26%20Instructions%20%E2%80%94%20CodeAlpha%20M1.pdf), completing a minimum of **2 to 3 tasks** from the list is mandatory to qualify for the internship certificate. Submitting only one task will be considered incomplete.

### 🌟 Deliverables Checklist
* [x] Share internship status on LinkedIn (tagging `@CodeAlpha`).
* [x] Upload clean, functional code to GitHub under `CodeAlpha_ProjectName`.
* [x] Post a video explanation of your project on LinkedIn with your GitHub repository link.
* [x] Submit the completed project links via the Submission Form shared in the WhatsApp group.

---

## 📞 Support & Contacts
- **Website**: [www.codealpha.tech](http://www.codealpha.tech)
- **WhatsApp**: +91 9336576683
- **Email Support**: services@codealpha.tech | services.codealpha@gmail.com
