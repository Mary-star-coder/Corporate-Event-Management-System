# Corporate Event Management System

A full-stack web application built with FastAPI, PostgreSQL, SQLAlchemy, and HTML, CSS, and JavaScript.

## Project Overview

Corporate Event Management System allows users to discover corporate events, create accounts, log in, and register for events. It provides REST APIs for managing events and registrations.

## Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- Psycopg
- JWT Authentication

### Database
- PostgreSQL 17

## Features

- User Registration and Login
- Secure Password Hashing
- JWT Authentication
- Protected User Profile Endpoint
- Create, Read, Update, and Delete Events
- Event Registration
- Duplicate Registration Prevention
- Available Seats Management
- Pagination
- Event Search and Location Filtering
- API Documentation with Swagger UI
- Input Validation and Error Handling

## Project Structure

```text
Corporate-Event-Management/
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── css/
│   ├── js/
│   └── images/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── auth.py
│   ├── requirements.txt
│   └── .env
│
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Mary-star-coder/Corporate-Event-Management-System.git
cd Corporate-Event-Management-System
```

### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv
```

### 3. Activate Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file inside the backend folder:

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=corporate_event_db
DB_USER=postgres
DB_PASSWORD=YOUR_DATABASE_PASSWORD
JWT_SECRET_KEY=YOUR_SECRET_KEY
```

Replace the placeholder values with your own local credentials. Never publish `.env`.

### 6. Run Backend

From the backend folder:

```bash
python -m uvicorn app.main:app --reload
```

Backend URL:

http://127.0.0.1:8000

Swagger API Documentation:

http://127.0.0.1:8000/docs

### 7. Run Frontend

Open the frontend folder in VS Code and use Live Server to run `index.html`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/register | Register user |
| POST | /auth/login | Login user |
| GET | /auth/me | Get authenticated profile |
| POST | /events | Create event |
| GET | /events | Get all events |
| GET | /events/{event_id} | Get event details |
| PUT | /events/{event_id} | Update event |
| DELETE | /events/{event_id} | Delete event |
| POST | /registrations | Register for an event |
| GET | /registrations | Get registrations |
| GET | /registrations/{registration_id} | Get registration details |

## Database

The application uses PostgreSQL with SQLAlchemy ORM.

Database tables:
- Users
- Events
- Registrations

## Testing

API endpoints and validation have been tested using Swagger UI.

## AI Assistance Disclosure

AI tools were used for learning, debugging, code explanations, and documentation assistance. The project was reviewed and tested during development.

## Author

Student Project – Corporate Event Management System

## Git Workflow

The project is maintained using Git and GitHub.

- `main` branch contains the stable project version.
- Feature branches are used for separate development tasks.
- Changes are committed with meaningful commit messages.
- Completed changes are pushed to GitHub and merged into main.