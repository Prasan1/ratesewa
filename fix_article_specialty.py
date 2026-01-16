"""
Fix the General Health Checkup article to link to Internal Medicine specialty.
Run this on production: python fix_article_specialty.py
"""
from app import app, db


def fix_article():
    with app.app_context():
        # Use raw SQL with correct table names: articles, specialties

        # First, find the Internal Medicine specialty ID
        result = db.session.execute(
            db.text("SELECT id, name FROM specialties WHERE name = 'Internal Medicine'")
        ).fetchone()

        if not result:
            print("ERROR: 'Internal Medicine' specialty not found!")
            print("\nAvailable specialties:")
            all_specs = db.session.execute(
                db.text("SELECT id, name FROM specialties ORDER BY id")
            ).fetchall()
            for s in all_specs:
                print(f"  - ID {s[0]}: {s[1]}")
            return

        specialty_id = result[0]
        print(f"Found Internal Medicine specialty with ID: {specialty_id}")

        # Find the article
        article = db.session.execute(
            db.text("SELECT id, title, slug, related_specialty_id FROM articles WHERE slug = 'when-to-see-a-doctor-in-nepal-a-guide-to-general-health-checkups'")
        ).fetchone()

        if not article:
            print("ERROR: Article not found!")
            print("\nSearching for similar articles...")
            similar = db.session.execute(
                db.text("SELECT id, title, slug FROM articles WHERE title LIKE '%health%' OR title LIKE '%checkup%'")
            ).fetchall()
            for a in similar:
                print(f"  - ID {a[0]}: {a[1]} (slug: {a[2]})")
            return

        print(f"Found article: {article[1]}")
        print(f"Current related_specialty_id: {article[3]}")

        # Update the article
        db.session.execute(
            db.text("UPDATE articles SET related_specialty_id = :spec_id WHERE slug = 'when-to-see-a-doctor-in-nepal-a-guide-to-general-health-checkups'"),
            {"spec_id": specialty_id}
        )
        db.session.commit()

        print(f"SUCCESS! Updated related_specialty_id to: {specialty_id}")
        print("The article will now recommend Internal Medicine doctors.")


if __name__ == "__main__":
    fix_article()
