#!/usr/bin/env python3
"""
Remove debug text from Biratnagar pharmacy article
Removes: "Related Specialty: Dentistry Category: Oral Health Recommended doctor specialty: Dentist (ID 11 based on your production database)"
"""

from app import app, db, Article

def remove_debug_text():
    with app.app_context():
        # Find the Biratnagar article
        article = Article.query.filter(Article.slug.like('%biratnagar%pharmacy%')).first()

        if not article:
            article = Article.query.filter(Article.title.like('%Biratnagar%Pharmacy%')).first()

        if not article:
            print("❌ Article not found!")
            return

        print(f"Found article: {article.title}")
        print(f"Article ID: {article.id}")
        print(f"Related specialty ID: {article.related_specialty_id}")

        # Remove debug text patterns
        debug_patterns = [
            "Related Specialty:",
            "Category: Oral Health",
            "Recommended doctor specialty:",
            "(ID 11 based on your production database)",
            "based on your production database"
        ]

        original_content = article.content
        updated_content = original_content

        # Try to find and remove the debug paragraph
        import re
        # Pattern to match the entire debug line
        debug_line_pattern = r'Related Specialty:.*?production database\)'
        updated_content = re.sub(debug_line_pattern, '', updated_content, flags=re.DOTALL)

        # Also try simpler patterns
        for pattern in debug_patterns:
            updated_content = updated_content.replace(pattern, '')

        # Clean up extra whitespace that might be left
        updated_content = re.sub(r'\n\n\n+', '\n\n', updated_content)
        updated_content = updated_content.strip()

        if original_content != updated_content:
            article.content = updated_content
            db.session.commit()
            print(f"✅ Debug text removed successfully!")
            print(f"   Removed {len(original_content) - len(updated_content)} characters")
        else:
            print("ℹ️  No debug text found to remove")
            print("\nShowing last 300 chars of content:")
            print(article.content[-300:])

if __name__ == '__main__':
    remove_debug_text()
