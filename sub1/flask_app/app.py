from flask import Flask, render_template, request, redirect, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'  

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('DROP TABLE IF EXISTS users')
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id TEXT NOT NULL UNIQUE,
                     username TEXT NOT NULL,
                     email TEXT NOT NULL UNIQUE,
                     course TEXT NOT NULL,
                     password TEXT NOT NULL)''')
    conn.commit()
    conn.close()
init_db()

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    user_id = request.form['user_id']
    username = request.form['username']
    email = request.form['email']
    course = request.form['course']
    password = request.form['password']

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid email address"

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    if user:
        conn.close()
        return "Email already registered."

    conn.execute('INSERT INTO users (user_id, username, email, course, password) VALUES (?, ?, ?, ?, ?)',
                 (user_id, username, email, course, password))
    conn.commit()
    conn.close()

    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()
        if user:
            # Store user info in the session
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['course'] = user['course']
            return redirect('/dashboard')
        else:
            return "Invalid credentials"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Make sure the user is logged in
    if 'email' not in session:
        return redirect('/login')

    current_user = {
        'user_id': session['user_id'],
        'username': session['username'],
        'email': session['email'],
        'course': session['course']
    }

    conn = get_db_connection()
    other_users = conn.execute('SELECT username, course FROM users WHERE email != ?', (session['email'],)).fetchall()
    conn.close()

    return render_template('dashboard.html', current_user=current_user, other_users=other_users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
