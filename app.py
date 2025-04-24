from flask import Flask, render_template, request, redirect, session, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# File paths
USER_FILE = 'users.json'
PASS_FILE = 'passes.json'

# Ensure data files exist
for file in [USER_FILE, PASS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

def read_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = read_json(USER_FILE)
        email = request.form['email']
        if email in users:
            return 'User already exists'
        users[email] = {
            'name': request.form['name'],
            'password': request.form['password']
        }
        write_json(USER_FILE, users)
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = read_json(USER_FILE)
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            session['email'] = email
            return redirect('/dashboard')
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect('/login')
    passes = read_json(PASS_FILE)
    user_pass = passes.get(session['email'])
    return render_template('dashboard.html', user=session['email'], bus_pass=user_pass)

@app.route('/apply', methods=['GET', 'POST'])
def apply_pass():
    if 'email' not in session:
        return redirect('/login')
    if request.method == 'POST':
        passes = read_json(PASS_FILE)
        passes[session['email']] = {
            'route': request.form['route'],
            'duration': request.form['duration'],
            'status': 'Applied'
        }
        write_json(PASS_FILE, passes)
        return redirect('/dashboard')
    return render_template('apply_pass.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
