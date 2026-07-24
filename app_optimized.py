"""
Optimized Flask Application with Security, Validation, and Logging
"""
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os
import threading
import smtplib
import random
import re
from email.mime.text import MIMEText
from dotenv import load_dotenv
from functools import wraps

# Import database and converter functions
from database_optimized import (
    create_tables, save_history, get_history, delete_history, get_db,
    get_languages, save_solution, save_suggestion, get_profile, update_profile
)
from engine.converter_optimized import convert_code
from engine.analyzer_optimized import analyze_code

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configurations
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV', 'development').lower() == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max request size

# Initialize database
create_tables()

# Constants
MAX_CODE_LENGTH = 1000000  # 1MB
OTP_VALIDITY = 300  # 5 minutes
INVALID_LOGIN_ATTEMPTS = 5


# ==================== INPUT VALIDATION ====================

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple:
    """
    Validate password strength
    
    Returns:
        (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain number"
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    return True, "Valid"


def validate_username(username: str) -> bool:
    """Validate username format"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None


def sanitize_input(text: str, max_length: int = 255) -> str:
    """Sanitize user input"""
    if not isinstance(text, str):
        return ""
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    # Remove potentially dangerous characters
    text = re.sub(r'[<>\"\'`]', '', text)
    return text


# ==================== SESSION & AUTH DECORATORS ====================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def check_session_timeout(f):
    """Decorator to check session timeout"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            import time
            current_time = time.time()
            last_activity = session.get('last_activity', current_time)
            
            # Session timeout: 1 hour
            if current_time - last_activity > 3600:
                session.clear()
                flash('Session expired. Please log in again', 'warning')
                return redirect('/login')
            
            session['last_activity'] = current_time
        
        return f(*args, **kwargs)
    return decorated_function


# ==================== EMAIL FUNCTIONS ====================

def send_otp(email: str, otp: str) -> bool:
    """
    Send OTP via email
    
    Args:
        email: Recipient email
        otp: One-time password
        
    Returns:
        True if sent successfully, False otherwise
    """
    def _send():
        try:
            sender_email = os.getenv("SENDER_EMAIL")
            sender_password = os.getenv("SENDER_PASSWORD")
            
            if not sender_email or not sender_password:
                logger.error("Missing email credentials")
                return False
            
            # Create email message
            msg = MIMEText(f"Your OTP for account verification is: {otp}")
            msg['Subject'] = "PolyCode Converter - OTP Verification"
            msg['From'] = sender_email
            msg['To'] = email
            
            # Send email
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            logger.info(f"OTP sent successfully to {email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("Email authentication failed")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    # Send email in background thread
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
    return True


# ==================== ROUTES ====================

# 🏠 HOME / DASHBOARD
@app.route("/", methods=["GET", "POST"])
@check_session_timeout
def home():
    """Home page with conversion feature"""
    output_code = ""
    solution = ""
    suggestion = ""
    languages = get_languages()
    
    if "user_id" in session:
        if request.method == "POST":
            try:
                # Get and validate form data
                source_code = request.form.get("source_code", "").strip()
                source_lang = request.form.get("source_lang", "").strip()
                target_lang = request.form.get("target_lang", "").strip()
                
                # Validate inputs
                if not source_code:
                    flash("Please enter source code", "warning")
                    return redirect("/")
                
                if len(source_code) > MAX_CODE_LENGTH:
                    flash(f"Code exceeds maximum length ({MAX_CODE_LENGTH} characters)", "danger")
                    return redirect("/")
                
                # Perform conversion
                logger.info(f"Converting from {source_lang} to {target_lang}")
                output_code = convert_code(source_code, source_lang, target_lang)
                
                # Get AI analysis
                analysis = analyze_code(source_code, output_code, source_lang, target_lang)
                solution = analysis.get("solution", "")
                suggestion = analysis.get("suggestion", "")
                
                # Save to history
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
                    logger.info(f"Conversion saved with history ID: {history_id}")
                
                flash("Code converted successfully!", "success")
                
            except ValueError as e:
                flash(f"Conversion error: {str(e)}", "danger")
                logger.error(f"Conversion error: {e}")
            except Exception as e:
                flash("An error occurred during conversion", "danger")
                logger.error(f"Unexpected error: {e}")
        
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


# 👤 PROFILE
@app.route("/profile", methods=["GET", "POST"])
@login_required
@check_session_timeout
def profile():
    """User profile page"""
    user_id = session.get("user_id")
    
    if request.method == "POST":
        try:
            name = sanitize_input(request.form.get("name", ""), 100)
            bio = sanitize_input(request.form.get("bio", ""), 500)
            phone = sanitize_input(request.form.get("phone", ""), 20)
            
            if not name:
                flash("Name is required", "warning")
                return redirect("/profile")
            
            # Update profile
            success = update_profile(user_id, name, bio, phone)
            if success:
                flash("Profile updated successfully!", "success")
                logger.info(f"Profile updated for user {user_id}")
            else:
                flash("Error updating profile", "danger")
            
            return redirect("/profile")
        
        except Exception as e:
            flash("An error occurred", "danger")
            logger.error(f"Profile update error: {e}")
            return redirect("/profile")
    
    profile_data = get_profile(user_id)
    return render_template("profile.html", profile=profile_data)


# 📚 HISTORY
@app.route("/history")
@login_required
@check_session_timeout
def history():
    """View conversion history"""
    user_id = session.get("user_id")
    history_data = get_history(user_id, limit=100)
    return render_template("history.html", records=history_data, active_page="history")


@app.route("/history/delete/<int:history_id>")
@login_required
def history_delete(history_id):
    user_id = session.get("user_id")
    deleted = delete_history(history_id, user_id)
    if not deleted:
        flash("Unable to delete this history entry.", "warning")
    return redirect("/history")


@app.route("/clear")
@login_required
def clear_history():
    user_id = session.get("user_id")
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM solutions WHERE history_id IN (SELECT id FROM history WHERE user_id = ?)", (user_id,))
            cursor.execute("DELETE FROM suggestions WHERE history_id IN (SELECT id FROM history WHERE user_id = ?)", (user_id,))
            cursor.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
            conn.commit()
        flash("All history cleared successfully.", "success")
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        flash("Unable to clear history.", "danger")
    return redirect("/history")


# 🚀 API ENDPOINT
@app.route("/api/convert", methods=["POST"])
@login_required
def api_convert():
    """API endpoint for code conversion"""
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
        
        source_code = data.get("source_code", "").strip()
        source_lang = data.get("source_lang", "").strip()
        target_lang = data.get("target_lang", "").strip()
        
        # Validate
        if not all([source_code, source_lang, target_lang]):
            return {"error": "Missing required fields"}, 400
        
        if len(source_code) > MAX_CODE_LENGTH:
            return {"error": "Code exceeds maximum length"}, 413
        
        # Convert
        result = convert_code(source_code, source_lang, target_lang)
        analysis = analyze_code(source_code, result, source_lang, target_lang)
        
        return {
            "success": True,
            "converted_code": result,
            "suggestion": analysis.get("suggestion"),
            "solution": analysis.get("solution")
        }, 200
    
    except ValueError as e:
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f"API conversion error: {e}")
        return {"error": "Internal server error"}, 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}")
    return render_template("500.html"), 500


@app.errorhandler(413)
def request_too_large(error):
    """Handle request too large"""
    logger.warning(f"413 error: Request too large")
    return {"error": "Request too large"}, 413


if __name__ == "__main__":
    app.run(debug=False)
