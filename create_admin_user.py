#!/usr/bin/env python3
"""
Create admin user for admin panel access
"""
from database import connect_db
from werkzeug.security import generate_password_hash

print("\n" + "="*60)
print("CREATING ADMIN USER")
print("="*60 + "\n")

# Admin credentials
admin_name = "Admin"
admin_username = "admin"
admin_email = "admin@polycode.com"
admin_password = "Admin@123456"

hashed_password = generate_password_hash(admin_password)

conn = connect_db()
cursor = conn.cursor()

try:
    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
    existing = cursor.fetchone()
    
    if existing:
        admin_id = existing[0]
        print(f"⚠️  Admin user '{admin_username}' already exists with ID: {admin_id}")
        
        # Check if already in admins table
        cursor.execute("SELECT id FROM admins WHERE user_id = ?", (admin_id,))
        if cursor.fetchone():
            print("✅ Already marked as admin")
        else:
            print("Adding to admins table...")
            cursor.execute("INSERT INTO admins (user_id) VALUES (?)", (admin_id,))
            conn.commit()
            print("✅ Added to admins table")
    else:
        print("Creating new admin user...")
        
        # Insert into users table
        cursor.execute(
            "INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)",
            (admin_name, admin_username, admin_email, hashed_password)
        )
        admin_id = cursor.lastrowid
        
        # Insert into profiles table
        cursor.execute(
            "INSERT INTO profiles (user_id, name, username, email) VALUES (?, ?, ?, ?)",
            (admin_id, admin_name, admin_username, admin_email)
        )
        
        # Insert into admins table
        cursor.execute("INSERT INTO admins (user_id) VALUES (?)", (admin_id,))
        
        conn.commit()
        
        print(f"✅ Admin user created with ID: {admin_id}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("ADMIN LOGIN CREDENTIALS:")
    print("="*60)
    print(f"👤 Username: {admin_username}")
    print(f"🔑 Password: {admin_password}")
    print("="*60 + "\n")
    print("✅ Now you can login with these credentials")
    print("✅ After login, go to /admin to access admin panel\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    conn.close()
