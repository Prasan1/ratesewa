#!/usr/bin/env python3
"""
Update the wait-time article with a Quick Answer box to reduce bounce rate.
Run after migrating: flask db upgrade
"""

from app import app, db
from models import Article

QUICK_ANSWER_HTML = """
<strong>Normal wait times in Nepal:</strong>
<ul>
    <li><strong>With appointment:</strong> 30-45 minutes past scheduled time (average)</li>
    <li><strong>Walk-in:</strong> 60-90 minutes</li>
    <li><strong>Emergency:</strong> Immediate for life-threatening; 15-30 min for urgent</li>
</ul>
<p><strong>Red flag:</strong> If you're waiting 2+ hours with no explanation, that's excessive. Read below for your rights and tips to minimize wait times.</p>
"""

def update_article():
    """Add quick answer to the wait-time article"""
    with app.app_context():
        article = Article.query.filter_by(slug='how-long-wait-doctor-nepal').first()

        if not article:
            print("Article not found: how-long-wait-doctor-nepal")
            return False

        article.quick_answer = QUICK_ANSWER_HTML.strip()
        db.session.commit()

        print(f"Updated article: {article.title}")
        print(f"Quick answer added successfully!")
        return True

if __name__ == '__main__':
    update_article()
