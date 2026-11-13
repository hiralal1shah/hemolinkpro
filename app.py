
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

app = Flask(__name__)

# Development secret key
app.secret_key = "hemolink_pro_development_key"


# ---------------- HOME PAGE ----------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------- REGISTRATION ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        city = request.form.get("city", "").strip()
        role = request.form.get("role", "donor").strip().lower()

        blood_group = request.form.get("blood_group", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()

        if not all([full_name, email, phone, password, city]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("register"))

        if role not in ["donor", "seeker"]:
            flash("Invalid user role.", "error")
            return redirect(url_for("register"))

        if role == "donor":

            if not all([blood_group, age, gender]):
                flash("Please provide your blood group, age and gender.", "error")
                return redirect(url_for("register"))

            try:
                age = int(age)
            except ValueError:
                flash("Please enter a valid age.", "error")
                return redirect(url_for("register"))

            if age < 18:
                flash("Donor registration requires age 18 or above.", "error")
                return redirect(url_for("register"))

            valid_blood_groups = [
                "A+", "A-", "B+", "B-",
                "AB+", "AB-", "O+", "O-"
            ]

            if blood_group not in valid_blood_groups:
                flash("Please select a valid blood group.", "error")
                return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        connection = get_db_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (full_name, email, password_hash, role, phone, city)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (full_name, email, password_hash, role, phone, city)
            )

            user_id = cursor.lastrowid

            if role == "donor":

                cursor.execute(
                    """
                    INSERT INTO donors
                    (user_id, blood_group, age, gender)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, blood_group, age, gender)
                )

            connection.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        except Exception as error:
            connection.rollback()

            if "UNIQUE constraint failed" in str(error):
                flash("This email is already registered.", "error")
            else:
                flash("Registration failed. Please try again.", "error")

            print("Registration error:", error)

        finally:
            connection.close()

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "error")
            return redirect(url_for("login"))

        connection = get_db_connection()

        try:
            user = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

            if user and check_password_hash(
                user["password_hash"], password
            ):

                session["user_id"] = user["user_id"]
                session["full_name"] = user["full_name"]
                session["role"] = user["role"]

                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid email or password.", "error")

        finally:
            connection.close()

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# ---------------- BLOOD REQUEST ----------------

@app.route("/request", methods=["GET", "POST"])
def blood_request():

    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":

        blood_group = request.form.get("blood_group", "").strip()
        units = request.form.get("units_requested", "").strip()
        hospital_name = request.form.get("hospital_name", "").strip()
        city = request.form.get("city", "").strip()
        urgency = request.form.get("urgency", "Normal").strip()

        valid_blood_groups = [
            "A+", "A-", "B+", "B-",
            "AB+", "AB-", "O+", "O-"
        ]

        if not all([blood_group, units, hospital_name, city, urgency]):
            flash("Please fill in all blood request details.", "error")
            return redirect(url_for("blood_request"))

        if blood_group not in valid_blood_groups:
            flash("Please select a valid blood group.", "error")
            return redirect(url_for("blood_request"))

        try:
            units = int(units)
        except ValueError:
            flash("Please enter a valid number of units.", "error")
            return redirect(url_for("blood_request"))

        if units <= 0:
            flash("Units requested must be greater than zero.", "error")
            return redirect(url_for("blood_request"))

        if urgency not in ["Normal", "Urgent", "Critical"]:
            flash("Invalid urgency selection.", "error")
            return redirect(url_for("blood_request"))

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO blood_requests
                (seeker_id, blood_group, units_requested,
                 hospital_name, city, urgency)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    blood_group,
                    units,
                    hospital_name,
                    city,
                    urgency
                )
            )

            connection.commit()

            flash("Blood request submitted successfully!", "success")
            return redirect(url_for("dashboard"))

        except Exception as error:
            connection.rollback()
            print("Blood request error:", error)
            flash("Unable to submit your request. Please try again.", "error")

        finally:
            connection.close()

    return render_template("request.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
