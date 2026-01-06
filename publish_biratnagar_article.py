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
            summary='A pharmacy in Biratnagar was caught changing prescriptions—turning "1 tablet" into "15" or "18" to defraud patients. GM Dipesh Rai confirms Nobel Medical College is moving to digital prescriptions. Learn how to protect yourself.',
            content='''<h2>Prescription Manipulation Scandal Rocks Biratnagar: What Patients Need to Know</h2>

<p class="lead">A pharmacy operating near Nobel Medical College in Biratnagar has been caught deliberately altering doctor prescriptions—changing "1 tablet" to "15" or "18" tablets—to defraud vulnerable patients purchasing expensive surgical medications on credit. The fraud was discovered when an educated patient's relative compared the original prescription with the pharmacy's photocopy. The pharmacist has fled after being confronted.</p>

<h3>What Happened?</h3>

<p>In a shocking breach of medical ethics and patient trust, a pharmacy operating outside Nobel Medical College in Biratnagar was discovered systematically manipulating doctor-written prescriptions. The fraud came to light when an educated patient's relative, suspicious about their bill, compared the original doctor's prescription with the pharmacy's photocopy and found deliberate alterations.</p>

<p><strong>Specific cases uncovered:</strong></p>

<ul>
    <li><strong>Recumid:</strong> Doctor prescribed "1" tablet (Rs. 640), pharmacy altered it to "15" tablets by adding a "5"</li>
    <li><strong>Destimid:</strong> Doctor prescribed "1" tablet (Rs. 1,208 per unit), pharmacy changed it to "18" tablets by adding an "8"</li>
    <li>Multiple other manipulations suspected across many patients</li>
</ul>

<h4>How They Got Away With It—Until Now</h4>

<p>The pharmacy specifically targeted vulnerable patients who needed credit (उधारो) for expensive surgical medications. Knowing these patients had no immediate cash and were in urgent medical situations, the pharmacist would:</p>

<ol>
    <li>Take the doctor's handwritten prescription</li>
    <li>Photocopy it for "record-keeping"</li>
    <li>Manually add digits to increase quantities (1 → 18, 1 → 15, etc.)</li>
    <li>Bill patients the inflated amounts</li>
    <li>Keep photocopies as false documentation</li>
</ol>

<p>Most patients in rushed, stressful medical situations never thought to count tablets or verify their bills against the original prescription. The fraud was only discovered when one vigilant family member insisted on comparing documents.</p>

<p>When confronted with evidence, the pharmacy owner immediately shut down operations and fled Biratnagar. The pharmacy has not been seen since, and their whereabouts remain unknown.</p>

<h3>Why This Is Extremely Dangerous</h3>

<p>Prescription manipulation isn't just about overcharging patients—it poses serious health risks:</p>

<p><strong>1. Overdosing Risk:</strong> Doubling medication dosages (like changing 8 to 18) can lead to drug toxicity, organ damage, or life-threatening reactions, especially with medications that have narrow therapeutic windows like blood thinners, diabetes medications, or heart medications.</p>

<p><strong>2. Treatment Failure:</strong> When patients take more medication than prescribed, they may run out before their next appointment, leading to gaps in treatment for chronic conditions like diabetes, hypertension, or infections.</p>

<p><strong>3. Financial Exploitation:</strong> Patients end up paying for medications they don't need, often at a time when they're already facing medical expenses.</p>

<p><strong>4. Loss of Medical Oversight:</strong> Doctors prescribe specific dosages based on patient condition, weight, age, and other medications. Altering these dosages bypasses critical medical judgment.</p>

<h3>A Growing Problem in Nepal's Healthcare System</h3>

<p>While this incident occurred in Biratnagar, it highlights broader concerns about healthcare transparency and accountability in Nepal. What makes this case particularly disturbing is how it specifically exploited vulnerable patients:</p>

<p><strong>The exploitation of medical emergencies:</strong> The pharmacy primarily targeted patients who needed expensive surgical medications on credit. These families, already under enormous stress and lacking immediate cash, were in no position to carefully scrutinize bills or count tablets. The pharmacist weaponized their desperation.</p>

<p><strong>The education gap:</strong> As GM Dipesh Rai noted, the fraud was only caught because this particular patient's relative was educated and suspicious. How many less-educated families were defrauded and never knew? How many patients simply trusted the system and paid inflated bills without question?</p>

<p>Patients place enormous trust in medical professionals—doctors, pharmacists, and healthcare institutions. When that trust is violated through deliberate fraud targeting the vulnerable, it affects the entire healthcare ecosystem.</p>

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

<h3>Nobel Medical College's Response</h3>

<p>General Manager Dipesh Rai acknowledged that the hospital administration was shocked by the incident. In a statement, he explained that the fraud was only discovered because the patient's relative was educated enough to be suspicious and had the courage to verify the prescription details.</p>

<p><strong>Immediate actions taken by Nobel Medical College:</strong></p>

<ul>
    <li><strong>Digital prescription system:</strong> The hospital is immediately moving away from handwritten prescriptions to a computer-based digital system to prevent such manipulation</li>
    <li><strong>Pharmacy meetings:</strong> Hospital held urgent meetings with all outside pharmacies operating near the facility (notably, the fraudulent pharmacy owner did not attend)</li>
    <li><strong>Patient advisory:</strong> Hospital now urges all patients to:
        <ul>
            <li>Verify that purchased medicines match the doctor's original prescription</li>
            <li>Count medications before leaving the pharmacy</li>
            <li>Keep the original prescription safe for final reconciliation</li>
            <li>Purchase from any pharmacy they trust, not just nearby ones</li>
        </ul>
    </li>
</ul>

<p>GM Rai noted that most patients in rushed, stressful situations don't have the presence of mind to count tablets or verify documents—exactly what the fraudulent pharmacist was counting on.</p>

<h3>What Should Happen Next?</h3>

<p>The Biratnagar incident demands immediate action from multiple parties:</p>

<p><strong>For Medical Institutions:</strong> Nobel Medical College has already begun implementing safeguards, but other hospitals across Nepal should take note and proactively move to digital prescription systems before similar incidents occur at their facilities.</p>

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

<p><strong>If you purchased medications from pharmacies near Nobel Medical College in Biratnagar (especially on credit), particularly Recumid or Destimid, you may have been affected.</strong></p>

<p>Take these steps immediately:</p>

<ol>
    <li><strong>Compare your original prescription with pharmacy bills:</strong> Look for added digits (1 changed to 18, 1 changed to 15, etc.). Check specifically for Recumid and Destimid but also other expensive surgical medications</li>
    <li><strong>Count remaining medications:</strong> If you were prescribed 1 tablet but billed for 15-18, you should have extras. If you don't, you may have been defrauded</li>
    <li><strong>Contact your prescribing doctor</strong> to verify the original prescription quantities if you no longer have the original prescription</li>
    <li><strong>Report to authorities:</strong> File complaints with:
        <ul>
            <li>Nepal Pharmacy Council (www.nepalpharmacycouncil.org.np)</li>
            <li>Local police (this is criminal fraud)</li>
            <li>Nobel Medical College administration (they are cooperating with affected patients)</li>
        </ul>
    </li>
    <li><strong>Get a medication review</strong> from your doctor if you took the wrong dosages</li>
    <li><strong>Share your experience</strong> to help other victims come forward and assist authorities in understanding the full scope</li>
</ol>

<p><strong>For future protection:</strong> Never purchase medications on credit from pharmacies you don't fully trust. If credit is necessary, insist on keeping the original prescription and take a photo before handing it over.</p>

<h3>Your Voice Matters</h3>

<p>Healthcare in Nepal will only improve when patients speak up about problems and share both positive and negative experiences. Whether it's prescription fraud, excessive wait times, unprofessional behavior, or excellent care that deserves recognition—your review helps other patients make informed decisions.</p>

<p>The Biratnagar pharmacy incident is a reminder that healthcare quality isn't guaranteed by institutional names or fancy facilities. It's built on trust, accountability, and transparency—values that only thrive when patients stay informed and vigilant.</p>

<div class="alert alert-info mt-4">
    <strong>Have you visited Nobel Medical College or other hospitals in Biratnagar?</strong> Share your experience to help other patients make informed healthcare decisions. Your review could prevent someone else from encountering similar problems.
</div>''',
            category_id=category.id,
            meta_description='Pharmacy at Nobel Medical College caught altering prescriptions. Learn how to verify your medications and protect yourself from dosage fraud in Nepal.',
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
