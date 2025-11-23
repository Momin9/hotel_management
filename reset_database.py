#!/usr/bin/env python3
import os
import django
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

def reset_database():
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'port': '5432',
        'user': 'momin-ali',
        'password': '123'
    }
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(database='postgres', **db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Terminate existing connections
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = 'hotel_software' AND pid <> pg_backend_pid()
        """)
        
        # Drop and recreate database
        cursor.execute("DROP DATABASE IF EXISTS hotel_software")
        cursor.execute("CREATE DATABASE hotel_software")
        
        print("Database reset successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()