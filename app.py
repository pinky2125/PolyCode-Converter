from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_tables, save_history, get_history, connect_db
from engine.converter import convert_code

app = Flask(__name__)
app.secret_key = "supersecretkey"

create_tables()

@app.route("/", methods=["GET", "POST"])
def home():

    output_code = ""

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
            logged_in=True
        )

    else:
        return render_template(
            "index.html",
            active_page="dashboard",
            logged_in=False
        )

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

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, hashed_password))
            conn.commit()
            return redirect("/login")

        except:
            return "Email already exists"

        finally:
            conn.close()

    return render_template("register.html")


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
            return redirect("/")
        else:
            return "Invalid email or password"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route("/clear")
def clear_history():

    if "user_id" not in session:
        return redirect("/login")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM history WHERE user_id = ?",
        (session["user_id"],)
    )

    conn.commit()
    conn.close()

    return redirect("/history")

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = connect_db()
    cursor = conn.cursor()

    # ✅ UPDATE PROFILE
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE users
            SET name = ?, email = ?
            WHERE id = ?
        """, (name, email, session["user_id"]))

        conn.commit()

        # session name bhi update karo (important)
        session["user_name"] = name

    # ✅ GET UPDATED DATA
    cursor.execute(
        "SELECT name, email FROM users WHERE id = ?",
        (session["user_id"],)
    )

    user = cursor.fetchone()
    conn.close()

    return render_template("profile.html", user=user, active_page="profile")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)