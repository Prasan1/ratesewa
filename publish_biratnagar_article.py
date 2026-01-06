#!/usr/bin/env python3
"""
Publish the Biratnagar pharmacy fraud article
"""

from app import app, db
from models import Article, ArticleCategory
from datetime import datetime

def publish_article():
    """Insert the Biratnagar pharmacy fraud article"""
    with app.app_context():
        print("Publishing Biratnagar pharmacy fraud article...")

        # Find or create the category (try Preventive Care or General Health)
        category = ArticleCategory.query.filter_by(name='Preventive Care').first()
        if not category:
            category = ArticleCategory.query.filter_by(name='General Health').first()
        if not category:
            # Create a category if none exists
            category = ArticleCategory(
                name='Patient Safety',
                slug='patient-safety',
                description='Articles about healthcare safety and patient rights'
            )
            db.session.add(category)
            db.session.commit()
            print(f"✓ Created new category: {category.name}")

        # Check if article already exists
        existing = Article.query.filter_by(
            title='Prescription Fraud Alert: Biratnagar Pharmacy Caught Manipulating Dosages - What Patients Must Know'
        ).first()

        if existing:
            print("⚠ Article already exists. Skipping.")
            return

        # Create the article
        article = Article(
            title='Prescription Fraud Alert: Biratnagar Pharmacy Caught Manipulating Dosages - What Patients Must Know',
            slug='biratnagar-pharmacy-fraud-prescription-safety',
            summary='A pharmacy at Nobel Medical College in Biratnagar was caught altering prescriptions, changing medication dosages that could endanger lives. Learn how to protect yourself and verify your prescriptions.',
            content='''<h2>Prescription Manipulation Scandal Rocks Biratnagar: What Patients Need to Know</h2>

<p class="lead">A pharmacy at Nobel Medical College in Biratnagar has been caught deliberately altering doctor prescriptions, changing medication dosages that could have endangered patient lives. The pharmacist responsible has fled the area after the fraud was discovered.</p>

<h3>What Happened?</h3>

<p>In a shocking breach of medical ethics and patient trust, a pharmacy operating at Nobel Medical College in Biratnagar was discovered systematically manipulating doctor-written prescriptions. The fraudulent practice involved altering dosage numbers on prescriptions:</p>

<ul>
    <li>Changing "8" tablets to "18" tablets</li>
    <li>Altering "7" doses to "9" doses</li>
    <li>Potentially other undiscovered modifications</li>
</ul>

<p>When confronted by patients and medical staff who noticed the discrepancies, the pharmacist closed the pharmacy and fled Biratnagar, leaving behind questions about how long this practice had been ongoing and how many patients were affected.</p>

<h3>Why This Is Extremely Dangerous</h3>

<p>Prescription manipulation isn't just about overcharging patients—it poses serious health risks:</p>

<p><strong>1. Overdosing Risk:</strong> Doubling medication dosages (like changing 8 to 18) can lead to drug toxicity, organ damage, or life-threatening reactions, especially with medications that have narrow therapeutic windows like blood thinners, diabetes medications, or heart medications.</p>

<p><strong>2. Treatment Failure:</strong> When patients take more medication than prescribed, they may run out before their next appointment, leading to gaps in treatment for chronic conditions like diabetes, hypertension, or infections.</p>

<p><strong>3. Financial Exploitation:</strong> Patients end up paying for medications they don't need, often at a time when they're already facing medical expenses.</p>

<p><strong>4. Loss of Medical Oversight:</strong> Doctors prescribe specific dosages based on patient condition, weight, age, and other medications. Altering these dosages bypasses critical medical judgment.</p>

<h3>A Growing Problem in Nepal's Healthcare System</h3>

<p>While this incident occurred in Biratnagar, it highlights broader concerns about healthcare transparency and accountability in Nepal. Patients place enormous trust in medical professionals—doctors, pharmacists, and healthcare institutions. When that trust is violated, it affects the entire healthcare ecosystem.</p>

<p>This case also raises questions about oversight mechanisms at private medical colleges and hospitals. How did this practice go undetected? Were there warning signs that were ignored? What systems need to be in place to prevent similar incidents?</p>

<h3>How to Protect Yourself: Essential Steps Every Patient Should Take</h3>

<p><strong>1. Always Verify Your Prescription</strong></p>
<ul>
    <li>Before leaving the doctor's office, clearly read the prescription and ask questions about dosages</li>
    <li>Take a photo of your original prescription on your phone</li>
    <li>When picking up medication, compare the quantity and dosage on the pharmacy bill with your original prescription</li>
</ul>

<p><strong>2. Count Your Medications</strong></p>
<ul>
    <li>Count tablets or check liquid volumes before leaving the pharmacy</li>
    <li>If something seems off, question it immediately</li>
    <li>Don't feel embarrassed—this is your health and your money</li>
</ul>

<p><strong>3. Use Trusted Pharmacies</strong></p>
<ul>
    <li>Stick to licensed, reputable pharmacies with established track records</li>
    <li>Hospital pharmacies are generally more accountable than standalone shops</li>
    <li>Ask your doctor for pharmacy recommendations</li>
</ul>

<p><strong>4. Know Your Rights</strong></p>
<ul>
    <li>You have the right to see the original prescription</li>
    <li>You can ask the pharmacist to explain any changes or substitutions</li>
    <li>You can refuse to purchase medications if something seems wrong</li>
    <li>You can report suspicious activity to the Nepal Pharmacy Council</li>
</ul>

<p><strong>5. Keep Records</strong></p>
<ul>
    <li>Save all prescriptions and pharmacy bills</li>
    <li>Keep a medication diary noting what you take and when</li>
    <li>Report any unusual side effects to your doctor immediately</li>
</ul>

<h3>What Should Happen Next?</h3>

<p>The Biratnagar incident demands immediate action from multiple parties:</p>

<p><strong>For Medical Institutions:</strong> Nobel Medical College must conduct a thorough internal investigation, compensate affected patients, and implement stronger pharmacy oversight systems. Their response to this crisis will define their credibility going forward.</p>

<p><strong>For Regulatory Bodies:</strong> The Nepal Medical Council and Nepal Pharmacy Council need to investigate not just this incident but whether similar practices exist elsewhere. Strengthening inspection protocols and implementing random audits could prevent future cases.</p>

<p><strong>For Patients:</strong> This incident should serve as a wake-up call. Blind trust in the healthcare system can be dangerous. Patient vigilance is not disrespectful—it's necessary self-protection.</p>

<h3>The Role of Healthcare Transparency</h3>

<p>Incidents like this underscore why platforms like RankSewa exist. Patients deserve to know:</p>
<ul>
    <li>Which doctors and healthcare facilities are trustworthy</li>
    <li>What other patients experienced during their visits</li>
    <li>Whether institutions respond professionally when problems arise</li>
    <li>Real wait times, costs, and treatment outcomes</li>
</ul>

<p>Transparency doesn't just protect individual patients—it raises standards across the entire healthcare system. When patients can share experiences and hold providers accountable, bad actors face consequences while good providers gain recognition.</p>

<h3>Moving Forward</h3>

<p>If you or someone you know may have been affected by the Biratnagar pharmacy fraud, take these steps:</p>

<ol>
    <li><strong>Review past prescriptions and pharmacy bills</strong> from this location for any discrepancies</li>
    <li><strong>Contact your prescribing doctor</strong> if you notice you have extra medication or ran out too quickly</li>
    <li><strong>Report the incident</strong> to the Nepal Pharmacy Council (www.nepalpharmacycouncil.org.np)</li>
    <li><strong>Get a medication review</strong> from your doctor to ensure you're taking correct dosages going forward</li>
    <li><strong>Share your experience</strong> to warn other patients and help authorities understand the scope of the problem</li>
</ol>

<h3>Your Voice Matters</h3>

<p>Healthcare in Nepal will only improve when patients speak up about problems and share both positive and negative experiences. Whether it's prescription fraud, excessive wait times, unprofessional behavior, or excellent care that deserves recognition—your review helps other patients make informed decisions.</p>

<p>The Biratnagar pharmacy incident is a reminder that healthcare quality isn't guaranteed by institutional names or fancy facilities. It's built on trust, accountability, and transparency—values that only thrive when patients stay informed and vigilant.</p>

<div class="alert alert-info mt-4">
    <strong>Have you visited Nobel Medical College or other hospitals in Biratnagar?</strong> Share your experience to help other patients make informed healthcare decisions. Your review could prevent someone else from encountering similar problems.
</div>''',
            category_id=category.id,
            meta_description='Biratnagar pharmacy fraud exposed: Learn how to protect yourself from prescription manipulation, verify medication dosages, and ensure healthcare safety in Nepal.',
            meta_keywords='pharmacy fraud Nepal, prescription safety, Biratnagar healthcare, Nobel Medical College, medication dosage, prescription manipulation, patient safety Nepal, pharmacy oversight',
            is_published=True,
            is_featured=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(article)
        db.session.commit()

        print(f"\n✅ Article published successfully!")
        print(f"   ID: {article.id}")
        print(f"   Title: {article.title}")
        print(f"   Category: {category.name}")
        print(f"   URL: /health-digest/{article.slug}")
        print(f"   Status: Published & Featured")
        print(f"\n📊 Article is now live and will appear on your homepage!")

if __name__ == '__main__':
    publish_article()
