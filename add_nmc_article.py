#!/usr/bin/env python3
"""
Script to add NMC verification article to database
"""

from app import app, db, Article, ArticleCategory
from datetime import datetime

ARTICLE_CONTENT = '''# How to Verify Your Doctor's NMC Number Online: A Complete Guide for Patients

**Last updated:** January 9, 2026

---

Every patient in Nepal deserves to know their doctor's credentials are legitimate. With over 28,000 registered doctors in Nepal, how can you be sure your doctor is who they claim to be?

The answer is simple: **verify their Nepal Medical Council (NMC) registration number**.

In this complete guide, we'll show you exactly how to verify your doctor's NMC number online, what to look for, and red flags that should concern you.

## Why NMC Verification Matters

The Nepal Medical Council is the only legal body authorized to register medical practitioners in Nepal. Every qualified doctor practicing in Nepal must have a valid NMC registration number.

### What NMC Verification Tells You:

- The doctor has a legitimate medical degree
- They are legally authorized to practice medicine in Nepal
- Their credentials have been verified by the NMC
- They haven't been suspended or struck off the medical register

**Important:** An NMC number doesn't guarantee a doctor is experienced or skilled—it only confirms they're legally qualified to practice. For insights on quality of care, patient reviews are invaluable.

## How to Verify NMC Numbers Online

### Method 1: Official NMC Website (Most Reliable)

1. **Visit the NMC website:** [nmc.org.np](https://www.nmc.org.np)
2. **Navigate to the "Registered Doctors" or "Verification" section**
3. **Search by:**
   - Doctor's name
   - NMC registration number
   - Qualification details

**What You'll Find:**
- Full name
- NMC registration number
- Registration date
- Qualifications
- Specialization (if applicable)

### Method 2: RankSewa Verification (Quick Check)

On RankSewa, we display NMC numbers for verified doctors on their profiles:

1. **Search for your doctor** at [ranksewa.com](https://ranksewa.com)
2. **Look for the Verified badge** and NMC number on their profile
3. **Cross-check with NMC website** if you want to double-verify

**Note:** A "Verified" badge on RankSewa means we've checked the doctor's NMC registration, but we always recommend patients verify independently as well.

### Method 3: Ask Your Doctor Directly

Don't be shy—it's your right to ask:

> "May I see your NMC registration certificate?"

**Every doctor in Nepal should:**
- Display their NMC certificate in their clinic
- Provide their NMC number on request
- Be completely transparent about their credentials

If a doctor is evasive or refuses to share their NMC number, that's a **major red flag**.

## Understanding NMC Registration Numbers

NMC numbers follow a specific format:

**Example:** `NMC-12345`

- The number indicates when the doctor was registered
- Lower numbers = registered earlier (more experience, potentially)
- Higher numbers = more recently registered

**Important:** Registration date does not equal years of experience. A doctor may have practiced abroad before registering with NMC.

## What If You Can't Find an NMC Number?

If you search for your doctor and can't find their NMC registration, there are several possible reasons:

### 1. Name Mismatch
Try searching with:
- Full formal name (not nickname)
- Without title (search "Ram Sharma" not "Dr. Ram Sharma")
- Alternative spellings

### 2. Recently Registered
New registrations may take time to appear in online databases.

### 3. Practicing Without Registration
This is the red flag scenario. If a doctor claims to be qualified but has no NMC record after thorough searching, **they may be practicing illegally**.

## Red Flags: When to Be Concerned

### Major Red Flags:
1. **No NMC certificate displayed** in clinic
2. **Refuses to provide NMC number** when asked
3. **NMC number doesn't match** their name in the database
4. **Claims specialization** not listed in NMC records
5. **Suspended or struck off** from NMC register

### What to Do If You Find a Red Flag:

1. **Don't panic** but be cautious
2. **Ask for clarification** from the doctor
3. **Seek a second opinion** from a verified doctor
4. **Report to NMC** if you suspect illegal practice

You can also file a complaint through the NMC website's formal channels.

## Verifying Specialists: Extra Steps

If your doctor claims to be a specialist (cardiologist, neurologist, etc.), verify:

### 1. Basic Medical Degree
- MBBS or equivalent
- Registered with NMC

### 2. Specialist Qualification
- MD, MS, or equivalent in their specialty
- Listed in NMC records under "Specialization"

**Example:** A cardiologist should have:
- MBBS + NMC registration
- MD (Medicine) or DM (Cardiology) or equivalent
- Specialization listed as "Cardiology" in NMC records

**Warning:** Some doctors may have general MBBS degrees but practice in specialized fields after short courses. This is legal but important to know when choosing a specialist.

## Common Questions About NMC Verification

### Q: Can doctors practice in Nepal without an NMC number?
**A:** No. It's illegal to practice medicine in Nepal without NMC registration. Even foreign doctors must register with NMC to practice legally.

### Q: Are dentists registered with NMC?
**A:** Yes. Dentists (BDS) are also registered with the Nepal Medical Council.

### Q: What about Ayurvedic doctors?
**A:** Ayurvedic practitioners are registered with the Nepal Ayurved Medical Council (NAMC), not NMC. BAMS doctors have a separate registry.

### Q: How often do doctors need to renew NMC registration?
**A:** NMC registration requires periodic renewal. Doctors must maintain active registration to practice legally.

### Q: Can I trust a doctor without an NMC number?
**A:** No. If someone is practicing as a medical doctor in Nepal without NMC registration, they're breaking the law. Seek care from registered doctors only.

## Beyond Verification: Choosing the Right Doctor

NMC verification confirms credentials, but choosing the right doctor involves more:

### Consider:
1. **Experience:** Years in practice, case volume
2. **Patient Reviews:** Read experiences from other patients
3. **Communication Style:** Do they listen? Explain clearly?
4. **Accessibility:** Appointment availability, location
5. **Hospital Affiliations:** Which hospitals do they work with?

**Pro Tip:** On RankSewa, you can filter by verified doctors AND read real patient reviews to make informed decisions.

## Why We Verify Doctors on RankSewa

At RankSewa, we believe patients deserve transparency:

- We verify NMC numbers for registered doctors
- We display "Verified" badges on confirmed profiles
- We show NMC numbers publicly when available
- We encourage patients to independently verify as well

**Our mission:** Help patients choose doctors with confidence, backed by facts and real experiences.

## Take Action: Verify Your Doctor Today

### Quick Checklist:
- Find your doctor's NMC number (ask or check their certificate)
- Verify on NMC website
- Check if specialization matches their claim
- Look for patient reviews on RankSewa
- Feel confident in your choice!

## Found This Helpful?

**Share your experience:**
- Have you verified your doctor's NMC number before?
- Did you discover any surprises?
- Share this guide to help other patients make informed choices.

---

## Find Verified Doctors Near You

Search for NMC-verified doctors in your city on RankSewa:

- [Find Doctors in Kathmandu](https://ranksewa.com?city=kathmandu)
- [Find Doctors in Pokhara](https://ranksewa.com?city=pokhara)
- [Find Doctors in Lalitpur](https://ranksewa.com?city=lalitpur)
- [Find Doctors in Biratnagar](https://ranksewa.com?city=biratnagar)
- [Search All Cities](https://ranksewa.com)

**Already seen a doctor?** [Leave a review](https://ranksewa.com) to help other patients.

---

## Disclaimer

This article is for informational purposes only. RankSewa is not affiliated with the Nepal Medical Council. Always verify credentials independently through official NMC channels. If you suspect illegal medical practice, report to NMC or relevant authorities.

---

**About RankSewa:** We're Nepal's first patient-driven doctor directory where you can find, compare, and review doctors based on real experiences. Our mission is to bring transparency to healthcare in Nepal.

*Have questions or concerns? Contact us or visit [ranksewa.com](https://ranksewa.com) to learn more.*
'''

def add_nmc_article():
    with app.app_context():
        content = ARTICLE_CONTENT

        # Get or create category
        category = ArticleCategory.query.filter_by(name='Healthcare Tips').first()
        if not category:
            # Create category if it doesn't exist
            category = ArticleCategory(
                name='Healthcare Tips',
                slug='healthcare-tips',
                description='Practical health and healthcare guidance',
                display_order=2
            )
            db.session.add(category)
            db.session.commit()

        # Check if article already exists
        existing = Article.query.filter_by(slug='verify-doctor-nmc-number-online').first()
        if existing:
            print(f"Article already exists (ID: {existing.id}). Updating instead...")
            existing.content = content
            existing.summary = "Learn how to verify your doctor's Nepal Medical Council (NMC) registration number online. Complete guide with step-by-step instructions to check doctor credentials and avoid unregistered practitioners."
            existing.meta_description = "Learn how to verify your doctor's NMC number online. Step-by-step guide to check credentials and spot red flags."
            existing.meta_keywords = "verify doctor nmc nepal, check doctor credentials nepal, nmc number lookup, nmc registration verification, verify medical license nepal, doctor verification nepal, nmc database search"
            existing.updated_at = datetime.utcnow()
            db.session.commit()
            print(f"Article updated successfully!")
            print(f"URL: /health-digest/{existing.slug}")
            return

        # Create new article
        article = Article(
            title="How to Verify Your Doctor's NMC Number Online: A Complete Guide for Patients",
            slug="verify-doctor-nmc-number-online",
            category_id=category.id,
            summary="Learn how to verify your doctor's Nepal Medical Council (NMC) registration number online. Complete guide with step-by-step instructions to check doctor credentials and avoid unregistered practitioners.",
            content=content,
            meta_description="Learn how to verify your doctor's NMC number online. Step-by-step guide to check credentials and spot red flags.",
            meta_keywords="verify doctor nmc nepal, check doctor credentials nepal, nmc number lookup, nmc registration verification, verify medical license nepal, doctor verification nepal, nmc database search",
            related_specialty_id=None,  # General article, not specialty-specific
            is_published=True,  # Publish immediately
            is_featured=True,  # Feature this article
            published_at=datetime.utcnow(),
            featured_image=None  # Can add image later via admin panel
        )

        db.session.add(article)
        db.session.commit()

        print("NMC verification article created successfully!")
        print(f"   ID: {article.id}")
        print(f"   Slug: {article.slug}")
        print(f"   URL: /health-digest/{article.slug}")
        print(f"   Published: {article.is_published}")
        print(f"   Featured: {article.is_featured}")
        print()
        print("View it at: http://localhost:5000/health-digest/verify-doctor-nmc-number-online")

if __name__ == '__main__':
    add_nmc_article()
