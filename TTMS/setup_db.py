#!/usr/bin/env python
"""
Database setup script for TTMS
"""
import pymysql
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import config
from config import DB_CONFIG

# Read schema
schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
with open(schema_path, 'r') as f:
    schema = f.read()

# Try to connect using config
try:
    print(f"Connecting to MySQL as {DB_CONFIG['user']}@{DB_CONFIG['host']}...")
    connection = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    print("✓ Connected successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Execute schema
try:
    cursor = connection.cursor()
    
    # Drop existing database first
    try:
        cursor.execute("DROP DATABASE timetable_db4")
        print("✓ Dropped existing database")
    except:
        pass  # Database may not exist
    
    # Split and execute each statement
    statements = schema.split(';')
    count = 0
    for stmt in statements:
        stmt = stmt.strip()
        if stmt:
            cursor.execute(stmt)
            count += 1
            print(f"✓ Executed statement {count}")
    
    connection.commit()
    print(f"\n✅ Database setup completed successfully! ({count} statements executed)")
    
except Exception as e:
    print(f"\n❌ Error executing schema: {e}")
    connection.rollback()
    sys.exit(1)
finally:
    connection.close()
