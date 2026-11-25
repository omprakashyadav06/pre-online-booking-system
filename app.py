from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

app = Flask(__name__)

# Load variables from .env
load_dotenv()

# Flask session security
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# JWT security
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

jwt = JWTManager(app)





# ---------- DATABASE ----------
# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Existing bookings table
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  service TEXT,
                  location TEXT,
                  branch TEXT,
                  date TEXT,
                  time TEXT,
                  purpose TEXT)''')

    # New users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route('/')
def index():
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("index.html", today=today)

# ---------- BOOK ----------
@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    service = request.form['service']
    location = request.form['location']
    branch = request.form['branch']
    date = request.form['date']
    time = request.form['time']
    purpose = request.form['purpose']

    if not name or not service or not location or not branch or not date or not time or not purpose:
        return "❌ All fields required"

    today = datetime.now().strftime("%Y-%m-%d")
    if date < today:
        return "❌ Cannot book past date"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM bookings WHERE date=? AND time=? AND branch=?", (date, time, branch))
    if c.fetchone():
        conn.close()
        return "❌ Slot already booked in this branch"

    c.execute("INSERT INTO bookings (name, service, location, branch, date, time, purpose) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (name, service, location, branch, date, time, purpose))

    conn.commit()
    conn.close()

    return render_template("success.html")

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect('/admin')
        else:
            return "❌ Invalid Login"

    return render_template("login.html")
# ---------- USER REGISTRATION API ----------

@app.route('/api/register', methods=['POST'])
def register_user():

    # 1. Check whether request contains valid JSON
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    # 2. Get username and password
    username = data.get("username")
    password = data.get("password")

    # 3. Validate input types
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({
            "message": "Username and password must be text"
        }), 400

    username = username.strip()

    # 4. Check empty values
    if not username or not password.strip():
        return jsonify({
            "message": "Username and password are required"
        }), 400

    # 5. Validate username length
    if len(username) < 3 or len(username) > 30:
        return jsonify({
            "message": "Username must contain 3 to 30 characters"
        }), 400

    # 6. Validate password length
    if len(password) < 8:
        return jsonify({
            "message": "Password must contain at least 8 characters"
        }), 400

    # 7. Hash password
    hashed_password = generate_password_hash(password)

    # 8. Connect to database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_password, "user")
        )

        conn.commit()

        return jsonify({
            "message": "User registered successfully",
            "username": username
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "message": "Username already exists"
        }), 409

    finally:
        conn.close()

# ---------- JWT LOGIN API ----------
# ---------- JWT LOGIN API ----------
# ---------- JWT LOGIN API ----------

@app.route('/api/login', methods=['POST'])
def api_login():

    # 1. Check valid JSON
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Valid JSON data is required"
        }), 400

    # 2. Get username and password
    username = data.get("username")
    password = data.get("password")

    # 3. Validate input types
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({
            "message": "Username and password must be text"
        }), 400

    username = username.strip()

    # 4. Check empty values
    if not username or not password.strip():
        return jsonify({
            "message": "Username and password are required"
        }), 400

    # 5. Connect to database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    try:
        c.execute(
            "SELECT username, password, role FROM users WHERE username = ?",
            (username,)
        )

        user = c.fetchone()

    finally:
        conn.close()

    # 6. Verify password
    if user and check_password_hash(user[1], password):

        # 7. Generate JWT tokens
        access_token = create_access_token(identity=user[0])
        refresh_token = create_refresh_token(identity=user[0])

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "username": user[0],
            "role": user[2]
        }), 200

    # 8. Invalid credentials
    return jsonify({
        "message": "Invalid username or password"
    }), 401

# ---------- JWT USER PROFILE API ----------
@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_current_user():

    current_user = get_jwt_identity()

    return jsonify({
        "message": "Authenticated user",
        "username": current_user
    }), 200
# ---------- JWT REFRESH API ----------
@app.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():

    current_user = get_jwt_identity()

    new_access_token = create_access_token(
        identity=current_user
    )

    return jsonify({
        "message": "New access token generated",
        "access_token": new_access_token
    }), 200
# ---------- ADMIN ----------
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    data = c.fetchall()
    conn.close()

    return render_template("admin.html", bookings=data)

# ---------- DELETE ----------
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):

    # Check whether admin is logged in
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("DELETE FROM bookings WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for('admin'))

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ---------- REST API: GET ALL BOOKINGS ----------

@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):

    # 1. Validate booking ID
    if booking_id <= 0:
        return jsonify({
            "error": "Booking ID must be a positive number"
        }), 400

    # 2. Get logged-in username
    current_user = get_jwt_identity()

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        # 3. Find logged-in user's ID and role
        c.execute(
            "SELECT id, role FROM users WHERE username = ?",
            (current_user,)
        )
        user = c.fetchone()

        if user is None:
            return jsonify({"error": "User not found"}), 404

        # 4. Find requested booking
        c.execute(
            "SELECT * FROM bookings WHERE id = ?",
            (booking_id,)
        )
        booking = c.fetchone()

        if booking is None:
            return jsonify({"error": "Booking not found"}), 404

        # 5. Check ownership or admin permission
        if user["role"] != "admin" and booking["user_id"] != user["id"]:
            return jsonify({
                "error": "You cannot access this booking"
            }), 403

        # 6. Return booking details
        return jsonify(dict(booking)), 200

    finally:
        conn.close()






# ---------- REST API: CREATE BOOKING ----------

@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():

    # 1. Get logged-in username from JWT
    current_user = get_jwt_identity()

    # 2. Validate JSON
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    # 3. Check required fields
    required_fields = [
        'name', 'service', 'location',
        'branch', 'date', 'time', 'purpose'
    ]

    for field in required_fields:
        value = data.get(field)

        if not isinstance(value, str) or not value.strip():
            return jsonify({
                "error": field + " is required and must be text"
            }), 400

    # 4. Remove unnecessary spaces
    name = data['name'].strip()
    service = data['service'].strip()
    location = data['location'].strip()
    branch = data['branch'].strip()
    date = data['date'].strip()
    time = data['time'].strip()
    purpose = data['purpose'].strip()

    # 5. Validate date format
    try:
        booking_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({
            "error": "Invalid date format. Use YYYY-MM-DD"
        }), 400

    # 6. Prevent past dates
    today = datetime.now().date()

    if booking_date < today:
        return jsonify({
            "error": "Cannot book past date"
        }), 400

    # 7. Validate time format
    try:
        datetime.strptime(time, "%H:%M")
    except ValueError:
        return jsonify({
            "error": "Invalid time format. Use HH:MM"
        }), 400

    # 8. Connect to database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    try:
        # 9. Find logged-in user's ID
        c.execute(
            "SELECT id FROM users WHERE username = ?",
            (current_user,)
        )

        user = c.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = user[0]

        # 10. Check duplicate booking slot
        c.execute(
            """SELECT id FROM bookings
            WHERE date = ? AND time = ? AND branch = ?""",
            (date, time, branch)
        )

        if c.fetchone():
            return jsonify({
                "error": "Slot already booked in this branch"
            }), 409

        # 11. Insert booking with user ID
        c.execute(
            """INSERT INTO bookings
            (name, service, location, branch, date, time, purpose, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name, service, location, branch,
                date, time, purpose, user_id
            )
        )

        booking_id = c.lastrowid
        conn.commit()

        return jsonify({
            "message": "Booking created successfully",
            "booking_id": booking_id,
            "user_id": user_id,
            "username": current_user
        }), 201

    finally:
        conn.close()



# ---------- REST API: UPDATE BOOKING ----------

# ---------- REST API: UPDATE BOOKING ----------

@app.route('/api/bookings/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):

    # 1. Validate booking ID
    if booking_id <= 0:
        return jsonify({"error": "Booking ID must be positive"}), 400

    current_user = get_jwt_identity()

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        # 2. Get logged-in user's ID and role
        c.execute(
            "SELECT id, role FROM users WHERE username = ?",
            (current_user,)
        )
        user = c.fetchone()

        if user is None:
            return jsonify({"error": "User not found"}), 404

        # 3. Find the booking
        c.execute(
            "SELECT * FROM bookings WHERE id = ?",
            (booking_id,)
        )
        booking = c.fetchone()

        if booking is None:
            return jsonify({"error": "Booking not found"}), 404

        # 4. Check ownership or admin permission
        if user["role"] != "admin" and booking["user_id"] != user["id"]:
            return jsonify({
                "error": "You cannot update this booking"
            }), 403

        # 5. Validate JSON
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Valid JSON data is required"}), 400

        required_fields = [
            "name", "service", "location",
            "branch", "date", "time", "purpose"
        ]

        for field in required_fields:
            value = data.get(field)

            if not isinstance(value, str) or not value.strip():
                return jsonify({
                    "error": field + " is required and must be text"
                }), 400

        # 6. Remove unnecessary spaces
        name = data["name"].strip()
        service = data["service"].strip()
        location = data["location"].strip()
        branch = data["branch"].strip()
        date = data["date"].strip()
        time = data["time"].strip()
        purpose = data["purpose"].strip()

        # 7. Validate date format
        try:
            booking_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({
                "error": "Invalid date format. Use YYYY-MM-DD"
            }), 400

        if booking_date < datetime.now().date():
            return jsonify({"error": "Cannot book past date"}), 400

        # 8. Validate time format
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return jsonify({
                "error": "Invalid time format. Use HH:MM"
            }), 400

        # 9. Check duplicate slot
        c.execute(
            """SELECT id FROM bookings
            WHERE date = ? AND time = ? AND branch = ? AND id != ?""",
            (date, time, branch, booking_id)
        )

        if c.fetchone():
            return jsonify({"error": "Slot already booked"}), 409

        # 10. Update booking
        c.execute(
            """UPDATE bookings
            SET name=?, service=?, location=?, branch=?,
                date=?, time=?, purpose=?
            WHERE id=?""",
            (
                name, service, location, branch,
                date, time, purpose, booking_id
            )
        )

        conn.commit()

        return jsonify({
            "message": "Booking updated successfully",
            "booking_id": booking_id
        }), 200

    finally:
        conn.close()





# ---------- REST API: DELETE BOOKING ----------

# ---------- REST API: DELETE BOOKING ----------

# ---------- REST API: DELETE BOOKING ----------

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def delete_booking_api(booking_id):

    # 1. Validate booking ID
    if booking_id <= 0:
        return jsonify({
            "error": "Booking ID must be positive"
        }), 400

    current_user = get_jwt_identity()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    try:
        # 2. Get logged-in user's ID and role
        c.execute(
            "SELECT id, role FROM users WHERE username = ?",
            (current_user,)
        )
        user = c.fetchone()

        if not user:
            return jsonify({"message": "User not found"}), 404

        user_id = user[0]
        role = user[1]

        # 3. Check whether booking exists
        c.execute(
            "SELECT * FROM bookings WHERE id = ?",
            (booking_id,)
        )
        booking = c.fetchone()

        if booking is None:
            return jsonify({"error": "Booking not found"}), 404

        # 4. Check ownership (admins can delete any booking)
        if role != "admin" and booking[8] != user_id:
            return jsonify({
                "error": "You cannot delete this booking"
            }), 403

        # 5. Delete booking
        c.execute(
            "DELETE FROM bookings WHERE id = ?",
            (booking_id,)
        )

        conn.commit()

        return jsonify({
            "message": "Booking deleted successfully",
            "booking_id": booking_id
        }), 200

    finally:
        conn.close()
        

# ---------- REST API: MY BOOKINGS ----------

@app.route('/api/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():

    current_user = get_jwt_identity()

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute(
            "SELECT id FROM users WHERE username = ?",
            (current_user,)
        )
        user = c.fetchone()

        if user is None:
            return jsonify({"message": "User not found"}), 404

        user_id = user["id"]

        c.execute(
            "SELECT * FROM bookings WHERE user_id = ?",
            (user_id,)
        )
        bookings = c.fetchall()

        result = [dict(booking) for booking in bookings]

        return jsonify({
            "username": current_user,
            "user_id": user_id,
            "total_bookings": len(result),
            "bookings": result
        }), 200

    finally:
        conn.close()

# ---------- REST API: ADMIN VIEW ALL BOOKINGS ----------

@app.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_all_bookings():

    current_user = get_jwt_identity()

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute(
            "SELECT id, role FROM users WHERE username = ?",
            (current_user,)
        )
        user = c.fetchone()

        if user is None:
            return jsonify({"error": "User not found"}), 404

        if user["role"] != "admin":
            return jsonify({"error": "Admin access required"}), 403

        c.execute("SELECT * FROM bookings")
        bookings = c.fetchall()

        result = [dict(booking) for booking in bookings]

        return jsonify({
            "total_bookings": len(result),
            "bookings": result
        }), 200

    finally:
        conn.close()
# ---------- HEALTH CHECK API ----------
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Booking API is running"
    }), 200

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
