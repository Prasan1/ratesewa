"""
Seed initial Health Digest articles
Run this once to populate the database with starter articles
"""
from app import app, db
from models import Article, ArticleCategory, Specialty
from datetime import datetime


def seed_articles():
    """Create initial health articles"""
    with app.app_context():
        print("📝 Seeding Health Digest articles...")

        # Get categories and specialties
        diabetes_cat = ArticleCategory.query.filter_by(slug='diabetes').first()
        bp_cat = ArticleCategory.query.filter_by(slug='blood-pressure').first()
        heart_cat = ArticleCategory.query.filter_by(slug='heart-health').first()

        cardiology = Specialty.query.filter_by(name='Cardiologist').first()
        general = Specialty.query.filter_by(name='General Practitioner').first()

        articles_data = [
            {
                'title': 'Understanding Type 2 Diabetes in Nepal: What You Need to Know',
                'slug': 'understanding-type-2-diabetes-nepal',
                'category_id': diabetes_cat.id if diabetes_cat else 2,
                'summary': 'Diabetes affects millions in Nepal. Learn the warning signs, risk factors, and how to manage this growing health challenge with lifestyle changes and medical care.',
                'content': """
<p>In the bustling streets of Kathmandu and across Nepal's valleys, a silent epidemic is taking hold. Type 2 diabetes, once considered a disease of affluence, now affects an estimated 8-10% of Nepal's adult population—a number that continues to climb each year.</p>

<h2>What Is Type 2 Diabetes?</h2>

<p>Type 2 diabetes occurs when your body becomes resistant to insulin or doesn't produce enough of it to maintain normal blood sugar levels. Unlike Type 1 diabetes, which typically appears in childhood, Type 2 develops gradually and is closely linked to lifestyle factors.</p>

<p>"We're seeing patients in their 30s and 40s being diagnosed, which was rare just a decade ago," explains health experts working in Kathmandu's medical centers. The shift reflects changing dietary patterns and increasingly sedentary lifestyles across urban Nepal.</p>

<h2>Warning Signs You Shouldn't Ignore</h2>

<p>Diabetes often develops slowly, and many people don't realize they have it until complications arise. Watch for these symptoms:</p>

<ul>
<li><strong>Increased thirst and frequent urination</strong> - Your kidneys work overtime to filter excess sugar</li>
<li><strong>Unexplained weight loss</strong> - Despite eating normally or more than usual</li>
<li><strong>Persistent fatigue</strong> - Cells aren't getting the energy they need</li>
<li><strong>Blurred vision</strong> - High blood sugar affects the lens of your eye</li>
<li><strong>Slow-healing wounds</strong> - Particularly on feet and legs</li>
<li><strong>Tingling or numbness</strong> - In hands and feet, a sign of nerve damage</li>
</ul>

<h2>Risk Factors in the Nepali Context</h2>

<p>Several factors increase your risk of developing Type 2 diabetes:</p>

<p><strong>Family History:</strong> If your parents or siblings have diabetes, your risk increases significantly. Genetic predisposition plays a crucial role in Nepal's population.</p>

<p><strong>Diet Changes:</strong> The traditional Nepali diet of dal-bhat, vegetables, and moderate portions has given way to more processed foods, sugary drinks, and larger serving sizes in urban areas.</p>

<p><strong>Physical Inactivity:</strong> Modern jobs and transportation mean less walking and physical labor compared to previous generations.</p>

<p><strong>Age and Weight:</strong> Risk increases after age 40 and with excess body weight, particularly around the abdomen.</p>

<h2>Taking Control: Prevention and Management</h2>

<p>The good news? Type 2 diabetes is largely preventable, and even after diagnosis, it can be well-managed.</p>

<h3>Dietary Adjustments</h3>

<p>You don't have to abandon dal-bhat—in fact, traditional Nepali food can be part of a diabetes-friendly diet:</p>

<ul>
<li>Choose brown rice over white rice when possible</li>
<li>Load half your plate with vegetables</li>
<li>Include protein sources like lentils, beans, and lean meat</li>
<li>Limit deep-fried snacks and sugary beverages</li>
<li>Watch portion sizes, especially of starchy foods</li>
</ul>

<h3>Stay Active</h3>

<p>Aim for 30 minutes of moderate activity most days. In Kathmandu, this could mean:</p>

<ul>
<li>Morning walks around your neighborhood</li>
<li>Taking stairs instead of elevators</li>
<li>Joining a local gym or yoga class</li>
<li>Evening walks at nearby parks</li>
</ul>

<h3>Regular Monitoring</h3>

<p>If you have risk factors, get your blood sugar tested annually. Many pharmacies in Kathmandu, Pokhara, and other cities offer affordable testing. Fasting blood sugar above 126 mg/dL or HbA1c above 6.5% indicates diabetes.</p>

<h2>When to See a Doctor</h2>

<p>Don't wait for symptoms to become severe. Consult a healthcare provider if:</p>

<ul>
<li>You have any of the warning signs mentioned above</li>
<li>You're over 40 and haven't been tested recently</li>
<li>You have a family history of diabetes</li>
<li>You're overweight or have been diagnosed with prediabetes</li>
</ul>

<p>Early diagnosis and treatment can prevent serious complications like heart disease, kidney damage, vision loss, and nerve damage.</p>

<h2>Living Well with Diabetes</h2>

<p>A diabetes diagnosis isn't a life sentence—it's a call to action. With proper management, including medication when needed, dietary changes, regular exercise, and monitoring, people with Type 2 diabetes lead full, active lives.</p>

<p>The key is working closely with healthcare providers, staying informed, and making sustainable lifestyle changes. In Nepal's evolving healthcare landscape, support and treatment are more accessible than ever before.</p>
                """,
                'featured_image': '/static/img/type-2-diabates.jpg',
                'meta_description': 'Learn about Type 2 diabetes symptoms, risk factors, and management in Nepal. Essential guide to prevention and treatment options.',
                'meta_keywords': 'diabetes Nepal, type 2 diabetes, diabetes symptoms, diabetes prevention Kathmandu, blood sugar',
                'related_specialty_id': general.id if general else None,
                'is_published': True,
                'is_featured': True,
                'published_at': datetime.utcnow()
            },
            {
                'title': 'High Blood Pressure in Nepal: The Silent Threat You Can Control',
                'slug': 'high-blood-pressure-nepal-control',
                'category_id': bp_cat.id if bp_cat else 3,
                'summary': 'Hypertension affects 1 in 4 Nepali adults but often goes undetected. Discover how to monitor, prevent, and manage high blood pressure with practical lifestyle changes.',
                'content': """
<p>It's been called the "silent killer" for good reason. High blood pressure, or hypertension, rarely causes obvious symptoms until it has already damaged your heart, brain, or kidneys. In Nepal, where an estimated 25-30% of adults have elevated blood pressure, many don't even know they're at risk.</p>

<h2>Understanding Blood Pressure Numbers</h2>

<p>Blood pressure measures the force of blood against artery walls. It's recorded as two numbers:</p>

<ul>
<li><strong>Systolic pressure (top number):</strong> Pressure when your heart beats</li>
<li><strong>Diastolic pressure (bottom number):</strong> Pressure when your heart rests between beats</li>
</ul>

<p>Normal blood pressure is below 120/80 mmHg. You have hypertension if readings consistently show 140/90 mmHg or higher. The range between (120-139/80-89) is considered prehypertension—a warning sign.</p>

<h2>Why Blood Pressure Matters</h2>

<p>Untreated high blood pressure damages blood vessels throughout your body. Over time, this significantly increases risk of:</p>

<ul>
<li>Heart attack and heart failure</li>
<li>Stroke—a leading cause of disability in Nepal</li>
<li>Kidney disease and failure</li>
<li>Vision problems and blindness</li>
<li>Cognitive decline and dementia</li>
</ul>

<p>The troubling part? Most people feel fine even as their blood pressure silently damages vital organs.</p>

<h2>Risk Factors in Nepali Lifestyle</h2>

<p>Several factors contribute to Nepal's rising hypertension rates:</p>

<p><strong>Salt Intake:</strong> Traditional Nepali cuisine, while nutritious, often contains high sodium levels. Pickles (achar), processed snacks, and added salt in cooking contribute to elevated blood pressure.</p>

<p><strong>Stress:</strong> Urban life in cities like Kathmandu brings work pressure, traffic congestion, and financial stress—all factors that can elevate blood pressure.</p>

<p><strong>Tobacco and Alcohol:</strong> Both significantly increase hypertension risk and are common in Nepal.</p>

<p><strong>Lack of Exercise:</strong> Modern sedentary lifestyles mean less physical activity than previous generations.</p>

<p><strong>Family History:</strong> Genetics play a role—if your parents had high blood pressure, your risk increases.</p>

<h2>Taking Control: Lifestyle Changes That Work</h2>

<p>The encouraging news: lifestyle modifications can significantly lower blood pressure, sometimes eliminating the need for medication.</p>

<h3>Reduce Sodium Intake</h3>

<p>Aim for less than 5 grams (1 teaspoon) of salt daily:</p>

<ul>
<li>Use less salt when cooking dal-bhat</li>
<li>Limit pickles and processed snacks</li>
<li>Choose fresh vegetables over canned</li>
<li>Flavor food with herbs and spices instead of salt</li>
<li>Read labels on packaged foods</li>
</ul>

<h3>Increase Physical Activity</h3>

<p>Regular exercise is one of the most effective blood pressure reducers:</p>

<ul>
<li>Aim for 150 minutes per week of moderate activity</li>
<li>Morning or evening walks work well</li>
<li>Climb stairs when possible</li>
<li>Try yoga or meditation for stress reduction</li>
<li>Even household chores count as activity</li>
</ul>

<h3>Maintain Healthy Weight</h3>

<p>Losing even 5-10% of body weight can significantly lower blood pressure. Focus on:</p>

<ul>
<li>Portion control—eat until satisfied, not stuffed</li>
<li>More vegetables, less rice and roti</li>
<li>Limit deep-fried foods and sweets</li>
<li>Stay hydrated with water, not sugary drinks</li>
</ul>

<h3>Manage Stress</h3>

<p>Chronic stress contributes to high blood pressure. Try:</p>

<ul>
<li>Regular meditation or prayer</li>
<li>Adequate sleep (7-8 hours)</li>
<li>Spending time with family and friends</li>
<li>Pursuing hobbies you enjoy</li>
<li>Deep breathing exercises</li>
</ul>

<h3>Limit Alcohol and Quit Tobacco</h3>

<p>Both directly raise blood pressure. If you use tobacco, quitting is the single best thing you can do for your health. Limit alcohol to moderate amounts—or avoid it entirely.</p>

<h2>Know Your Numbers</h2>

<p>Many pharmacies in Nepal offer blood pressure checks. Get tested:</p>

<ul>
<li>Annually if you're under 40 with no risk factors</li>
<li>Every 6 months if you're over 40</li>
<li>More frequently if you have prehypertension or risk factors</li>
</ul>

<p>If diagnosed with hypertension, home blood pressure monitors are increasingly available and affordable in Kathmandu and other cities.</p>

<h2>When Medication Is Necessary</h2>

<p>Sometimes lifestyle changes aren't enough. Blood pressure medications are safe, effective, and widely available in Nepal. Common types include:</p>

<ul>
<li>Diuretics (water pills)</li>
<li>ACE inhibitors</li>
<li>Calcium channel blockers</li>
<li>Beta blockers</li>
</ul>

<p>Never stop taking prescribed medication without consulting your doctor, even if you feel fine. Uncontrolled blood pressure continues damaging your body whether you feel symptoms or not.</p>

<h2>When to Seek Medical Care</h2>

<p>See a healthcare provider immediately if you experience:</p>

<ul>
<li>Severe headache with confusion or vision changes</li>
<li>Chest pain or difficulty breathing</li>
<li>Numbness or weakness, especially on one side</li>
<li>Blood pressure readings consistently above 140/90</li>
</ul>

<p>High blood pressure is serious, but it's also manageable. With regular monitoring, healthy lifestyle choices, and medical treatment when needed, you can protect your heart, brain, and kidneys for years to come.</p>
                """,
                'featured_image': '/static/img/heart-health.jpg',
                'meta_description': 'High blood pressure affects 1 in 4 Nepalis. Learn symptoms, prevention, and management strategies for hypertension in Nepal.',
                'meta_keywords': 'blood pressure Nepal, hypertension Kathmandu, high BP, blood pressure control, heart health Nepal',
                'related_specialty_id': cardiology.id if cardiology else None,
                'is_published': True,
                'is_featured': True,
                'published_at': datetime.utcnow()
            },
            {
                'title': 'Cholesterol and Heart Health: A Guide for Nepal',
                'slug': 'cholesterol-heart-health-nepal',
                'category_id': heart_cat.id if heart_cat else 1,
                'summary': 'Understanding cholesterol levels and making heart-healthy choices within traditional Nepali diet. Practical advice for prevention and management of high cholesterol.',
                'content': """
<p>Heart disease has become a leading health concern across Nepal, and high cholesterol plays a central role. As dietary patterns shift and lifestyles become more sedentary, understanding cholesterol—and how to manage it—has never been more important.</p>

<h2>What Is Cholesterol?</h2>

<p>Cholesterol is a waxy, fat-like substance your body needs to build cells and produce hormones. Your liver makes all the cholesterol you need, but you also get it from animal-based foods.</p>

<p>There are different types:</p>

<ul>
<li><strong>LDL (Low-Density Lipoprotein):</strong> Often called "bad" cholesterol, high levels build up in arteries, forming dangerous plaques</li>
<li><strong>HDL (High-Density Lipoprotein):</strong> "Good" cholesterol that helps remove LDL from your bloodstream</li>
<li><strong>Triglycerides:</strong> Another type of fat in your blood; high levels increase heart disease risk</li>
</ul>

<h2>Understanding Your Numbers</h2>

<p>A simple blood test measures your cholesterol levels. Ideal targets:</p>

<ul>
<li><strong>Total Cholesterol:</strong> Less than 200 mg/dL</li>
<li><strong>LDL Cholesterol:</strong> Less than 100 mg/dL</li>
<li><strong>HDL Cholesterol:</strong> 60 mg/dL or higher</li>
<li><strong>Triglycerides:</strong> Less than 150 mg/dL</li>
</ul>

<p>Many medical centers in Kathmandu, Pokhara, and other cities offer lipid profile tests. Adults should get tested every 4-6 years, or more often if they have risk factors.</p>

<h2>Why High Cholesterol Is Dangerous</h2>

<p>High LDL cholesterol leads to atherosclerosis—the buildup of fatty deposits in arteries. Over years, these plaques narrow blood vessels and can rupture, causing:</p>

<ul>
<li><strong>Heart Attack:</strong> When blood flow to the heart is blocked</li>
<li><strong>Stroke:</strong> When blood flow to the brain is interrupted</li>
<li><strong>Peripheral Artery Disease:</strong> Reduced blood flow to limbs</li>
</ul>

<p>The insidious part: high cholesterol has no symptoms. You feel fine until a serious event occurs.</p>

<h2>Risk Factors in Nepal</h2>

<p>Several factors contribute to rising cholesterol levels:</p>

<p><strong>Diet Changes:</strong> Increased consumption of ghee, butter, fried foods, and processed snacks has shifted Nepal's traditional diet. While dal-bhat remains a staple, accompaniments have become richer and portions larger.</p>

<p><strong>Physical Inactivity:</strong> Modern work often involves sitting for hours, with little physical labor compared to agricultural lifestyles.</p>

<p><strong>Genetics:</strong> Family history plays a significant role. If parents or siblings have high cholesterol or early heart disease, your risk increases.</p>

<p><strong>Age and Gender:</strong> Cholesterol levels rise with age. Men face higher risk earlier in life, while women's risk increases after menopause.</p>

<p><strong>Tobacco Use:</strong> Smoking lowers good HDL cholesterol and damages blood vessel walls.</p>

<h2>Heart-Healthy Eating Within Nepali Diet</h2>

<p>You don't need to abandon traditional foods. Small adjustments make a big difference:</p>

<h3>Choose Healthy Fats</h3>

<ul>
<li>Use mustard oil or sunflower oil for cooking instead of excessive ghee</li>
<li>Limit deep-fried snacks like samosas and pakoras</li>
<li>Choose lean cuts of meat and remove visible fat</li>
<li>Include fish when available—it contains heart-healthy omega-3 fats</li>
<li>Enjoy nuts and seeds in moderation</li>
</ul>

<h3>Increase Fiber</h3>

<p>Fiber helps lower cholesterol. Traditional Nepali diet can be high in fiber if you:</p>

<ul>
<li>Fill half your plate with vegetables</li>
<li>Choose whole grain roti over white flour</li>
<li>Eat dal (lentils and beans) daily</li>
<li>Include fresh fruits</li>
<li>Consider oats for breakfast occasionally</li>
</ul>

<h3>Limit Dietary Cholesterol</h3>

<ul>
<li>Reduce red meat consumption</li>
<li>Limit egg yolks to 3-4 per week</li>
<li>Minimize organ meats</li>
<li>Use low-fat dairy when available</li>
</ul>

<h3>Avoid Trans Fats</h3>

<p>These are often found in:</p>

<ul>
<li>Packaged baked goods and snacks</li>
<li>Some margarines</li>
<li>Fried fast foods</li>
<li>Commercially baked items</li>
</ul>

<p>Check labels and avoid products listing "partially hydrogenated oil."</p>

<h2>Lifestyle Changes That Lower Cholesterol</h2>

<h3>Get Moving</h3>

<p>Regular physical activity raises good HDL cholesterol and lowers triglycerides:</p>

<ul>
<li>Aim for 30 minutes of moderate activity most days</li>
<li>Brisk walking is excellent and free</li>
<li>Climb stairs instead of using elevators</li>
<li>Try yoga for flexibility and stress reduction</li>
<li>Find activities you enjoy so you'll stick with them</li>
</ul>

<h3>Maintain Healthy Weight</h3>

<p>Losing excess weight helps lower LDL and triglycerides while raising HDL. Even 5-10% weight loss makes a difference.</p>

<h3>Quit Tobacco</h3>

<p>Quitting smoking improves HDL cholesterol levels within weeks and dramatically reduces heart disease risk.</p>

<h3>Limit Alcohol</h3>

<p>While moderate alcohol might slightly raise HDL, excessive drinking raises triglycerides and blood pressure. If you drink, do so in moderation.</p>

<h2>When Medication Is Needed</h2>

<p>Sometimes lifestyle changes aren't enough, especially with strong family history. Statins and other cholesterol-lowering medications are safe, effective, and widely available in Nepal.</p>

<p>Your doctor might recommend medication if:</p>

<ul>
<li>LDL remains high despite lifestyle changes</li>
<li>You have other risk factors like diabetes or high blood pressure</li>
<li>You have a family history of early heart disease</li>
<li>You've already had a heart attack or stroke</li>
</ul>

<p>Take medications as prescribed. They work best combined with healthy eating and exercise, not as a replacement for them.</p>

<h2>Know Your Risk, Take Action</h2>

<p>High cholesterol can be prevented and managed. Get tested regularly, especially if you have risk factors. Work with healthcare providers to create a plan that fits your lifestyle.</p>

<p>The goal isn't perfection—it's progress. Small, sustainable changes in diet and activity level can significantly improve your cholesterol profile and protect your heart for decades to come.</p>

<p>In Nepal's evolving health landscape, knowledge is power. Understanding cholesterol and taking action puts you in control of your heart health future.</p>
                """,
                'featured_image': '/static/img/cholesterol.jpg',
                'meta_description': 'Learn about cholesterol management and heart health in Nepal. Practical diet and lifestyle tips for lowering cholesterol naturally.',
                'meta_keywords': 'cholesterol Nepal, heart health Kathmandu, cholesterol diet, heart disease prevention, LDL HDL',
                'related_specialty_id': cardiology.id if cardiology else None,
                'is_published': True,
                'is_featured': True,
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
    seed_articles()
