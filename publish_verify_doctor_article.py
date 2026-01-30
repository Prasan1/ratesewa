#!/usr/bin/env python3
"""
Script to publish article: Why Verifying Your Doctor's Credentials Matters in Nepal
"""

from app import app, db, Article, ArticleCategory
from datetime import datetime

ARTICLE_CONTENT = '''
## The Reality of Medical Licensing in Nepal

Choosing a doctor is one of the most important healthcare decisions you'll make. But how do you know if your doctor is actually qualified to practice medicine in Nepal?

Recent data from the Nepal Medical Council (NMC) reveals a concerning reality: **nearly 60% of medical graduates fail the licensing examination**.

In the 74th Medical License Examination, only 372 out of 943 candidates passed—a pass rate of just 39.45%. For MBBS graduates, only 300 out of 775 candidates (38.7%) passed. For BDS (dental) graduates, 72 out of 168 (42.85%) passed.

This means that **having an MBBS or BDS degree does not automatically make someone a licensed doctor** in Nepal. Without passing the NMC examination, they cannot legally practice medicine.

## When Even Licensed Doctors Break Trust

Unfortunately, having an NMC license doesn't guarantee ethical behavior. In a recent case that shocked the medical community, Dr. Yashoda Rijal, a senior doctor at Kharanitar Hospital in Nuwakot, was suspended by the Nepal Medical Council for two months.

Her offense? **Creating fraudulent hospital records** to help her father in a legal case. The Kathmandu District Court convicted her in July 2025 after investigators discovered that "the same person appeared in both court and hospital records on the same day."

This case reminds us that credentials alone don't ensure trustworthiness.

## How to Verify Your Doctor

### Step 1: Check NMC Registration

Every licensed doctor in Nepal has an NMC registration number. You can verify this on the [Nepal Medical Council website](https://nmc.org.np/).

**What to look for:**
- Valid NMC registration number
- Registration status (active, suspended, or revoked)
- Specialization matches their practice

### Step 2: Look for Verified Profiles

Platforms like RankSewa verify doctors through multiple checks:
- NMC registration verification
- Identity document verification
- Practice location confirmation

A "Verified" badge means the doctor has completed these verification steps.

### Step 3: Read Patient Reviews

Real patient experiences reveal what credentials cannot:
- Communication style
- Wait times and availability
- Treatment outcomes
- Overall trustworthiness

## Red Flags to Watch For

Be cautious if a doctor:
- Cannot provide their NMC registration number
- Avoids questions about their qualifications
- Has no verifiable online presence
- Practices in unlicensed or unregistered facilities

## Why This Matters

With 60% of medical graduates unable to pass licensing exams, and even some licensed doctors facing disciplinary actions, **verification is not optional—it's essential** for your safety.

At RankSewa, every doctor profile is verified against NMC records. We believe patients deserve to know their doctor is qualified, licensed, and in good standing.

---

**Find Verified Doctors:** [Search on RankSewa](https://ranksewa.com)

*Your health is too important to leave to chance. Always verify.*

---

## Disclaimer

This article is for informational purposes only. RankSewa is not affiliated with the Nepal Medical Council. Always verify credentials independently through official NMC channels. If you suspect illegal medical practice, report to NMC or relevant authorities.

---

**About RankSewa:** We're Nepal's first patient-driven doctor directory where you can find, compare, and review doctors based on real experiences. Our mission is to bring transparency to healthcare in Nepal.
'''

QUICK_ANSWER = '''
<strong>Key Facts:</strong>
<ul>
<li>60% of medical graduates in Nepal fail the NMC licensing exam</li>
<li>An MBBS/BDS degree alone doesn't authorize someone to practice</li>
<li>Even licensed doctors can face suspension for misconduct</li>
<li>Always verify your doctor's NMC registration status before treatment</li>
</ul>
'''

def publish_article():
    with app.app_context():
        # Get or create category
        category = ArticleCategory.query.filter_by(name='Healthcare Tips').first()
        if not category:
            category = ArticleCategory(
                name='Healthcare Tips',
                slug='healthcare-tips',
                description='Practical health and healthcare guidance',
                display_order=2
            )
            db.session.add(category)
            db.session.commit()
            print(f"Created category: Healthcare Tips")

        slug = 'why-verify-doctor-credentials-nepal'

        # Check if article already exists
        existing = Article.query.filter_by(slug=slug).first()
        if existing:
            print(f"Article already exists (ID: {existing.id}). Updating...")
            existing.content = ARTICLE_CONTENT
            existing.quick_answer = QUICK_ANSWER
            existing.updated_at = datetime.utcnow()
            db.session.commit()
            print(f"Article updated!")
            print(f"URL: /health-digest/{existing.slug}")
            return

        # Create new article
        article = Article(
            title="Why Verifying Your Doctor's Credentials Matters in Nepal",
            slug=slug,
            category_id=category.id,
            summary="60% of medical graduates fail Nepal's licensing exam, and even licensed doctors face disciplinary actions. Learn why verifying your doctor's NMC credentials is essential for your safety.",
            content=ARTICLE_CONTENT,
            quick_answer=QUICK_ANSWER,
            meta_description="60% of medical graduates fail Nepal's NMC exam. Learn why verifying doctor credentials matters and how to check if your doctor is licensed.",
            meta_keywords="verify doctor nepal, nmc exam pass rate, doctor credentials nepal, medical license nepal, nmc registration check, doctor verification, healthcare nepal",
            author_name="RankSewa Health Team",
            related_specialty_id=None,
            is_published=True,
            is_featured=False,
            published_at=datetime.utcnow(),
            featured_image=None
        )

        db.session.add(article)
        db.session.commit()

        print("Article published successfully!")
        print(f"   ID: {article.id}")
        print(f"   Title: {article.title}")
        print(f"   Slug: {article.slug}")
        print(f"   URL: /health-digest/{article.slug}")
        print(f"   Published: {article.is_published}")

if __name__ == '__main__':
    publish_article()
