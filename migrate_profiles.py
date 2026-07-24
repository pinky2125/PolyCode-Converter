#!/usr/bin/env python3
"""
Migration script: Create profiles for existing users
"""
from database import connect_db, create_profile
import sys

def migrate_users_to_profiles():
    print("\n" + "="*60)
    print("MIGRATING USERS TO PROFILES")
    print("="*60 + "\n")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Get all users without profiles
    cursor.execute("""
        SELECT id FROM users 
        WHERE id NOT IN (SELECT DISTINCT user_id FROM profiles)
    """)
    orphaned_users = cursor.fetchall()
    
    if not orphaned_users:
        print("✅ No orphaned users found. All users have profiles!")
        conn.close()
        return
    
    print(f"Found {len(orphaned_users)} users without profiles.\n")
    
    for user_id, in orphaned_users:
        print(f"Processing User ID: {user_id}...")
        
        # Generate default profile data
        username = f"user_{user_id}"
        name = f"User {user_id}"
        email = f"user{user_id}@polycode.local"
        
        try:
            create_profile(user_id, name, username, email)
            print(f"  ✅ Profile created: {username}")
        except Exception as e:
            print(f"  ❌ Error creating profile: {e}")
    
    conn.close()
    print("\n" + "="*60)
    print("✅ Migration complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    migrate_users_to_profiles()
