# Online Pre-Booking System

A web-based appointment booking application developed using Python, Flask, SQLite, HTML, CSS, and REST APIs. It allows users to register, authenticate, create and manage bookings, and access their booking records securely.

## Features

- User registration and login
- Password hashing
- JWT access and refresh tokens
- Appointment booking
- Booking validation and duplicate-slot prevention
- User-specific booking access
- Admin-only booking management
- Create, read, update, and delete (CRUD) operations
- SQLite database integration
- Environment-based secret key configuration

## Technologies Used

- Python
- Flask
- SQLite
- REST API
- JWT Authentication
- HTML5 and CSS3
- Git and GitHub
- Postman
- Python-dotenv

## Project Structure

```text
booking2/
├── static/
│   └── style.css
├── templates/
│   ├── admin.html
│   ├── index.html
│   └── layout.html
├── app.py
├── requirements.txt
├── .gitignore
├── .env
└── database.db
```

Note: `.env`, `database.db`, and `venv/` are local files and are excluded from Git tracking.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/omprakashyadav06/pre-online-booking-system.git
cd pre-online-booking-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a local `.env` file:

```env
FLASK_SECRET_KEY=your_generated_flask_secret
JWT_SECRET_KEY=your_generated_jwt_secret
```

Generate strong random values for both keys. Never commit `.env` to GitHub.

### 6. Run the application

```bash
python app.py
```

Open:

`http://127.0.0.1:5000`

## REST API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/register` | Register a user |
| POST | `/api/login` | User login |
| GET | `/api/me` | Get authenticated user |
| POST | `/api/refresh` | Refresh access token |
| POST | `/api/bookings` | Create booking |
| GET | `/api/bookings` | Get all bookings (admin) |
| GET | `/api/my-bookings` | Get logged-in user's bookings |
| GET | `/api/bookings/<booking_id>` | Get a booking |
| PUT | `/api/bookings/<booking_id>` | Update a booking |
| DELETE | `/api/bookings/<booking_id>` | Delete a booking |

### Browser Routes

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Home page |
| POST | `/book` | Submit booking form |
| GET, POST | `/login` | Browser-based login |
| GET | `/admin` | Admin page |
| POST | `/delete/<id>` | Delete booking from admin page |
| GET | `/logout` | Browser logout |

## Booking Fields

The booking API uses these fields:

- `name`
- `service`
- `location`
- `branch`
- `date`
- `time`
- `purpose`

The authenticated user's ID is associated with newly created API bookings.

## Authentication and Authorization

- Passwords are stored as hashes.
- Login returns an access token and refresh token.
- Protected API endpoints require JWT authentication.
- Access tokens expire after 15 minutes.
- Refresh tokens expire after 30 days.
- Normal users can access their own bookings.
- Admin users can access and manage all bookings.
- Unauthorized access is rejected.

## API Testing

Use Postman to test the REST API.

For protected endpoints, use:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Test registration, login, booking creation, retrieval, updating, deletion, ownership restrictions, and admin permissions.

## GitHub

Repository: https://github.com/omprakashyadav06/pre-online-booking-system

## Developer

**Omprakash Yadav Adimulam**

Computer Science Engineering Graduate

Python | Flask | SQL | REST APIs | Git | GitHub | Linux

