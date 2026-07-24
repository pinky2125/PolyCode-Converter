#!/usr/bin/env python3
"""
Check actual database schema
"""
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Get users table info
print("\n📊 USERS TABLE SCHEMA:")
print("="*60)
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]} (nullable={col[3]==0})")

# Get profiles table info
print("\n📊 PROFILES TABLE SCHEMA:")
print("="*60)
cursor.execute("PRAGMA table_info(profiles)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]} (nullable={col[3]==0})")

# Check actual users data
print("\n📊 USERS TABLE DATA:")
print("="*60)
cursor.execute("SELECT * FROM users LIMIT 3")
cols = [description[0] for description in cursor.description]
print("Columns:", cols)
rows = cursor.fetchall()
for row in rows:
    print(f"  {row}")

conn.close()
