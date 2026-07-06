from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  service TEXT,
                  location TEXT,
                  branch TEXT,
                  date TEXT,
                  time TEXT,
                  purpose TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route('/')
def index():
    return render_template("index.html")

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
@app.route('/delete/<int:id>')
def delete(id):
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

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)