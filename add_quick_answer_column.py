#!/usr/bin/env python3
"""
Add quick_answer column using raw database connection.
Usage: python add_quick_answer_column.py
"""

import os

def add_column():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return

    # Handle postgres:// vs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    import psycopg2

    print("Connecting to database...")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        # Check if column exists
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'articles' AND column_name = 'quick_answer'
        """)
        if cur.fetchone():
            print("✅ Column 'quick_answer' already exists.")
        else:
            print("Adding 'quick_answer' column...")
            cur.execute("ALTER TABLE articles ADD COLUMN quick_answer TEXT")
            print("✅ Column added successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    add_column()
