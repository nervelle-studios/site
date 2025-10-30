from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = 'nervelle_secret_key'
db = SQLAlchemy(app)

# --- Database model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='client')  # 'admin' or 'client'

# --- Create tables ---
with app.app_context():
    db.create_all()
    # Ensure one admin exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()

# --- Routes ---
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            session['role'] = user.role
            flash('Login successful! Redirecting...', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('client'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html', username=session['user'])

@app.route('/client')
def client():
    if 'user' not in session or session.get('role') != 'client':
        return redirect(url_for('login'))
    return render_template('client.html', username=session['user'])

if __name__ == '__main__':
    app.run(debug=True)
