#!/usr/bin/env python3
"""
Diagnostic script to check login issue
"""
from database import connect_db
from werkzeug.security import check_password_hash
import sys

def check_database():
    print("\n" + "="*60)
    print("CHECKING DATABASE FOR LOGIN ISSUES")
    print("="*60 + "\n")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Check users table
    print("📊 USERS TABLE:")
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"  Total users: {user_count}")
    if user_count > 0:
        cursor.execute("SELECT id, password FROM users LIMIT 5")
        for row in cursor.fetchall():
            print(f"    - User ID: {row[0]}, Password Hash: {row[1][:20]}...")
    
    # Check profiles table
    print("\n📊 PROFILES TABLE:")
    cursor.execute("SELECT COUNT(*) FROM profiles")
    profile_count = cursor.fetchone()[0]
    print(f"  Total profiles: {profile_count}")
    if profile_count > 0:
        cursor.execute("SELECT user_id, username, name, email FROM profiles LIMIT 5")
        for row in cursor.fetchall():
            print(f"    - User ID: {row[0]}, Username: {row[1]}, Name: {row[2]}, Email: {row[3]}")
    
    # Check JOIN
    print("\n🔗 CHECKING JOIN (users + profiles):")
    cursor.execute("""
        SELECT users.id, users.password, profiles.name, profiles.username, profiles.email 
        FROM users 
        JOIN profiles ON users.id = profiles.user_id 
        LIMIT 5
    """)
    join_results = cursor.fetchall()
    if join_results:
        print(f"  JOIN returned {len(join_results)} records:")
        for row in join_results:
            print(f"    - ID: {row[0]}, Username: {row[3]}, Name: {row[2]}")
    else:
        print("  ❌ JOIN returned no results!")
    
    # Check for orphaned records
    print("\n⚠️  CHECKING FOR ORPHANED RECORDS:")
    cursor.execute("""
        SELECT id FROM users 
        WHERE id NOT IN (SELECT DISTINCT user_id FROM profiles)
    """)
    orphaned = cursor.fetchall()
    if orphaned:
        print(f"  ❌ Found {len(orphaned)} users without profiles:")
        for row in orphaned:
            print(f"    - User ID: {row[0]}")
    else:
        print("  ✅ No orphaned users found")
    
    # Test login with first user
    print("\n🧪 TESTING LOGIN WITH FIRST USER:")
    cursor.execute("""
        SELECT users.id, users.password, profiles.username, profiles.name 
        FROM users 
        JOIN profiles ON users.id = profiles.user_id 
        LIMIT 1
    """)
    test_user = cursor.fetchone()
    if test_user:
        print(f"  Found test user: {test_user[2]}")
        print(f"  User ID: {test_user[0]}")
        print(f"  Password Hash: {test_user[1][:30]}...")
        print(f"  To test login, try password you used during registration")
    
    conn.close()
    print("\n" + "="*60)
    print("Diagnostic check complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    check_database()
