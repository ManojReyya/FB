"""
FBAIS - Food Business AI System
Restaurant profitability prediction, inventory management, and waste tracking
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from functools import wraps
import secrets
import sys
import re
import bcrypt
from dotenv import load_dotenv

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "features"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "machine_learning"))

from features.inventory import inventory_bp, inventory_init_recipes  # noqa: E402
from features.profit import profit_bp, init_predictor  # noqa: E402
from features.waste import waste_bp  # noqa: E402
from features.customer import customer_bp, init_customer_predictor  # noqa: E402

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, supports_credentials=True)

app.config["DEBUG"] = os.getenv("DEBUG", "True").lower() == "true"
app.config["DATABASE"] = os.getenv("DATABASE_PATH", "data/fbais.db")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))
app.config["WTF_CSRF_ENABLED"] = True
app.config["WTF_CSRF_TIME_LIMIT"] = None

csrf = CSRFProtect(app)


def load_all_data():
    """Initialize database, models, and recipes"""
    try:
        init_predictor()
        init_database()
        inventory_init_recipes()
        init_customer_predictor()
        print("✓ All systems ready")
        return True
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return False


# ========================================
# DATABASE
# ========================================


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Create database tables"""
    Path("data").mkdir(exist_ok=True)

    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            business_name TEXT,
            phone TEXT,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """
    )

    # Waste tracking tables
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS waste_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            date_recorded DATE NOT NULL,
            cost_value REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    )

    # Migrate existing waste_entries if needed
    cursor.execute("PRAGMA table_info(waste_entries)")
    columns = [col[1] for col in cursor.fetchall()]
    if "user_id" not in columns:
        # Add user_id column to existing table
        cursor.execute("ALTER TABLE waste_entries ADD COLUMN user_id INTEGER")
        # Set default user_id to 1 for existing entries (or delete them)
        cursor.execute("UPDATE waste_entries SET user_id = 1 WHERE user_id IS NULL")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS waste_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            average_cost_per_unit REAL DEFAULT 0
        )
    """
    )

    # Insert default waste categories
    cursor.execute("SELECT COUNT(*) FROM waste_categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ("Vegetables", 2.5),
            ("Fruits", 3.0),
            ("Dairy", 4.5),
            ("Meat", 8.0),
            ("Bread & Grains", 2.0),
            ("Condiments", 3.5),
            ("Other", 2.0),
        ]
        cursor.executemany(
            "INSERT INTO waste_categories (name, average_cost_per_unit) VALUES (?, ?)", categories
        )

    conn.commit()
    conn.close()
    print("✓ Database ready")


# ========================================
# INPUT SANITIZATION
# ========================================


def sanitize_string(text, max_length=255):
    """Sanitize text input"""
    if not text:
        return ""
    text = str(text).strip()
    text = text[:max_length]
    return text


def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def sanitize_numeric(value, min_val=None, max_val=None, default=0):
    """Sanitize numeric input"""
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return default
        if max_val is not None and num > max_val:
            return default
        return num
    except (ValueError, TypeError):
        return default


# ========================================
# AUTHENTICATION
# ========================================


def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=int(os.getenv("BCRYPT_LOG_ROUNDS", 12)))
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password, password_hash):
    """Verify password using bcrypt"""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def login_required(f):
    """Protect routes requiring authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("landing"))
        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    """Get current user"""
    if "user_id" not in session:
        return None

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))
    user = cursor.fetchone()
    conn.close()
    return user


# ========================================
# PAGE ROUTES
# ========================================


@app.route("/")
def index():
    """Home page"""
    if "user_id" in session:
        return render_template("dashboard.html")
    return render_template("landing.html")


@app.route("/landing")
def landing():
    """Landing page"""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard"""
    user = get_current_user()
    return render_template("dashboard.html", user=user)


@app.route("/profitability-prediction")
@login_required
def profitability_prediction():
    """Profitability predictor"""
    return render_template("profit.html")


@app.route("/inventory-recipes")
@login_required
def inventory_recipes():
    """Inventory management"""
    return render_template("inventory.html")


@app.route("/customer-personas")
@login_required
def customer_personas():
    """Customer persona analysis"""
    return render_template("customer.html")


@app.route("/profile")
@login_required
def profile():
    """User profile"""
    user = get_current_user()
    return render_template("profile.html", user=user)


# ========================================
# AUTH APIs
# ========================================


@app.route("/api/login", methods=["POST"])
@csrf.exempt
def api_login():
    """Login endpoint"""
    data = request.get_json()
    email = sanitize_string(data.get("email", ""), max_length=255)
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"}), 400

    if not validate_email(email):
        return jsonify({"success": False, "error": "Invalid email format"}), 400

    if len(password) > 128:
        return jsonify({"success": False, "error": "Password too long"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user or not verify_password(password, user["password_hash"]):
            conn.close()
            return jsonify({"success": False, "error": "Invalid credentials"}), 401

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now(), user["id"]))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Login successful"})

    except Exception:
        return jsonify({"success": False, "error": "An error occurred"}), 500


@app.route("/api/register", methods=["POST"])
@csrf.exempt
def api_register():
    """Registration endpoint"""
    data = request.get_json()
    name = sanitize_string(data.get("full_name", ""), max_length=100)
    email = sanitize_string(data.get("email", ""), max_length=255)
    business = sanitize_string(data.get("business_name", ""), max_length=200)
    password = data.get("password", "")

    if not all([name, email, password]):
        return jsonify({"success": False, "error": "Name, email, and password required"}), 400

    if not validate_email(email):
        return jsonify({"success": False, "error": "Invalid email format"}), 400

    if len(password) < 8:
        return jsonify({"success": False, "error": "Password must be 8+ characters"}), 400

    if len(password) > 128:
        return jsonify({"success": False, "error": "Password too long"}), 400

    password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    if not re.match(password_pattern, password):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Password must contain uppercase, lowercase, and numbers",
                }
            ),
            400,
        )

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users (name, email, business_name, password_hash)
            VALUES (?, ?, ?, ?)
        """,
            (name, email, business, hash_password(password)),
        )

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        session["user_id"] = user_id
        session["user_name"] = name
        session["user_email"] = email

        return jsonify({"success": True, "message": "Account created"})

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Email already registered"}), 409
    except Exception:
        return jsonify({"success": False, "error": "An error occurred"}), 500


@app.route("/api/logout")
@app.route("/logout")
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for("landing"))


@app.route("/api/update-profile", methods=["POST"])
@login_required
@csrf.exempt
def api_update_profile():
    """Update profile"""
    data = request.get_json()
    name = sanitize_string(data.get("name", ""), max_length=100)
    business = sanitize_string(data.get("business_name", ""), max_length=200)
    phone = sanitize_string(data.get("phone", ""), max_length=20)

    if not name:
        return jsonify({"success": False, "error": "Name required"}), 400

    if phone and not re.match(r"^\+?[\d\s-]{10,20}$", phone):
        return jsonify({"success": False, "error": "Invalid phone number"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users SET name = ?, business_name = ?, phone = ? WHERE id = ?
        """,
            (name, business, phone, session["user_id"]),
        )

        conn.commit()
        conn.close()

        session["user_name"] = name
        return jsonify({"success": True, "message": "Profile updated"})
    except Exception:
        return jsonify({"success": False, "error": "An error occurred"}), 500


# ========================================
# SYSTEM
# ========================================


@app.route("/health", methods=["GET"])
def health():
    """Health check"""
    return jsonify(
        {
            "status": "healthy",
            "app": "FBAIS",
            "version": "2.0",
            "features": ["Profitability Predictor", "Inventory", "Waste Tracker"],
        }
    )


# ========================================
# STARTUP
# ========================================

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("FBAIS - Food Business AI System")
    print("=" * 50)

    load_all_data()

    app.register_blueprint(inventory_bp)
    app.register_blueprint(profit_bp)
    app.register_blueprint(waste_bp)
    app.register_blueprint(customer_bp)

    # Exempt waste API endpoints from CSRF
    csrf.exempt(waste_bp)
    # Exempt inventory API endpoints from CSRF
    csrf.exempt(inventory_bp)
    # Exempt profit API endpoints from CSRF
    csrf.exempt(profit_bp)
    # Exempt customer API endpoints from CSRF
    csrf.exempt(customer_bp)

    print("\n✓ Server running on http://localhost:5000")
    print("=" * 50 + "\n")

    app.run(debug=True, host="0.0.0.0", port=5000)
