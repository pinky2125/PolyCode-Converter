from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import create_tables, save_history, get_history, delete_history, connect_db, get_languages, save_solution, save_suggestion, save_feedback, get_all_feedback, is_admin, make_admin, get_users_with_admin_status, get_profile, get_profile_by_username, get_profile_by_email, update_profile
from engine.converter import convert_code
from engine.analyzer import analyze_code

import random
import smtplib
from email.mime.text import MIMEText
import os
import threading
from dotenv import load_dotenv

load_dotenv()

# ✅ SINGLE APP ONLY
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

create_tables()


ALLOWED_UPLOAD_EXTENSIONS = {"py", "java", "cpp", "c", "txt"}


# 📧 SEND OTP
def send_otp(email, otp):
    def _send():
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            print("Missing email credentials")
            return

        msg = MIMEText(f"Your OTP is: {otp}")
        msg['Subject'] = "OTP Verification"
        msg['From'] = sender_email
        msg['To'] = email

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")
            
    threading.Thread(target=_send).start()


# 🏠 HOME
@app.route("/", methods=["GET", "POST"])
def home():

    output_code = ""
    solution = ""
    suggestion = ""
    languages = get_languages()

    if "user_id" in session:

        if request.method == "POST":
            source_code = request.form.get("source_code", "").strip()
            source_lang = request.form.get("source_lang", "").strip()
            target_lang = request.form.get("target_lang", "").strip()

            if not source_code or not source_lang or not target_lang:
                flash("Please enter code and choose both languages.", "error")
            else:
                output_code = convert_code(source_code, source_lang, target_lang)

                analysis = analyze_code(source_code, output_code, source_lang, target_lang)
                solution = analysis.get("solution", "")
                suggestion = analysis.get("suggestion", "")

                history_id = save_history(
                    session["user_id"],
                    source_lang,
                    target_lang,
                    source_code,
                    output_code
                )

                if history_id:
                    save_solution(history_id, session["user_id"], solution)
                    save_suggestion(history_id, session["user_id"], suggestion)

        return render_template(
            "index.html",
            output_code=output_code,
            solution=solution,
            suggestion=suggestion,
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


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file uploaded.", "error")
        return redirect("/")

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        flash("Please choose a file.", "error")
        return redirect("/")

    filename = secure_filename(uploaded_file.filename)
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        flash("Unsupported file type.", "error")
        return redirect("/")

    content = uploaded_file.read().decode("utf-8", errors="ignore")
    return render_template(
        "index.html",
        output_code="",
        solution="",
        suggestion="",
        active_page="dashboard",
        logged_in=True,
        languages=get_languages(),
        uploaded_code=content,
    )


@app.route("/api/convert", methods=["POST"])
def api_convert():
    data = request.get_json(silent=True) or {}
    source_code = data.get("source_code", "")
    source_lang = data.get("source_lang", "")
    target_lang = data.get("target_lang", "")

    if not source_code or not source_lang or not target_lang:
        return jsonify({"error": "source_code, source_lang and target_lang are required"}), 400

    output_code = convert_code(source_code, source_lang, target_lang)
    analysis = analyze_code(source_code, output_code, source_lang, target_lang)
    return jsonify({
        "output_code": output_code,
        "suggestion": analysis.get("suggestion", ""),
        "solution": analysis.get("solution", "")
    })


@app.route("/api/assistant", methods=["POST"])
def api_assistant():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    question = data.get("question", "")

    if not code:
        return jsonify({"answer": "Please provide code to explain."}), 400

    answer = f"This code appears to be focused on: {question or 'understanding the conversion'}"
    if code.strip():
        answer += f"\n\nCode preview: {code[:200]}"
    return jsonify({"answer": answer})


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

    cursor.execute("SELECT users.id, profiles.name, profiles.email FROM users LEFT JOIN profiles ON users.id = profiles.user_id")
    users = cursor.fetchall()

    cursor.execute("""
        SELECT profiles.name, history.source_language, history.target_language, history.timestamp
        FROM history
        JOIN profiles ON history.user_id = profiles.user_id
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

    users = get_users_with_admin_status()

    return render_template("admin_users.html", users=users)


@app.route("/admin/make_admin/<int:user_id>")
def make_user_admin(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return "Access Denied ❌"
    
    make_admin(user_id)
    flash("User made admin successfully!", "success")
    return redirect("/admin/users")


@app.route("/admin/remove_admin/<int:user_id>")
def remove_user_admin(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return "Access Denied ❌"
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    flash("Admin privileges removed!", "success")
    return redirect("/admin/users")


@app.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return "Access Denied ❌"
    
    # Prevent deleting self or other admins
    if user_id == session["user_id"] or is_admin(user_id):
        flash("Cannot delete admin users!", "error")
        return redirect("/admin/users")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Cascade delete manually since SQLite schema didn't define ON DELETE CASCADE initially
        cursor.execute("DELETE FROM solutions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM suggestions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM feedback WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        flash("User deleted successfully, along with all associated data!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting user: {e}", "error")
        print(f"Delete Error: {e}")
    finally:
        conn.close()
    
    return redirect("/admin/users")


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
        SELECT profiles.name, history.source_language, history.target_language, history.timestamp,
               solutions.content, suggestions.content
        FROM history
        JOIN profiles ON history.user_id = profiles.user_id
        LEFT JOIN solutions ON history.id = solutions.history_id
        LEFT JOIN suggestions ON history.id = suggestions.history_id
        ORDER BY history.id DESC
    """)

    history = cursor.fetchall()
    conn.close()

    return render_template("admin_activity.html", history=history)


# 🧾 ADMIN SOLUTIONS
@app.route("/admin/solutions")
def admin_solutions():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied ❌"

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT solutions.id, profiles.name, history.source_language, history.target_language, solutions.content, solutions.timestamp
        FROM solutions
        JOIN history ON solutions.history_id = history.id
        JOIN profiles ON history.user_id = profiles.user_id
        ORDER BY solutions.id DESC
    """)
    solutions = cursor.fetchall()
    conn.close()

    return render_template("admin_solutions.html", solutions=solutions, active_page="admin_solutions")


# 📝 ADMIN SUGGESTIONS
@app.route("/admin/suggestions")
def admin_suggestions():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied ❌"

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT suggestions.id, profiles.name, history.source_language, history.target_language, suggestions.content, suggestions.timestamp
        FROM suggestions
        JOIN history ON suggestions.history_id = history.id
        JOIN profiles ON history.user_id = profiles.user_id
        ORDER BY suggestions.id DESC
    """)
    suggestions = cursor.fetchall()
    conn.close()

    return render_template("admin_suggestions.html", suggestions=suggestions, active_page="admin_suggestions")


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
    except Exception as e:
        flash(f"Error adding language: {e}", "error")

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


@app.route("/history/delete/<int:history_id>")
def history_delete(history_id):
    if "user_id" not in session:
        return redirect("/login")

    deleted = delete_history(history_id, session["user_id"])
    if not deleted:
        flash("Unable to delete this history entry.", "error")

    return redirect("/history")


@app.route("/clear")
def clear_history():
    if "user_id" not in session:
        return redirect("/login")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM solutions WHERE history_id IN (SELECT id FROM history WHERE user_id = ?)", (session["user_id"],))
    cursor.execute("DELETE FROM suggestions WHERE history_id IN (SELECT id FROM history WHERE user_id = ?)", (session["user_id"],))
    cursor.execute("DELETE FROM history WHERE user_id = ?", (session["user_id"],))
    conn.commit()
    conn.close()

    flash("All history cleared successfully.", "success")
    return redirect("/history")


# 📝 REGISTER WITH SAME PAGE OTP (FINAL FIXED)
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # 🔥 SEND OTP
        if "send_otp" in request.form:
            name = request.form["name"]
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]

            otp = str(random.randint(100000, 999999))

            session["temp_user"] = {
                "name": name,
                "username": username,
                "email": email,
                "password": generate_password_hash(password),
                "otp": otp
            }

            send_otp(email, otp)

            return render_template("register.html", otp_sent=True, name=name, username=username, email=email)

        # 🔥 VERIFY OTP
        elif "verify_otp" in request.form:
            user_otp = request.form["otp"]
            data = session.get("temp_user")

            if data and user_otp == data["otp"]:

                conn = connect_db()
                cursor = conn.cursor()

                try:
                    # Check if email or username already exists in users table
                    cursor.execute("SELECT 1 FROM users WHERE email = ? OR username = ?", (data["email"], data["username"]))
                    if cursor.fetchone():
                        conn.close()
                        return render_template("register.html", otp_sent=True, error="Email or username already exists ❌")

                    # Insert into users table with all required fields
                    cursor.execute("INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)", 
                                 (data["name"], data["username"], data["email"], data["password"]))
                    user_id = cursor.lastrowid
                    
                    # Insert into profiles table
                    cursor.execute("INSERT INTO profiles (user_id, name, username, email) VALUES (?, ?, ?, ?)",
                                 (user_id, data["name"], data["username"], data["email"]))

                    conn.commit()

                except Exception as e:
                    print(f"Registration error: {e}")
                    conn.rollback()
                    conn.close()
                    flash(f"Database error during registration. Please try again later.", "error")
                    return redirect("/register")

                finally:
                    conn.close()

                session.pop("temp_user", None)

                flash("✅ Registered Successfully! Please login with your credentials.", "success")
                return redirect("/login")

            else:
                return render_template("register.html", otp_sent=True, error="Invalid OTP ❌")

    return render_template("register.html", otp_sent=False)


# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        error = None

        if not username or not password:
            error = "Username and password are required"
        else:
            # Get user by username (joins users and profiles tables)
            user = get_profile_by_username(username)

            if user:
                # user[0] = user_id, user[1] = hashed_password, user[2] = name
                try:
                    if check_password_hash(user[1], password):
                        session["user_id"] = user[0]
                        session["user_name"] = user[2]
                        session["role"] = "admin" if is_admin(user[0]) else "user"
                        flash(f"Welcome back, {user[2]}! ✅", "success")
                        return redirect("/")
                    else:
                        error = "Invalid password"
                except Exception as e:
                    print(f"Password hash error: {e}")
                    error = "Authentication failed"
            else:
                error = "Username not found"
        
        return render_template("login.html", error=error)
    
    return render_template("login.html")


# � FORGOT PASSWORD
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        
        user = get_profile_by_email(email)
        
        if user:
            user_id = user[0]
            # Generate reset token (simple OTP for now)
            reset_token = str(random.randint(100000, 999999))
            
            session["reset_token"] = reset_token
            session["reset_user_id"] = user_id
            session["reset_email"] = email
            
            msg = f"Your password reset OTP is: {reset_token}"
            try:
                sender_email = os.getenv("SENDER_EMAIL")
                sender_password = os.getenv("SENDER_PASSWORD")
                
                if sender_email and sender_password:
                    mime_msg = MIMEText(msg)
                    mime_msg['Subject'] = "Password Reset OTP"
                    mime_msg['From'] = sender_email
                    mime_msg['To'] = email
                    
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(mime_msg)
                    server.quit()
                    
                    return render_template("forgot_password.html", otp_sent=True, email=email)
                else:
                    return "Email service not configured"
            except Exception as e:
                print(f"Email error: {e}")
                return "Failed to send email"
        else:
            return render_template("forgot_password.html", error="Email not found")

    return render_template("forgot_password.html", otp_sent=False)


@app.route("/reset-password", methods=["POST"])
def reset_password():
    otp = request.form["otp"]
    new_password = request.form["new_password"]
    
    if (session.get("reset_token") == otp and 
        "reset_user_id" in session):
        
        user_id = session["reset_user_id"]
        hashed_password = generate_password_hash(new_password)
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        conn.close()
        
        # Clear session
        session.pop("reset_token", None)
        session.pop("reset_user_id", None)
        session.pop("reset_email", None)
        
        flash("Password reset successfully! Please login.", "success")
        return redirect("/login")
    else:
        return render_template("forgot_password.html", otp_sent=True, error="Invalid OTP")


# �🚪 LOGOUT
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
        username = request.form["username"]
        email = request.form["email"]
        bio = request.form.get("bio", "").strip()
        phone = request.form.get("phone", "").strip()

        # Check if username is already taken by another profile
        cursor.execute("SELECT id FROM profiles WHERE username = ? AND user_id != ?", (username, session["user_id"]))
        if cursor.fetchone():
            profile = get_profile(session["user_id"])
            conn.close()
            return render_template("profile.html", user=profile, error="Username already taken", active_page="profile")

        update_profile(session["user_id"], name, username, email, bio, phone)
        session["user_name"] = name

    profile = get_profile(session["user_id"])
    conn.close()

    return render_template("profile.html", user=profile, active_page="profile")


# 💬 FEEDBACK
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        rating = int(request.form["rating"])
        message = request.form["message"]

        save_feedback(session["user_id"], name, email, rating, message)
        flash("Thank you for your feedback! ✅", "success")
        return redirect("/")

    return render_template("feedback.html", active_page="feedback")


# 👑 ADMIN FEEDBACK
@app.route("/admin/feedback")
def admin_feedback():
    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied ❌"

    feedbacks = get_all_feedback()
    return render_template("admin_feedback.html", feedbacks=feedbacks)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)