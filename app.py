from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_tables, save_history, get_history, connect_db, get_languages
from engine.converter import convert_code

import random
import smtplib
from email.mime.text import MIMEText

# ✅ SINGLE APP ONLY
app = Flask(__name__)
app.secret_key = "supersecretkey"

create_tables()


# 📧 SEND OTP
def send_otp(email, otp):
    sender_email = "reshmapal5131@gmail.com"
    sender_password = "ocfwdypezgazoktu"

    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = "OTP Verification"
    msg['From'] = sender_email
    msg['To'] = email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()


# 🏠 HOME
@app.route("/", methods=["GET", "POST"])
def home():

    output_code = ""
    languages = get_languages()

    if "user_id" in session:

        if request.method == "POST":
            source_code = request.form["source_code"]
            source_lang = request.form["source_lang"]
            target_lang = request.form["target_lang"]

            output_code = convert_code(source_code, source_lang, target_lang)

            save_history(
                session["user_id"],
                source_lang,
                target_lang,
                source_code,
                output_code
            )

        return render_template(
            "index.html",
            output_code=output_code,
            active_page="dashboard",
            logged_in=True,
            languages=languages
        )

    return render_template(
        "index.html",
        active_page="dashboard",
        logged_in=False,
        languages=languages
    )


# 👑 ADMIN DASHBOARD
@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied ❌"

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM history")
    total_conversions = cursor.fetchone()[0]

    cursor.execute("SELECT id, name, email, role FROM users")
    users = cursor.fetchall()

    cursor.execute("""
        SELECT users.name, history.source_language, history.target_language, history.timestamp
        FROM history
        JOIN users ON history.user_id = users.id
        ORDER BY history.id DESC
    """)
    history = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_conversions=total_conversions,
        users=users,
        history=history
    )


# 👥 ADMIN USERS
@app.route("/admin/users")
def admin_users():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied ❌"

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, role FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template("admin_users.html", users=users)


# 📜 ADMIN ACTIVITY
@app.route("/admin/activity")
def admin_activity():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied ❌"

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT users.name, history.source_language, history.target_language, history.timestamp
        FROM history
        JOIN users ON history.user_id = users.id
        ORDER BY history.id DESC
    """)

    history = cursor.fetchall()
    conn.close()

    return render_template("admin_activity.html", history=history)


# 🌐 MANAGE LANGUAGES
@app.route("/admin/languages")
def manage_languages():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied ❌"

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM languages")
    languages = cursor.fetchall()

    conn.close()

    return render_template("languages.html", languages=languages)


# ➕ ADD LANGUAGE
@app.route("/admin/add-language", methods=["POST"])
def add_language():

    if session.get("role") != "admin":
        return "Access Denied ❌"

    name = request.form["name"].lower()

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO languages (name) VALUES (?)", (name,))
        conn.commit()
    except:
        pass

    conn.close()
    return redirect("/admin/languages")


# ❌ DELETE LANGUAGE
@app.route("/admin/delete-language/<int:id>")
def delete_language(id):

    if session.get("role") != "admin":
        return "Access Denied ❌"

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM languages WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin/languages")


# 📜 HISTORY
@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    records = get_history(session["user_id"])

    return render_template(
        "history.html",
        records=records,
        active_page="history"
    )


# 📝 REGISTER WITH SAME PAGE OTP (FINAL FIXED)
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # 🔥 SEND OTP
        if "send_otp" in request.form:
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]

            otp = str(random.randint(100000, 999999))

            session["temp_user"] = {
                "name": name,
                "email": email,
                "password": generate_password_hash(password),
                "otp": otp
            }

            send_otp(email, otp)

            return render_template("register.html", otp_sent=True, name=name, email=email)

        # 🔥 VERIFY OTP
        elif "verify_otp" in request.form:
            user_otp = request.form["otp"]
            data = session.get("temp_user")

            if data and user_otp == data["otp"]:

                conn = connect_db()
                cursor = conn.cursor()

                try:
                    cursor.execute("SELECT * FROM users WHERE email = ?", (data["email"],))
                    if cursor.fetchone():
                        return render_template("register.html", otp_sent=True, error="Email already exists ❌")

                    cursor.execute("""
                        INSERT INTO users (name, email, password, role)
                        VALUES (?, ?, ?, 'user')
                    """, (data["name"], data["email"], data["password"]))

                    conn.commit()

                except Exception as e:
                    print(e)
                    return "Database error ❌"

                finally:
                    conn.close()

                session.pop("temp_user", None)

                flash("✅ Registered Successfully!", "success")
                return redirect("/login")

            else:
                return render_template("register.html", otp_sent=True, error="Invalid OTP ❌")

    return render_template("register.html", otp_sent=False)


# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["role"] = user[4]
            return redirect("/")
        else:
            return "Invalid email or password"

    return render_template("login.html")


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return render_template("logout.html")


# 👤 PROFILE
@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = connect_db()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE users
            SET name = ?, email = ?
            WHERE id = ?
        """, (name, email, session["user_id"]))

        conn.commit()
        session["user_name"] = name

    cursor.execute(
        "SELECT name, email FROM users WHERE id = ?",
        (session["user_id"],)
    )

    user = cursor.fetchone()
    conn.close()

    return render_template("profile.html", user=user, active_page="profile")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)