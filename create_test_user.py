#!/usr/bin/env python3
"""
Create a test user for easy login testing
"""
from database import connect_db, create_profile
from werkzeug.security import generate_password_hash

def create_test_user():
    print("\n" + "="*60)
    print("CREATING TEST USER FOR LOGIN")
    print("="*60 + "\n")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Test user details
    test_username = "testuser"
    test_password = "Test@123456"  # Simple password for testing
    test_email = "test@polycode.local"
    test_name = "Test User"
    
    # Hash the password
    hashed_password = generate_password_hash(test_password)
    
    try:
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (test_username,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  Test user '{test_username}' already exists!")
        else:
            # Create user in users table (with all required fields)
            cursor.execute("INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)", 
                         (test_name, test_username, test_email, hashed_password))
            user_id = cursor.lastrowid
            
            # Create profile (duplicate of user info, but maintains schema)
            create_profile(user_id, test_name, test_username, test_email)
            
            conn.commit()
            
            print(f"✅ Test user created successfully!\n")
            print("="*60)
            print("LOGIN CREDENTIALS FOR TESTING:")
            print("="*60)
            print(f"👤 Username: {test_username}")
            print(f"🔑 Password: {test_password}")
            print("="*60 + "\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_user()
