#!/usr/bin/env python3
"""
Update the wait-time article with Quick Answer using raw SQL.
Usage: python update_wait_time_article.py
"""

import os

QUICK_ANSWER_HTML = """<strong>Normal wait times in Nepal:</strong>
<ul>
    <li><strong>With appointment:</strong> 30-45 minutes past scheduled time (average)</li>
    <li><strong>Walk-in:</strong> 60-90 minutes</li>
    <li><strong>Emergency:</strong> Immediate for life-threatening; 15-30 min for urgent</li>
</ul>
<p><strong>Red flag:</strong> If you're waiting 2+ hours with no explanation, that's excessive. Read below for your rights and tips to minimize wait times.</p>"""

def update_article():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    import psycopg2

    print("Connecting to database...")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE articles SET quick_answer = %s WHERE slug = %s",
            (QUICK_ANSWER_HTML.strip(), 'how-long-wait-doctor-nepal')
        )
        if cur.rowcount > 0:
            print("✅ Article updated with Quick Answer!")
        else:
            print("⚠️  Article 'how-long-wait-doctor-nepal' not found.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    update_article()
