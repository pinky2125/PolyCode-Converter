#!/usr/bin/env python3
"""
Delete all users and admins from database for fresh start
"""
from database import connect_db

conn = connect_db()
cursor = conn.cursor()

try:
    print("\n" + "="*60)
    print("CLEANING DATABASE")
    print("="*60 + "\n")
    
    # Get count before deletion
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM profiles")
    profile_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM admins")
    admin_count = cursor.fetchone()[0]
    
    print(f"📊 BEFORE DELETION:")
    print(f"   Users: {user_count}")
    print(f"   Profiles: {profile_count}")
    print(f"   Admins: {admin_count}\n")
    
    # Delete data (KEEP TABLES)
    cursor.execute("DELETE FROM admins")
    print("✅ Deleted all admins")
    
    cursor.execute("DELETE FROM profiles")
    print("✅ Deleted all profiles")
    
    cursor.execute("DELETE FROM users")
    print("✅ Deleted all users")
    
    # Also clean up other tables with user references
    cursor.execute("DELETE FROM history")
    print("✅ Deleted all history")
    
    cursor.execute("DELETE FROM solutions")
    print("✅ Deleted all solutions")
    
    cursor.execute("DELETE FROM suggestions")
    print("✅ Deleted all suggestions")
    
    cursor.execute("DELETE FROM feedback")
    print("✅ Deleted all feedback")
    
    conn.commit()
    
    # Verify deletion
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM profiles")
    profile_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM admins")
    admin_count = cursor.fetchone()[0]
    
    print(f"\n📊 AFTER DELETION:")
    print(f"   Users: {user_count}")
    print(f"   Profiles: {profile_count}")
    print(f"   Admins: {admin_count}")
    
    print("\n" + "="*60)
    print("✅ DATABASE CLEANED - READY FOR FRESH REGISTRATION")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()

finally:
    conn.close()
