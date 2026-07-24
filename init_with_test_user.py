#!/usr/bin/env python3
"""
Initialize database and create test user
"""
from database import create_tables, connect_db
from werkzeug.security import generate_password_hash

print("\n" + "="*60)
print("INITIALIZING DATABASE WITH TEST USER")
print("="*60 + "\n")

# Create tables
print("📊 Creating database tables...")
create_tables()

import time
time.sleep(1)  # Wait for tables to be created

conn = connect_db()
cursor = conn.cursor()

# Test user details
test_username = "testuser"
test_password = "Test@123456"
test_email = "test@polycode.local"
test_name = "Test User"

# Hash the password
hashed_password = generate_password_hash(test_password)

try:
    # Create test user in users table
    print("👤 Creating test user...")
    cursor.execute("INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)", 
                 (test_name, test_username, test_email, hashed_password))
    user_id = cursor.lastrowid
    
    # Create profile for test user (directly, without calling create_profile function)
    print("📋 Creating profile...")
    cursor.execute("""
        INSERT INTO profiles (user_id, name, username, email)
        VALUES (?, ?, ?, ?)
    """, (user_id, test_name, test_username, test_email))
    
    conn.commit()
    conn.close()
    
    print("\n✅ SUCCESS!\n")
    print("="*60)
    print("LOGIN CREDENTIALS FOR TESTING:")
    print("="*60)
    print(f"👤 Username: {test_username}")
    print(f"🔑 Password: {test_password}")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    conn.close()
