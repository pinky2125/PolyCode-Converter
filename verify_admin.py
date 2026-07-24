#!/usr/bin/env python3
"""
Verify admin user creation
"""
from database import connect_db

conn = connect_db()
cursor = conn.cursor()

print("\n" + "="*60)
print("VERIFYING ADMIN USER SETUP")
print("="*60 + "\n")

# Check users table
print("📊 USERS TABLE:")
cursor.execute("SELECT id, name, username, email FROM users WHERE username = 'admin'")
user = cursor.fetchone()
if user:
    print(f"  ✅ Found user: ID={user[0]}, Name={user[1]}, Username={user[2]}, Email={user[3]}")
else:
    print("  ❌ Admin user NOT found in users table")

# Check profiles table
print("\n📊 PROFILES TABLE:")
cursor.execute("SELECT id, user_id, name, username FROM profiles WHERE username = 'admin'")
profile = cursor.fetchone()
if profile:
    print(f"  ✅ Found profile: ID={profile[0]}, UserID={profile[1]}, Name={profile[2]}, Username={profile[3]}")
else:
    print("  ❌ Admin profile NOT found in profiles table")

# Check admins table
print("\n📊 ADMINS TABLE:")
cursor.execute("SELECT id, user_id FROM admins WHERE user_id = ?", (user[0] if user else 0,))
admin = cursor.fetchone()
if admin:
    print(f"  ✅ Found admin: ID={admin[0]}, UserID={admin[1]}")
else:
    print("  ❌ Admin NOT found in admins table")

# Show all data for reference
print("\n📋 COMPLETE DATA SUMMARY:")
print("="*60)
cursor.execute("SELECT id, username, email FROM users")
all_users = cursor.fetchall()
print(f"\nTotal Users: {len(all_users)}")
for user in all_users:
    cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user[0],))
    is_admin = "👑 ADMIN" if cursor.fetchone() else "👤 USER"
    print(f"  {is_admin}: {user[1]} ({user[2]})")

conn.close()

print("\n" + "="*60)
print("✅ VERIFICATION COMPLETE - READY FOR LOGIN")
print("="*60 + "\n")
