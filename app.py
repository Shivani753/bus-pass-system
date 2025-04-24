from flask import Flask, render_template, request, redirect, session, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Firebase setup
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        phone = request.form['phone']

        # Check if the email already exists
        user_ref = db.collection("Users").where("email", "==", email).stream()
        if any(user for user in user_ref):
            return "Email already exists. Please try again."

        # Save user data to Firestore
        user_data = {
            "name": name,
            "email": email,
            "password": password,
            "user_type": user_type,
            "phone": phone
        }
        db.collection("Users").add(user_data)
        return redirect('/login')

    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch user data from Firestore
        user_ref = db.collection("Users").where("email", "==", email).stream()
        user_data = next(user_ref, None)

        if user_data and user_data.to_dict().get("password") == password:
            session['user'] = email
            return redirect('/dashboard')
        else:
            return "Login failed. Invalid credentials."

    return render_template('login.html')

# Dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        # Fetch user data from Firestore to display on dashboard
        user_ref = db.collection("Users").where("email", "==", session['user']).stream()
        user_data = next(user_ref, None).to_dict()
        return render_template('dashboard.html', user=user_data)
    return redirect('/login')

# Apply for bus pass
@app.route('/apply_bus_pass', methods=['GET', 'POST'])
def apply_bus_pass():
    if 'user' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        email = session['user']
        start_date = request.form['start_date']
        expiry_date = request.form['expiry_date']
        pass_type = request.form['pass_type']
        route = request.form['route']
        amount = request.form['amount']

        # Save bus pass data to Firestore
        bus_pass_data = {
            "email": email,
            "start_date": datetime.strptime(start_date, '%Y-%m-%d'),
            "expiry_date": datetime.strptime(expiry_date, '%Y-%m-%d'),
            "pass_type": pass_type,
            "route": route,
            "amount": amount
        }
        db.collection("BusPass").add(bus_pass_data)
        return redirect('/dashboard')

    return render_template('apply_bus_pass.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
