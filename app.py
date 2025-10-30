import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-env")
DATABASE_URL = os.environ.get("DATABASE_URL")  # If provided, should be a SQLAlchemy compatible URL (e.g. postgres://...)
if DATABASE_URL:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    site_link = db.Column(db.String(1024), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Helpers
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)

def login_user(user):
    session["user_id"] = user.id

def logout_user():
    session.pop("user_id", None)

# Create DB and admin user if env set
@app.before_first_request
def ensure_db_and_admin():
    db.create_all()
    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if admin_username and admin_password:
        admin = User.query.filter_by(username=admin_username).first()
        if not admin:
            admin = User(
                username=admin_username,
                password_hash=generate_password_hash(admin_password),
                site_link="",
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Created admin user from environment variables.")

# Routes
@app.route("/")
def index():
    user = current_user()
    if user:
        if user.is_admin:
            return redirect(url_for("admin_dashboard"))
        return render_template("dashboard.html", user=user)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# Admin area
def require_admin():
    user = current_user()
    if not user or not user.is_admin:
        abort(403)

@app.route("/admin")
def admin_dashboard():
    require_admin()
    users = User.query.filter(User.is_admin == False).all()
    return render_template("admin.html", users=users)

@app.route("/admin/create", methods=["GET","POST"])
def admin_create_user():
    require_admin()
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        site_link = request.form.get("site_link","").strip()
        if not username or not password:
            flash("Username and password required", "danger")
            return redirect(url_for("admin_create_user"))
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash("User already exists", "danger")
            return redirect(url_for("admin_create_user"))
        new = User(username=username, password_hash=generate_password_hash(password), site_link=site_link, is_admin=False)
        db.session.add(new)
        db.session.commit()
        flash("User created", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_create.html")

@app.route("/admin/edit/<int:user_id>", methods=["GET","POST"])
def admin_edit_user(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        site_link = request.form.get("site_link","").strip()
        password = request.form.get("password","")
        user.site_link = site_link
        if password:
            user.password_hash = generate_password_hash(password)
        db.session.commit()
        flash("User updated", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_edit.html", u=user)

@app.route("/admin/delete/<int:user_id>", methods=["POST"])
def admin_delete_user(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted", "info")
    return redirect(url_for("admin_dashboard"))

# API endpoint for embed (optional)
@app.route("/api/user-info")
def api_user_info():
    user = current_user()
    if not user:
        return {"error":"not authenticated"}, 401
    return {"username":user.username, "site_link":user.site_link, "is_admin":user.is_admin}

# Run locally
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
