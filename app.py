from flask import Flask, render_template, request, redirect, url_for, session
from google.cloud import firestore
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Firestore client setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "your-credentials.json"  # Place in Render secrets
db = firestore.Client()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = db.collection('Users').where('email', '==', email).where('password', '==', password).get()
        if users:
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    user_email = session['user_email']
    bus_pass = db.collection('BusPass').where('email', '==', user_email).get()
    pass_data = None

    if bus_pass:
        doc = bus_pass[0]
        data = doc.to_dict()
        pass_data = {
            'pass_type': data['pass_type'],
            'route': data['route'],
            'start_date': data['start_date'].strftime('%Y-%m-%d'),
            'expiry_date': data['expiry_date'].strftime('%Y-%m-%d'),
            'amount': data['amount']
        }

    return render_template('dashboard.html', user_email=user_email, pass_data=pass_data)

@app.route('/apply', methods=['POST'])
def apply_pass():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    email = session['user_email']
    pass_type = request.form['pass_type']
    route = request.form['route']
    start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
    amount = float(request.form['amount'])

    expiry_date = start_date + timedelta(days=30)

    pass_data = {
        'email': email,
        'pass_type': pass_type,
        'route': route,
        'start_date': start_date,
        'expiry_date': expiry_date,
        'amount': amount
    }

    db.collection('BusPass').add(pass_data)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
