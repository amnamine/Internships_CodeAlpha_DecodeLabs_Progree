# CodeAlpha Backend Development Internship — Module 1

Welcome to the **CodeAlpha Backend Development Internship** repository! This project houses a collection of server-side applications built during the internship program to demonstrate proficiency in backend architectures, database management, API design, and web interfaces.

The repository is structured into four main backend application tasks, utilising **Python**, **Flask**, **Django**, and **SQLite**.

---

## 📂 Repository Structure

```directory
Backend/
│
├── Backend Development Tasks & Instructions — CodeAlpha M1.pdf   # Task guidelines
├── README.md                                                     # Project documentation (this file)
│
├── Task1/               # Simple URL Shortener (Flask + SQLite)
│   ├── app.py           # Main Flask application and API routes
│   ├── database.py      # SQLite connection and helper functions
│   ├── templates/       # HTML view templates
│   └── static/          # CSS stylesheets and client-side JavaScript
│
├── Task2/               # Event Registration System (Django + SQLite)
│   ├── manage.py        # Django project CLI entrypoint
│   ├── event_manager/   # Django project configuration settings & routing
│   └── events/          # Django app containing models, views, forms, and templates
│
├── Task3/               # Restaurant Management System (Django + SQLite)
│   ├── manage.py        # Django project CLI entrypoint
│   ├── restaurant_manager/ # Django project settings & routing
│   └── restaurant/      # Django app for menus, reservations, orders, and inventory
│
└── Task4/               # Job Board Platform (Django + SQLite)
    ├── manage.py        # Django project CLI entrypoint
    ├── job_board/       # Django project settings & routing
    └── board/           # Django app for candidate/employer profiles, job listings, & applications
```

---

## 🛠️ Tasks Breakdown

### 🔗 Task 1: Simple URL Shortener
A lightweight web application built to convert long, complex URLs into short, easy-to-share links. It records and displays click statistics for each link created.

*   **Technology Stack**: Python, Flask, SQLite, HTML5, CSS3, JavaScript.
*   **Core Features**:
    *   **Short Code Generation**: Automatically generates a unique 6-character alphanumeric code for every submitted URL.
    *   **Robust URL Validation**: Validates that inputs are correctly formatted URLs before processing.
    *   **Auto-Redirection**: Resolves short codes and redirects visitors to the original destination URL.
    *   **Analytics Dashboard**: Tracks the click count and creation timestamp for all generated links.
*   **Database Schema (`urls.db`)**:
    *   `id`: Integer Primary Key (Autoincrement)
    *   `original_url`: Text (Original destination address)
    *   `short_code`: Text (Unique short identifier)
    *   `created_at`: Timestamp (Defaulting to current time)
    *   `clicks`: Integer (Analytics counter, defaults to 0)

---

### 📅 Task 2: Event Registration System
A Django-powered application designed to manage public and private events, handle category grouping, and facilitate user registrations with real-time occupancy updates and cancellation capabilities.

*   **Technology Stack**: Python, Django, SQLite, Bootstrap CSS.
*   **Core Features**:
    *   **Event Exploration**: Users can browse upcoming events, filter by categories, and view detailed information.
    *   **Capacity Control**: Dynamically counts registered guests, computes occupancy percentage, and automatically flags events as "Full" once capacity limits are reached.
    *   **Unique Ticket Generation**: Confirmed registrations receive a uniquely generated ticket code (e.g. `EVT-XXXXXXXX`).
    *   **Management Dashboard**: Registered users can view their upcoming schedules and cancel registrations.
*   **Key Database Models**:
    *   [Category](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task2/events/models.py#L7): Groups events (e.g. Workshops, Concerts) and customises icons.
    *   [Event](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task2/events/models.py#L23): Represents scheduled events with dates, times, locations, capacity limits, and organizers.
    *   [Registration](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task2/events/models.py#L74): Maps users to events, holds unique ticket codes, and tracks confirmation states.

---

### 🍳 Task 3: Restaurant Management System
A comprehensive management platform serving restaurant operators, kitchen staff, and customers. It synchronizes menu offerings, table layouts, bookings, orders, and ingredient stock.

*   **Technology Stack**: Python, Django, SQLite, Custom CSS.
*   **Core Features**:
    *   **Menu & Inventory Linking**: Menu items are tied to specific inventory ingredients. Placing an order automatically checks availability and deducts quantities from the inventory.
    *   **Interactive Table Tracker**: Monitors tables as *Available*, *Reserved*, or *Occupied*.
    *   **Reservation Bookings**: Allows customers to request reservations which staff can assign to specific tables and update to *Confirmed* or *Cancelled*.
    *   **Order & Bill Processing**: Places orders for specific tables, tracks kitchen preparation status, and computes billing totals.
*   **Key Database Models**:
    *   [MenuItem](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task3/restaurant/models.py#L4): Stores dish names, descriptions, prices, categories, and availability status.
    *   [Table](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task3/restaurant/models.py#L22): Represents dining tables, their guest capacities, and current occupancy states.
    *   [Reservation](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task3/restaurant/models.py#L36): Stores booking details, times, guest counts, and status.
    *   [Order](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task3/restaurant/models.py#L55) / [OrderItem](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task3/restaurant/models.py#L71): Manages table orders, individual items, quantities, and totals.
    *   [InventoryItem](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task3/restaurant/models.py#L81) / [MenuItemIngredient](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task3/restaurant/models.py#L91): Tracks stock volumes, units, reorder levels, and details how much of each ingredient is required for menu items.

---

### 💼 Task 4: Job Board Platform
An end-to-end jobs marketplace connecting employers with job seekers. It supports distinct portal experiences tailored to the user's role.

*   **Technology Stack**: Python, Django, SQLite, Custom CSS, JS.
*   **Core Features**:
    *   **Role-Based Access Control**: Users register as either a **Job Seeker (Candidate)** or an **Employer**, unlocking dedicated dashboard panels.
    *   **Employer Suite**: Custom profiles detailing company info, job posting creation, and application tracking (Reviewing, Shortlisted, Accepted, Rejected).
    *   **Candidate Portal**: Custom profile editor supporting skill tags, bio, experience details, resume uploads, and job search filters.
    *   **Application Pipeline**: Candidates can write cover letters, attach custom resumes, and track their application progress.
*   **Key Database Models**:
    *   [UserProfile](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task4/board/models.py#L4): Distinguishes roles (Candidate vs Employer) linked to Django's standard User.
    *   [EmployerProfile](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task4/board/models.py#L15): Details company info, websites, logos, and descriptions.
    *   [CandidateProfile](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task4/board/models.py#L26): Manages resume files, experience summaries, education, and skill lists.
    *   [JobListing](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task4/board/models.py#L37): Contains job descriptions, requirements, types (Full-Time, Remote, etc.), and categories.
    *   [JobApplication](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Backend/Task4/board/models.py#L59): Pairs candidates to jobs, tracking application statuses, application resumes, and cover letters.

---

## 🚀 Installation & Setup Instructions

### 📋 Prerequisites
Ensure you have **Python 3.8+** and `pip` installed on your machine.

### ⚙️ Step-by-Step Installation
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/YourUsername/CodeAlpha_ProjectName.git
    cd CodeAlpha_ProjectName
    ```

2.  **Create and Activate a Virtual Environment** (Highly Recommended):
    *   **On Windows**:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    *   **On macOS/Linux**:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install Required Dependencies**:
    Create a `requirements.txt` file or run:
    ```bash
    pip install django flask pillow
    ```

---

## 🏃 Running the Projects

You can run each application independently by navigating to its respective folder:

### Run Task 1 (Flask URL Shortener)
```bash
cd Task1
python app.py
```
*   The Flask application will start running on **`http://127.0.0.1:5000/`**.

### Run Task 2 (Event Registration System)
```bash
cd Task2
python manage.py migrate
python manage.py runserver 8000
```
*   Access the Event Manager at **`http://127.0.0.1:8000/`**.

### Run Task 3 (Restaurant Management System)
```bash
cd Task3
python manage.py migrate
python manage.py runserver 8001
```
*   Access the Restaurant Manager at **`http://127.0.0.1:8001/`**.

### Run Task 4 (Job Board Platform)
```bash
cd Task4
python manage.py migrate
python manage.py runserver 8002
```
*   Access the Job Board at **`http://127.0.0.1:8002/`**.

---

## 🤝 Contact Information
For questions or inquiries regarding the implementations:
*   **Website**: [www.codealpha.tech](http://www.codealpha.tech)
*   **WhatsApp Support**: [+91 9336576683](https://wa.me/919336576683)
*   **Email Support**: [services@codealpha.tech](mailto:services@codealpha.tech) | [services.codealpha@gmail.com](mailto:services.codealpha@gmail.com)
