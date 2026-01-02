"""
Seed additional Health Digest articles (Women's Health, Nutrition, Mental Health)
Run this to add more articles to the database
"""
from app import app, db
from models import Article, ArticleCategory, Specialty
from datetime import datetime, timedelta


def seed_more_articles():
    """Create additional health articles"""
    with app.app_context():
        print("📝 Seeding additional Health Digest articles...")

        # Get categories and specialties
        womens_cat = ArticleCategory.query.filter_by(slug='womens-health').first()
        nutrition_cat = ArticleCategory.query.filter_by(slug='nutrition').first()
        mental_cat = ArticleCategory.query.filter_by(slug='mental-health').first()

        gynecology = Specialty.query.filter_by(name='Gynecologist').first()
        psychiatry = Specialty.query.filter_by(name='Psychiatrist').first()
        general = Specialty.query.filter_by(name='General Practitioner').first()

        articles_data = [
            {
                'title': 'Women\'s Health in Nepal: Challenges and Essential Care',
                'slug': 'womens-health-nepal-challenges-care',
                'category_id': womens_cat.id if womens_cat else 5,
                'summary': 'From maternal health to nutrition challenges, understanding the unique health needs of women in Nepal and how to access quality care.',
                'content': """
<p>Women's health in Nepal faces unique challenges shaped by cultural practices, geographic barriers, and evolving healthcare access. Understanding these challenges—and knowing where to find help—can make all the difference in maintaining lifelong wellness.</p>

<h2>The Current Landscape</h2>

<p>While Nepal has made significant strides in maternal healthcare over the past two decades, disparities remain. Urban women generally have better access to healthcare facilities, while those in remote areas face significant barriers to quality medical attention.</p>

<p>Young married women, in particular, face nutritional challenges. Research shows that newly married women often have lower social status within households, which can affect their access to adequate nutrition and healthcare decision-making power.</p>

<h2>Key Health Concerns for Nepali Women</h2>

<h3>Maternal Health</h3>

<p>Pregnancy and childbirth remain critical health events requiring proper care:</p>

<ul>
<li><strong>Prenatal care:</strong> Regular checkups throughout pregnancy help detect complications early</li>
<li><strong>Nutritional needs:</strong> Pregnant and nursing mothers need adequate iron, calcium, and folic acid</li>
<li><strong>Safe delivery:</strong> Access to skilled birth attendants reduces maternal and infant mortality</li>
<li><strong>Postpartum care:</strong> The weeks after delivery require monitoring and support</li>
</ul>

<p>Most urban areas now have birthing centers and hospitals equipped for safe deliveries. Government programs increasingly provide free or subsidized maternal healthcare services.</p>

<h3>Anemia and Nutritional Deficiencies</h3>

<p>Iron deficiency anemia affects a significant portion of Nepali women, causing:</p>

<ul>
<li>Persistent fatigue and weakness</li>
<li>Difficulty concentrating</li>
<li>Increased susceptibility to infections</li>
<li>Complications during pregnancy</li>
</ul>

<p>Simple blood tests can diagnose anemia. Treatment typically involves iron supplements and dietary changes—including more leafy greens, lentils, and when possible, lean meat or fortified foods.</p>

<h3>Reproductive Health</h3>

<p>Understanding your reproductive health is essential:</p>

<p><strong>Menstrual health:</strong> Irregular, extremely painful, or unusually heavy periods warrant medical consultation. These could indicate underlying conditions requiring treatment.</p>

<p><strong>Family planning:</strong> Access to contraception and reproductive health services has improved in urban Nepal. Many healthcare centers now offer counseling and various contraceptive options.</p>

<p><strong>Cervical cancer screening:</strong> Regular screening can detect precancerous changes early. Women over 30 should discuss screening options with their healthcare provider.</p>

<h3>Common Health Issues</h3>

<p>Several conditions disproportionately affect women:</p>

<p><strong>Thyroid disorders:</strong> More common in women, thyroid problems can cause fatigue, weight changes, and mood shifts. A simple blood test can diagnose thyroid issues.</p>

<p><strong>Urinary tract infections (UTIs):</strong> Women are more susceptible to UTIs. Symptoms include painful urination, frequent urges, and lower abdominal discomfort. Early treatment prevents kidney complications.</p>

<p><strong>Osteoporosis risk:</strong> After menopause, women face increased bone loss. Adequate calcium and vitamin D intake, along with weight-bearing exercise, helps maintain bone strength.</p>

<h2>Overcoming Barriers to Healthcare</h2>

<p>Many Nepali women face obstacles when seeking healthcare:</p>

<h3>Cultural and Social Barriers</h3>

<p>Traditional gender roles may limit women's healthcare access. Some women need permission from family members to seek medical care or lack independent financial resources for treatment.</p>

<p>Empowerment comes through education and open family communication about health needs. Women's health isn't a luxury—it's essential for family wellbeing.</p>

<h3>Geographic Challenges</h3>

<p>Remote areas have fewer healthcare facilities and specialists. However, expanding community health worker programs bring basic services closer to underserved populations.</p>

<p>Urban women in Kathmandu, Pokhara, and other cities have access to gynecologists, maternal health specialists, and comprehensive women's health services.</p>

<h3>Financial Constraints</h3>

<p>Government programs increasingly provide free or subsidized services for maternal health, family planning, and basic healthcare. Many hospitals offer payment plans or reduced fees based on income.</p>

<h2>Taking Charge of Your Health</h2>

<h3>Regular Checkups</h3>

<p>Preventive care catches problems early:</p>

<ul>
<li>Annual general health checkups</li>
<li>Blood pressure and blood sugar monitoring</li>
<li>Breast self-examination monthly; clinical breast exams as recommended</li>
<li>Pap smears for cervical cancer screening (starting around age 21-30)</li>
<li>Bone density tests after menopause if risk factors present</li>
</ul>

<h3>Nutrition for Women's Health</h3>

<p>Adequate nutrition supports all aspects of women's health:</p>

<ul>
<li><strong>Iron-rich foods:</strong> Dark leafy greens, lentils, beans, fortified cereals</li>
<li><strong>Calcium sources:</strong> Dairy products, leafy greens, fortified plant milks</li>
<li><strong>Folic acid:</strong> Essential before and during pregnancy; found in leafy greens and fortified grains</li>
<li><strong>Protein:</strong> Lentils, beans, dairy, eggs, lean meat support tissue repair and immunity</li>
</ul>

<h3>Exercise and Mental Wellbeing</h3>

<p>Physical activity benefits both body and mind:</p>

<ul>
<li>Reduces risk of chronic diseases</li>
<li>Strengthens bones and muscles</li>
<li>Improves mood and reduces stress</li>
<li>Helps maintain healthy weight</li>
<li>Supports better sleep</li>
</ul>

<p>Even 30 minutes of walking most days makes a significant difference.</p>

<h2>When to See a Doctor</h2>

<p>Don't delay seeking care for:</p>

<ul>
<li>Abnormal vaginal bleeding or discharge</li>
<li>Severe menstrual pain or irregularity</li>
<li>Persistent pelvic or abdominal pain</li>
<li>Pregnancy planning or prenatal care</li>
<li>Menopause symptoms affecting quality of life</li>
<li>Breast lumps or changes</li>
<li>Persistent fatigue or unexplained weight changes</li>
</ul>

<h2>Finding Quality Care</h2>

<p>Nepal's healthcare system offers multiple options:</p>

<p><strong>Government hospitals and health posts:</strong> Provide affordable basic and maternal healthcare services across the country.</p>

<p><strong>Private clinics and hospitals:</strong> Available in urban areas, offering specialized women's health services, gynecology, and obstetrics care.</p>

<p><strong>Teaching hospitals:</strong> Major medical colleges in Kathmandu and other cities provide comprehensive care with specialists.</p>

<h2>A Path Forward</h2>

<p>Women's health encompasses physical, mental, and social wellbeing. By understanding your health needs, advocating for yourself, accessing available services, and maintaining preventive care, you take control of your health journey.</p>

<p>Remember: Your health matters not just for you, but for your family and community. Prioritizing women's health strengthens all of Nepal.</p>
                """,
                'featured_image': '/static/img/womens-health.jpg',
                'meta_description': 'Understanding women\'s health challenges in Nepal, from maternal care to nutrition. Essential guide to accessing quality healthcare services.',
                'meta_keywords': 'women health Nepal, maternal health Kathmandu, gynecologist Nepal, reproductive health, anemia Nepal',
                'related_specialty_id': gynecology.id if gynecology else general.id if general else None,
                'is_published': True,
                'is_featured': True,
                'published_at': datetime.utcnow() - timedelta(days=2)
            },
            {
                'title': 'Nutrition Essentials: Building a Healthy Diet for Your Family',
                'slug': 'nutrition-essentials-healthy-diet-nepal',
                'category_id': nutrition_cat.id if nutrition_cat else 4,
                'summary': 'Practical nutrition guidance for Nepali families. Learn how to meet essential nutritional needs with familiar foods and simple dietary changes.',
                'content': """
<p>Good nutrition is the foundation of health, yet many Nepali families struggle to meet all their nutritional needs. The good news? You don't need expensive supplements or exotic foods—just knowledge about what your body needs and how to get it from everyday meals.</p>

<h2>Understanding Nutritional Basics</h2>

<p>Your body needs two types of nutrients:</p>

<p><strong>Macronutrients</strong> provide energy and building blocks:</p>

<ul>
<li><strong>Carbohydrates:</strong> Your body's primary energy source (rice, roti, bread, potatoes)</li>
<li><strong>Proteins:</strong> Build and repair tissues (dal, beans, meat, eggs, dairy)</li>
<li><strong>Fats:</strong> Support cell function and nutrient absorption (cooking oil, nuts, dairy)</li>
</ul>

<p><strong>Micronutrients</strong> support bodily functions:</p>

<ul>
<li><strong>Vitamins:</strong> Essential for immunity, energy, bone health</li>
<li><strong>Minerals:</strong> Including iron, calcium, potassium for various body functions</li>
</ul>

<p>The key principle: <em>quality matters more than specific diet trends</em>. Focus on whole, minimally processed foods rather than worrying about "low-carb" or "low-fat" labels.</p>

<h2>The Healthy Plate Formula</h2>

<p>A simple visual guide for balanced meals:</p>

<ul>
<li><strong>Half your plate:</strong> Vegetables and fruits (mix of colors)</li>
<li><strong>Quarter of your plate:</strong> Whole grains (brown rice, whole wheat roti)</li>
<li><strong>Quarter of your plate:</strong> Protein (dal, beans, lean meat, eggs)</li>
</ul>

<p>This traditional wisdom aligns perfectly with dal-bhat tarkari—just ensure vegetables take up the largest portion.</p>

<h2>Essential Nutrients Nepalis Often Need More Of</h2>

<h3>Dietary Fiber</h3>

<p>Fiber aids digestion, controls blood sugar, and helps you feel full longer.</p>

<p><strong>How to get more:</strong></p>

<ul>
<li>Choose brown rice over white rice when possible</li>
<li>Eat whole fruits instead of juice</li>
<li>Include dal and beans daily</li>
<li>Add vegetables to every meal</li>
<li>Choose whole wheat roti over refined flour</li>
<li>Snack on nuts and seeds</li>
</ul>

<h3>Calcium and Vitamin D</h3>

<p>These work together for strong bones and teeth. Deficiency increases osteoporosis risk, especially for women after menopause.</p>

<p><strong>Good sources:</strong></p>

<ul>
<li><strong>Calcium:</strong> Dairy products (milk, yogurt, cheese), dark leafy greens (spinach, saag), sesame seeds, fortified foods</li>
<li><strong>Vitamin D:</strong> Sunlight exposure (15-20 minutes daily), fatty fish, fortified milk, egg yolks</li>
</ul>

<p>Many Nepalis get adequate sunlight for vitamin D production, but those who spend most time indoors may need supplements.</p>

<h3>Iron</h3>

<p>Iron deficiency causes anemia—widespread in Nepal, particularly among women and children. Symptoms include fatigue, weakness, and difficulty concentrating.</p>

<p><strong>Iron-rich foods:</strong></p>

<ul>
<li>Dark leafy greens (spinach, fenugreek leaves)</li>
<li>Lentils and beans</li>
<li>Meat (especially liver, though consume in moderation)</li>
<li>Fortified cereals</li>
<li>Dried fruits (raisins, apricots)</li>
</ul>

<p><strong>Tip:</strong> Vitamin C helps iron absorption. Eat iron-rich foods with tomatoes, citrus fruits, or bell peppers.</p>

<h3>Potassium</h3>

<p>Potassium supports heart, kidney, muscle, and nerve function. It also helps counter sodium's blood pressure effects.</p>

<p><strong>Potassium sources:</strong></p>

<ul>
<li>Bananas</li>
<li>Potatoes and sweet potatoes</li>
<li>Beans and lentils</li>
<li>Dark leafy greens</li>
<li>Beets</li>
<li>Yogurt</li>
</ul>

<h2>What to Reduce in Your Diet</h2>

<h3>Added Sugars</h3>

<p>Excess sugar contributes to weight gain, diabetes, and heart disease. Most added sugar comes from sweetened beverages, desserts, and processed snacks.</p>

<p><strong>Simple swaps:</strong></p>

<ul>
<li>Replace soda and sweetened tea with water or unsweetened tea</li>
<li>Reduce sugar in homemade chai gradually</li>
<li>Choose fresh fruit over sweets for dessert</li>
<li>Read labels on packaged foods</li>
</ul>

<h3>Saturated Fats</h3>

<p>While traditional ghee has cultural significance, excessive saturated fat raises cholesterol levels.</p>

<p><strong>Healthier approaches:</strong></p>

<ul>
<li>Use ghee sparingly for flavor rather than as primary cooking fat</li>
<li>Cook with mustard oil, sunflower oil, or olive oil</li>
<li>Limit deep-fried foods</li>
<li>Choose lean cuts of meat</li>
<li>Include plant-based proteins regularly</li>
</ul>

<h3>Sodium (Salt)</h3>

<p>Traditional Nepali cuisine can be high in sodium, especially with pickles (achar) and processed foods. Excess sodium raises blood pressure.</p>

<p><strong>Reduce sodium by:</strong></p>

<ul>
<li>Using less salt when cooking</li>
<li>Limiting pickles and processed snacks</li>
<li>Flavoring food with herbs, spices, lemon juice</li>
<li>Choosing fresh vegetables over canned</li>
<li>Reading nutrition labels on packaged foods</li>
</ul>

<h2>Building Healthy Habits</h2>

<h3>Eat Colorfully</h3>

<p>Different colored foods provide different nutrients. Aim for variety:</p>

<ul>
<li><strong>Green:</strong> Leafy vegetables (spinach, saag, lettuce)</li>
<li><strong>Red/Orange:</strong> Tomatoes, carrots, pumpkin, bell peppers</li>
<li><strong>Purple:</strong> Eggplant, red cabbage, beets</li>
<li><strong>White/Brown:</strong> Cauliflower, mushrooms, potatoes</li>
</ul>

<h3>Practice Portion Control</h3>

<p>Even healthy foods contribute to weight gain when portions are too large:</p>

<ul>
<li>Eat until satisfied, not stuffed</li>
<li>Serve appropriate portions rather than bringing serving dishes to the table</li>
<li>Listen to hunger and fullness cues</li>
<li>Avoid eating while distracted (watching TV, using phone)</li>
</ul>

<h3>Stay Hydrated</h3>

<p>Water is essential for all body functions. Aim for 8-10 glasses daily, more in hot weather or when physically active.</p>

<h3>Plan Ahead</h3>

<p>Meal planning helps ensure nutritious choices:</p>

<ul>
<li>Plan weekly menus including variety of vegetables and proteins</li>
<li>Shop with a list to avoid impulse purchases</li>
<li>Prepare vegetables in advance for easier cooking</li>
<li>Keep healthy snacks available (fruits, nuts, yogurt)</li>
</ul>

<h2>Nutrition Through Life Stages</h2>

<p><strong>Children and teens:</strong> Need adequate calcium for growing bones, iron for development, and protein for growth. Establish healthy eating patterns early.</p>

<p><strong>Pregnant and nursing mothers:</strong> Require extra iron, folic acid, calcium, and overall calories. Prenatal care includes nutritional guidance.</p>

<p><strong>Adults:</strong> Focus on maintaining healthy weight, preventing chronic disease, and meeting all nutritional needs through balanced diet.</p>

<p><strong>Older adults:</strong> May need less food overall but require nutrient-dense choices. Calcium and vitamin D become especially important for bone health.</p>

<h2>When to Consider Supplements</h2>

<p>For most people, a balanced diet provides adequate nutrition. Supplements may be appropriate for:</p>

<ul>
<li>Diagnosed deficiencies (confirmed by blood tests)</li>
<li>Pregnant women (prenatal vitamins with folic acid and iron)</li>
<li>People with limited sun exposure (vitamin D)</li>
<li>Strict vegetarians/vegans (B12 supplements)</li>
<li>Those with absorption disorders</li>
</ul>

<p><strong>Always consult a healthcare provider before taking supplements.</strong> More isn't always better, and some supplements can interact with medications or cause harm in excess.</p>

<h2>Making It Work in Nepal</h2>

<p>Good nutrition doesn't require imported superfoods or expensive specialty items. Traditional Nepali foods—dal, rice, vegetables, yogurt—form an excellent nutritional foundation when consumed in right proportions.</p>

<p>The keys are:</p>

<ul>
<li>Emphasizing vegetables and fruits</li>
<li>Including protein at every meal</li>
<li>Choosing whole grains when possible</li>
<li>Limiting added sugars, excessive salt, and fried foods</li>
<li>Staying physically active</li>
</ul>

<p>Small, sustainable changes lead to lasting health improvements. You don't need to overhaul your entire diet overnight—start with one or two changes and build from there.</p>

<p>Your family's health begins with what's on your plate. Choose wisely, eat mindfully, and enjoy the journey toward better nutrition.</p>
                """,
                'featured_image': '/static/img/nutrition.jpg',
                'meta_description': 'Complete nutrition guide for Nepali families. Learn essential nutrients, healthy eating habits, and practical tips for balanced meals.',
                'meta_keywords': 'nutrition Nepal, healthy eating Kathmandu, balanced diet, vitamins minerals, family nutrition Nepal',
                'related_specialty_id': general.id if general else None,
                'is_published': True,
                'is_featured': False,
                'published_at': datetime.utcnow() - timedelta(days=3)
            },
            {
                'title': 'Understanding Mental Health in Nepal: Breaking the Silence',
                'slug': 'understanding-mental-health-nepal',
                'category_id': mental_cat.id if mental_cat else 6,
                'summary': 'Mental health challenges affect millions in Nepal, yet stigma prevents many from seeking help. Understanding the crisis is the first step toward change.',
                'content': """
<p>A silent crisis unfolds across Nepal. Suicide rates have surged 72% over the past decade, with mental health issues identified as the predominant cause. Yet many who suffer do so in silence, afraid of judgment, unaware of treatment options, or unable to access care.</p>

<p>It's time to break that silence.</p>

<h2>The Reality of Mental Health in Nepal</h2>

<p>Mental health conditions are common—and they can affect anyone. Depression, anxiety, trauma-related disorders, and other mental health conditions don't discriminate by age, gender, education, or economic status.</p>

<p>The numbers tell a sobering story:</p>

<ul>
<li>Suicide rates have climbed dramatically, particularly among youth</li>
<li>Following the 2015 earthquake, surveys found one in three adults showing symptoms of depression</li>
<li>One in ten earthquake survivors reported suicidal thoughts just months after the disaster</li>
<li>Academic pressure contributes to student suicides, especially following exam results</li>
</ul>

<p>Yet despite this growing crisis, mental health remains misunderstood and stigmatized across Nepal.</p>

<h2>Common Mental Health Conditions</h2>

<h3>Depression</h3>

<p>More than temporary sadness, clinical depression affects how you think, feel, and function daily. Symptoms include:</p>

<ul>
<li>Persistent sad or empty mood lasting weeks or months</li>
<li>Loss of interest in activities you once enjoyed</li>
<li>Changes in appetite and sleep patterns</li>
<li>Fatigue and lack of energy</li>
<li>Difficulty concentrating or making decisions</li>
<li>Feelings of worthlessness or excessive guilt</li>
<li>Thoughts of death or suicide</li>
</ul>

<p>Depression is treatable. Combination of therapy, sometimes medication, and lifestyle changes helps most people recover.</p>

<h3>Anxiety Disorders</h3>

<p>Everyone feels anxious sometimes, but anxiety disorders involve excessive worry that interferes with daily life. Types include:</p>

<ul>
<li><strong>Generalized anxiety disorder:</strong> Persistent worry about various aspects of life</li>
<li><strong>Panic disorder:</strong> Sudden episodes of intense fear with physical symptoms</li>
<li><strong>Social anxiety:</strong> Extreme fear of social situations and judgment</li>
<li><strong>Specific phobias:</strong> Intense fear of particular objects or situations</li>
</ul>

<p>Symptoms may include racing heart, sweating, trembling, difficulty breathing, and overwhelming fear. Treatment through therapy and sometimes medication is highly effective.</p>

<h3>Post-Traumatic Stress Disorder (PTSD)</h3>

<p>Traumatic events—natural disasters, violence, accidents, loss—can lead to PTSD. Symptoms include:</p>

<ul>
<li>Intrusive memories or flashbacks of the trauma</li>
<li>Nightmares and sleep disturbances</li>
<li>Avoiding reminders of the traumatic event</li>
<li>Being easily startled or constantly on edge</li>
<li>Negative changes in mood and thinking</li>
</ul>

<p>Many Nepalis experienced trauma during the 2015 earthquakes, civil conflict, or personal tragedies. PTSD is not weakness—it's a normal response to abnormal events, and it's treatable.</p>

<h3>Substance Use Disorders</h3>

<p>Alcohol and drug addiction are mental health conditions requiring treatment. They often co-occur with depression, anxiety, or trauma.</p>

<h2>Why Mental Health Matters</h2>

<p>Mental health is inseparable from overall health. Untreated mental health conditions:</p>

<ul>
<li>Reduce quality of life and ability to function</li>
<li>Strain relationships and family dynamics</li>
<li>Decrease work or academic performance</li>
<li>Increase risk of physical health problems</li>
<li>Can lead to substance abuse</li>
<li>Raise suicide risk</li>
</ul>

<p>Conversely, good mental health enables you to:</p>

<ul>
<li>Handle life's stresses and challenges</li>
<li>Maintain healthy relationships</li>
<li>Work productively</li>
<li>Make meaningful contributions to community</li>
<li>Realize your full potential</li>
</ul>

<h2>Breaking Down Stigma</h2>

<p>Stigma remains one of the biggest barriers to mental healthcare in Nepal. Many people fear:</p>

<ul>
<li><strong>Judgment:</strong> Being seen as "crazy" or weak</li>
<li><strong>Discrimination:</strong> Impact on marriage prospects, employment, social standing</li>
<li><strong>Misunderstanding:</strong> Family and friends not recognizing mental illness as real medical condition</li>
</ul>

<p>This stigma is based on misconceptions:</p>

<p><strong>Myth:</strong> Mental illness is a character weakness or personal failing.<br>
<strong>Reality:</strong> Mental health conditions are medical conditions involving brain chemistry, genetics, and life experiences.</p>

<p><strong>Myth:</strong> People with mental illness can "snap out of it" if they try hard enough.<br>
<strong>Reality:</strong> Mental health conditions require treatment, just like diabetes or high blood pressure.</p>

<p><strong>Myth:</strong> Mental illness is rare.<br>
<strong>Reality:</strong> Mental health conditions are common. Many people you know have experienced them—they just don't talk about it.</p>

<p><strong>Myth:</strong> Seeking mental health treatment means you're weak.<br>
<strong>Reality:</strong> Seeking help takes courage and is a sign of strength and self-awareness.</p>

<h2>Risk Factors and Warning Signs</h2>

<p>Anyone can develop a mental health condition, but certain factors increase risk:</p>

<ul>
<li>Family history of mental illness</li>
<li>Traumatic experiences (abuse, violence, disasters, loss)</li>
<li>Chronic stress (financial, work-related, relationship problems)</li>
<li>Serious medical conditions</li>
<li>Substance abuse</li>
<li>Social isolation and loneliness</li>
</ul>

<p><strong>Warning signs someone may need help:</strong></p>

<ul>
<li>Withdrawing from activities and relationships</li>
<li>Dramatic mood changes or personality shifts</li>
<li>Significant changes in eating or sleeping</li>
<li>Difficulty functioning at work, school, or home</li>
<li>Increased substance use</li>
<li>Expressing feelings of hopelessness</li>
<li>Talking about suicide or death</li>
<li>Giving away possessions</li>
<li>Engaging in risky or self-destructive behavior</li>
</ul>

<h2>Taking Action</h2>

<h3>If You're Struggling</h3>

<p>Recognizing you need help is the first step. Mental health conditions are treatable, and recovery is possible:</p>

<ul>
<li><strong>Talk to someone you trust:</strong> A family member, friend, teacher, or religious leader</li>
<li><strong>Seek professional help:</strong> A doctor, psychologist, or psychiatrist can provide diagnosis and treatment</li>
<li><strong>Contact a crisis line:</strong> If experiencing suicidal thoughts, reach out immediately (see resources below)</li>
<li><strong>Be patient with yourself:</strong> Recovery takes time and effort, but it happens</li>
</ul>

<h3>If Someone You Know Is Struggling</h3>

<p>Your support can make a life-saving difference:</p>

<ul>
<li><strong>Listen without judgment:</strong> Create a safe space for them to share</li>
<li><strong>Express concern and care:</strong> Let them know you're worried and want to help</li>
<li><strong>Encourage professional help:</strong> Offer to help find resources or accompany them to appointments</li>
<li><strong>Take suicide threats seriously:</strong> Never dismiss or minimize talk of suicide</li>
<li><strong>Stay connected:</strong> Regular contact shows you care</li>
</ul>

<h2>The Path Forward</h2>

<p>Nepal faces significant mental health challenges—from professional shortages to limited services outside urban areas. But change is happening:</p>

<ul>
<li>Increasing awareness and public discussion</li>
<li>Growing number of mental health professionals</li>
<li>Expanding services and treatment options</li>
<li>Advocacy for mental health policy and funding</li>
</ul>

<p>Each conversation about mental health chips away at stigma. Each person who seeks help demonstrates courage. Each community that supports mental wellness creates space for healing.</p>

<h2>Crisis Resources</h2>

<p><strong>If you or someone you know is in crisis:</strong></p>

<ul>
<li><strong>Suicide Prevention Hotline (Nepal):</strong> 1660 0102004</li>
<li><strong>Transcultural Psychosocial Organization (TPO):</strong> 01-4102666</li>
<li><strong>Emergency services:</strong> 100 or 102</li>
</ul>

<p>Mental health challenges are not signs of weakness—they are medical conditions that respond to treatment. By understanding mental health, challenging stigma, and supporting those who struggle, we build a healthier, more compassionate Nepal.</p>

<p>If you're struggling, please know: you are not alone, it's not your fault, and help is available. Recovery is possible.</p>
                """,
                'featured_image': '/static/img/mental-health-understanding.jpg',
                'meta_description': 'Understanding mental health crisis in Nepal: depression, anxiety, PTSD, stigma, and the path toward accessible mental healthcare.',
                'meta_keywords': 'mental health Nepal, depression Kathmandu, anxiety treatment, PTSD Nepal, suicide prevention, mental health stigma',
                'related_specialty_id': psychiatry.id if psychiatry else general.id if general else None,
                'is_published': True,
                'is_featured': True,
                'published_at': datetime.utcnow() - timedelta(days=1)
            },
            {
                'title': 'Getting Mental Health Help in Nepal: A Practical Guide',
                'slug': 'getting-mental-health-help-nepal',
                'category_id': mental_cat.id if mental_cat else 6,
                'summary': 'Navigating Nepal\'s mental healthcare system can be challenging. This guide helps you find qualified professionals, understand treatment options, and overcome barriers to care.',
                'content': """
<p>Deciding to seek mental health help takes courage. But once you've made that decision, you face a new challenge: actually finding and accessing quality care in Nepal's limited mental healthcare system.</p>

<p>While obstacles exist, help is available. This guide helps you navigate the system, find qualified professionals, understand what to expect, and get the support you deserve.</p>

<h2>Understanding the Landscape</h2>

<p>Nepal faces a severe shortage of mental health professionals:</p>

<ul>
<li>Only <strong>144 psychiatrists</strong> nationwide</li>
<li>Approximately <strong>30 practicing psychologists</strong></li>
<li>0.17 psychiatrists per 100,000 people (far below WHO recommendations)</li>
<li>Most professionals concentrated in Kathmandu and major urban centers</li>
</ul>

<p>This shortage means:</p>

<ul>
<li>Long wait times for appointments in some facilities</li>
<li>Higher costs, especially in private sector</li>
<li>Limited access in rural and remote areas</li>
<li>Some therapists handling cases outside their specialization</li>
</ul>

<p>Despite these challenges, many people do find effective treatment. Being informed and persistent increases your chances of getting quality care.</p>

<h2>Types of Mental Health Professionals</h2>

<p>Different professionals provide different services:</p>

<h3>Psychiatrists</h3>

<p>Medical doctors specializing in mental health. They can:</p>

<ul>
<li>Diagnose mental health conditions</li>
<li>Prescribe medications</li>
<li>Provide therapy (though many focus primarily on medication management)</li>
<li>Treat severe mental illnesses</li>
</ul>

<p>See a psychiatrist if you need medication or have severe symptoms.</p>

<h3>Psychologists</h3>

<p>Mental health professionals with advanced degrees in psychology. They:</p>

<ul>
<li>Provide therapy and counseling</li>
<li>Conduct psychological assessments</li>
<li>Cannot prescribe medication (only psychiatrists can)</li>
<li>Often specialize in specific therapy approaches</li>
</ul>

<p>Psychologists are ideal for talk therapy, counseling, and behavioral interventions.</p>

<h3>Counselors</h3>

<p>Trained in counseling techniques, typically with less extensive education than psychologists. They provide:</p>

<ul>
<li>General counseling for life challenges</li>
<li>Support during difficult times</li>
<li>Guidance on relationships, stress management</li>
</ul>

<p>Counselors can help with everyday stressors and mild symptoms.</p>

<h3>Psychiatric Nurses</h3>

<p>Nurses with specialized mental health training who work in psychiatric facilities and can provide:</p>

<ul>
<li>Patient care and monitoring</li>
<li>Basic counseling and support</li>
<li>Medication administration</li>
</ul>

<h2>Where to Find Help</h2>

<h3>Government Hospitals and Health Posts</h3>

<p><strong>Advantages:</strong></p>
<ul>
<li>More affordable or free services</li>
<li>Available across the country</li>
<li>Some have dedicated mental health units</li>
</ul>

<p><strong>Challenges:</strong></p>
<ul>
<li>Limited specialist availability, especially outside Kathmandu</li>
<li>Long wait times</li>
<li>May focus primarily on medication rather than therapy</li>
</ul>

<p><strong>Major government mental health facilities:</strong></p>
<ul>
<li>Mental Health Hospital, Lagankhel, Kathmandu</li>
<li>Patan Hospital Mental Health Unit</li>
<li>Teaching hospitals affiliated with medical colleges</li>
<li>District hospital mental health services (availability varies)</li>
</ul>

<h3>Private Clinics and Hospitals</h3>

<p><strong>Advantages:</strong></p>
<ul>
<li>More specialists available</li>
<li>Shorter wait times</li>
<li>More therapy options</li>
<li>Better privacy and comfort</li>
</ul>

<p><strong>Challenges:</strong></p>
<ul>
<li>Higher costs (sessions typically Rs 1,000-3,000+)</li>
<li>Mostly in Kathmandu and major cities</li>
<li>Quality varies—important to research providers</li>
</ul>

<h3>NGOs and Community Organizations</h3>

<p>Several organizations provide mental health services:</p>

<ul>
<li><strong>Transcultural Psychosocial Organization (TPO) Nepal:</strong> Community mental health programs, crisis support</li>
<li><strong>Centre for Mental Health and Counselling (CMC):</strong> Affordable counseling services</li>
<li><strong>Various NGOs:</strong> Provide support groups, counseling, and resources</li>
</ul>

<p>These often offer more affordable options and community-based care.</p>

<h3>University Counseling Centers</h3>

<p>Some universities offer counseling services for students, often free or low-cost.</p>

<h2>What to Expect: Your First Appointment</h2>

<h3>Initial Assessment</h3>

<p>Your first session typically involves:</p>

<ul>
<li>Discussing what brought you in</li>
<li>Reviewing your symptoms and how long you've experienced them</li>
<li>Questions about your medical history, family history, life circumstances</li>
<li>Mental health screening or assessment</li>
<li>Discussion of treatment options</li>
</ul>

<p>Be honest and open—everything you share is confidential and helps your provider understand how to help you.</p>

<h3>Treatment Options</h3>

<p><strong>Therapy/Counseling:</strong></p>

<p>Talk therapy helps you understand your thoughts, feelings, and behaviors. Common approaches include:</p>

<ul>
<li><strong>Cognitive Behavioral Therapy (CBT):</strong> Identifies and changes negative thought patterns</li>
<li><strong>Interpersonal Therapy:</strong> Focuses on relationships and communication</li>
<li><strong>Trauma-focused therapy:</strong> Addresses PTSD and trauma</li>
<li><strong>Supportive counseling:</strong> Provides emotional support and coping strategies</li>
</ul>

<p>Therapy typically involves regular sessions (weekly or biweekly) over several weeks or months.</p>

<p><strong>Medication:</strong></p>

<p>Psychiatric medications can help with various conditions:</p>

<ul>
<li><strong>Antidepressants:</strong> For depression and anxiety</li>
<li><strong>Anti-anxiety medications:</strong> For severe anxiety (often short-term)</li>
<li><strong>Mood stabilizers:</strong> For bipolar disorder</li>
<li><strong>Antipsychotics:</strong> For psychosis and severe conditions</li>
</ul>

<p>Medications often take several weeks to show full effects. Work closely with your psychiatrist to find the right medication and dosage. Never stop medication abruptly without medical guidance.</p>

<p><strong>Combined Treatment:</strong></p>

<p>For many conditions, combination of therapy and medication is most effective. You might see both a psychiatrist for medication management and a psychologist for therapy.</p>

<h2>Overcoming Barriers to Care</h2>

<h3>Cost Concerns</h3>

<p>Mental healthcare can be expensive. Strategies to manage costs:</p>

<ul>
<li>Start with government facilities for most affordable care</li>
<li>Ask about sliding scale fees (some private providers adjust based on income)</li>
<li>Check if your employer offers health insurance covering mental health</li>
<li>Look for NGO programs offering subsidized services</li>
<li>Consider group therapy (often less expensive than individual sessions)</li>
</ul>

<h3>Stigma and Privacy</h3>

<p>Fear of judgment prevents many from seeking help. Remember:</p>

<ul>
<li>Mental health professionals are bound by confidentiality</li>
<li>You don't have to tell anyone you're seeing a therapist</li>
<li>Seeking help is a sign of strength, not weakness</li>
<li>Your health matters more than others' opinions</li>
</ul>

<h3>Finding the Right Provider</h3>

<p>Not every therapist is right for every person. A good therapeutic relationship matters:</p>

<ul>
<li><strong>Ask questions:</strong> About their experience, approach, specializations</li>
<li><strong>Trust your instincts:</strong> You should feel comfortable and heard</li>
<li><strong>Give it time:</strong> Try 2-3 sessions before deciding if it's a good fit</li>
<li><strong>It's okay to change:</strong> If someone isn't helping, find another provider</li>
</ul>

<p>Red flags to watch for:</p>

<ul>
<li>Provider seems judgmental or dismissive</li>
<li>Sessions feel unfocused or unproductive</li>
<li>No clear treatment plan or goals</li>
<li>Inappropriate behavior or boundary violations</li>
</ul>

<h3>Geographic Barriers</h3>

<p>If you're outside Kathmandu:</p>

<ul>
<li>Check district hospitals for mental health services</li>
<li>Ask if providers offer phone or video consultations</li>
<li>Look for community health workers trained in basic mental health</li>
<li>Consider traveling to larger cities for initial assessment, then follow-up remotely</li>
</ul>

<h2>Self-Care While Seeking Help</h2>

<p>Professional treatment works best alongside self-care:</p>

<ul>
<li><strong>Maintain routines:</strong> Regular sleep, meals, activity</li>
<li><strong>Stay connected:</strong> Spend time with supportive people</li>
<li><strong>Exercise:</strong> Physical activity helps mood</li>
<li><strong>Avoid self-medication:</strong> Alcohol and drugs worsen mental health</li>
<li><strong>Practice stress reduction:</strong> Meditation, deep breathing, yoga</li>
<li><strong>Set small goals:</strong> Celebrate small accomplishments</li>
</ul>

<h2>Supporting Your Treatment</h2>

<p>To get the most from mental health care:</p>

<ul>
<li><strong>Attend appointments consistently:</strong> Even when you feel better</li>
<li><strong>Be honest with your provider:</strong> About symptoms, medication effects, struggles</li>
<li><strong>Do homework:</strong> Practice techniques between sessions</li>
<li><strong>Track your progress:</strong> Note mood changes, symptom patterns</li>
<li><strong>Communicate:</strong> Tell your provider what's working and what isn't</li>
<li><strong>Be patient:</strong> Improvement takes time</li>
</ul>

<h2>In Crisis: Immediate Help</h2>

<p>If you're in immediate danger or experiencing suicidal thoughts:</p>

<ul>
<li><strong>Call crisis lines:</strong> 1660 0102004 (Suicide Prevention Hotline)</li>
<li><strong>Go to emergency room:</strong> Patan Hospital, Teaching Hospital emergency departments</li>
<li><strong>Call emergency services:</strong> 100 or 102</li>
<li><strong>Reach out to someone:</strong> Family, friend, religious leader—anyone who can help you stay safe</li>
<li><strong>Remove means:</strong> Put distance between yourself and anything you might use to harm yourself</li>
</ul>

<p>Crisis is temporary. With help, you can get through this.</p>

<h2>Moving Forward</h2>

<p>Seeking mental health treatment is an act of courage and self-compassion. While Nepal's mental health system has limitations, help exists. Many people find effective treatment and go on to live fulfilling lives.</p>

<p>The journey may have challenges, but you don't have to navigate it alone. Reach out, ask for help, be persistent in finding care, and be patient with the process.</p>

<p>Your mental health matters. You deserve support, treatment, and the opportunity to heal. Take that first step—reach out today.</p>
                """,
                'featured_image': '/static/img/mental-health-help.jpg',
                'meta_description': 'Practical guide to accessing mental health care in Nepal. Find psychiatrists, psychologists, understand treatment options, and navigate the healthcare system.',
                'meta_keywords': 'mental health help Nepal, psychiatrist Kathmandu, therapy counseling Nepal, mental health treatment, finding psychologist Nepal',
                'related_specialty_id': psychiatry.id if psychiatry else general.id if general else None,
                'is_published': True,
                'is_featured': False,
                'published_at': datetime.utcnow()
            }
        ]

        created_count = 0
        for article_data in articles_data:
            # Check if article already exists
            existing = Article.query.filter_by(slug=article_data['slug']).first()
            if not existing:
                article = Article(**article_data)
                db.session.add(article)
                created_count += 1
                print(f"  ✅ Created: {article_data['title']}")
            else:
                print(f"  ⏭️  Skipped (already exists): {article_data['title']}")

        if created_count > 0:
            db.session.commit()
            print(f"\n🎉 Successfully created {created_count} articles!")
        else:
            print(f"\n✨ All articles already exist in database")


if __name__ == '__main__':
    seed_more_articles()
