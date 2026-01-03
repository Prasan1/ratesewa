# Google SEO Setup Guide

## ✅ What We Just Implemented:

### 1. **Doctor Profile SEO Meta Tags**
Every doctor profile now has:
- **SEO-optimized title**: "Dr. Ram Sharma - Cardiology in Kathmandu, Nepal | RankSewa"
- **Meta description**: Includes specialty, experience, ratings, workplace
- **Keywords**: Doctor name, specialty, city, Nepal-specific terms
- **Schema.org markup**: Tells Google this is a doctor profile with structured data

**Result:** When someone Googles "cardiologist in Kathmandu", your doctors can appear!

### 2. **XML Sitemap**
- URL: https://ranksewa.com/sitemap.xml
- Lists ALL doctor profiles, articles, and main pages
- Tells Google what to index
- Updates automatically as you add doctors

### 3. **Robots.txt**
- URL: https://ranksewa.com/robots.txt
- Tells search engines what they can/cannot crawl
- Points to sitemap
- Blocks admin pages from Google

---

## 🚀 Next Steps: Submit to Google

### Step 1: Google Search Console Setup (5 minutes)

1. **Go to:** https://search.google.com/search-console

2. **Add Property:**
   - Click "Add Property"
   - Enter: `ranksewa.com`
   - Select "URL prefix"

3. **Verify Ownership** (Choose ONE method):

   **Option A: DNS Verification** (Recommended - Permanent)
   - Google gives you a TXT record
   - Add to your domain DNS settings
   - Example: `google-site-verification=abcd1234...`
   - Wait 5 minutes, click Verify

   **Option B: HTML File Upload**
   - Download verification file from Google
   - Upload to: `/home/ppaudyal/Documents/drprofile/doctor_directory/static/`
   - Access at: `https://ranksewa.com/static/google<hash>.html`
   - Click Verify

   **Option C: HTML Tag** (Easiest for now)
   - Copy meta tag from Google
   - Add to `templates/base.html` in `<head>` section:
   ```html
   <meta name="google-site-verification" content="YOUR_CODE_HERE">
   ```
   - Deploy changes
   - Click Verify

### Step 2: Submit Sitemap (2 minutes)

1. In Google Search Console, go to **Sitemaps** (left sidebar)

2. Enter sitemap URL: `https://ranksewa.com/sitemap.xml`

3. Click **Submit**

4. **Expected Result:**
   ```
   Sitemap submitted successfully
   Discovered URLs: 200+
   ```

### Step 3: Request Indexing for Key Pages (5 minutes)

Manually request indexing for important pages:

1. Go to **URL Inspection** tool

2. Enter these URLs one by one:
   ```
   https://ranksewa.com/
   https://ranksewa.com/doctors
   https://ranksewa.com/health-digest
   https://ranksewa.com/doctors/dr-ram-sharma-kathmandu (example doctor)
   ```

3. Click **Request Indexing** for each

4. Google will crawl within 24-48 hours

---

## 📊 What to Monitor (After 1 Week):

### In Google Search Console:

1. **Performance Report:**
   - How many clicks from Google?
   - What keywords are people searching?
   - Which doctors are ranking?

2. **Coverage Report:**
   - How many pages indexed?
   - Target: All active doctor profiles

3. **Experience Report:**
   - Page speed (should be "Good")
   - Mobile usability (should be "Good")

### Expected Timeline:

- **Day 1-2:** Google discovers sitemap
- **Day 3-7:** Starts indexing doctor profiles
- **Week 2:** First impressions in Google search
- **Week 3-4:** Profiles start appearing in results
- **Month 2:** Organic traffic from Google

---

## 🎯 SEO Best Practices (Ongoing):

### For Each New Doctor Added:

1. **Complete profile data:**
   - Name, specialty, city (required)
   - Experience years
   - Education
   - Workplace
   - Phone number

2. **Encourage reviews:**
   - Google favors profiles with ratings
   - More reviews = better ranking

3. **Keep profiles updated:**
   - Current workplace
   - Accurate phone number
   - Fresh profile photo

### For Articles:

1. **Use Nepal-specific keywords:**
   - "Air pollution in Kathmandu"
   - "Dengue in Nepal monsoon"
   - NOT generic "air pollution"

2. **Update regularly:**
   - Google likes fresh content
   - Update statistics yearly

3. **Internal linking:**
   - Link articles to relevant doctor profiles
   - "Consult a cardiologist in Kathmandu →"

---

## 🔍 How to Check if SEO is Working:

### Test 1: Manual Google Search

Wait 2-3 weeks, then Google:
```
"cardiologist in Kathmandu"
"pediatrician Pokhara"
"Dr. [specific doctor name]"
```

Your doctors should start appearing!

### Test 2: Site Search

In Google, search:
```
site:ranksewa.com
```

Should show all indexed pages.

### Test 3: Rich Results Test

1. Go to: https://search.google.com/test/rich-results
2. Enter doctor profile URL
3. Should detect "Physician" schema
4. Shows rating stars in search results!

---

## 📈 Expected SEO Impact:

### Month 1:
- 10-20 doctor profiles indexed
- 5-10 organic visits from Google

### Month 2:
- 50+ profiles indexed
- 50-100 organic visits
- Start ranking for "[specialty] in [city]"

### Month 3:
- Most profiles indexed
- 200-500 organic visits
- Top 10 for several search terms

### Month 6:
- **1,000+ organic visits per month**
- **Major patient acquisition channel**
- **Doctors see Google traffic in analytics**

---

## ⚡ Quick Wins (Do These Now):

### 1. Add Google Verification Tag

**File:** `templates/base.html`

Add in `<head>` section (get code from Google Search Console):
```html
<meta name="google-site-verification" content="YOUR_CODE_HERE">
```

### 2. Test Sitemap Locally

```bash
curl http://localhost:5000/sitemap.xml
```

Should see XML with all doctor URLs.

### 3. Test Doctor Profile SEO

Visit any doctor profile and "View Page Source". Look for:
- ✅ `<title>` with specialty + city + Nepal
- ✅ Meta description with ratings
- ✅ Schema.org JSON-LD script
- ✅ Keywords meta tag

---

## 🎁 Bonus: Local SEO

To appear in Google Maps/Local results:

### 1. Google Business Profile (For Each Clinic)

If doctor has a clinic:
1. Create Google Business Profile
2. Add clinic address
3. Link to RankSewa profile
4. Request reviews on Google

### 2. NAP Consistency

Ensure Name, Address, Phone are identical across:
- RankSewa profile
- Google Business Profile
- Clinic website
- Social media

---

## ❓ Troubleshooting:

**Q: Sitemap returns 500 error**
- Check: `python` doesn't crash on `from models import Doctor`
- Run locally first to test

**Q: Google not indexing profiles**
- Check robots.txt allows Googlebot
- Request manual indexing for key pages
- Wait 2-3 weeks (patience!)

**Q: Doctor profiles don't appear in search**
- Need time (3-4 weeks minimum)
- Need backlinks (share profiles on social media)
- Need reviews (encourage patients)

**Q: Schema validation errors**
- Go to: https://search.google.com/test/rich-results
- Fix any errors shown
- Usually just missing commas in JSON

---

## ✅ Deployment Checklist:

After deploying these changes:

- [ ] Visit https://ranksewa.com/sitemap.xml (should work)
- [ ] Visit https://ranksewa.com/robots.txt (should work)
- [ ] View source of doctor profile (has schema markup)
- [ ] Set up Google Search Console
- [ ] Submit sitemap to Google
- [ ] Request indexing for homepage
- [ ] Request indexing for 5-10 doctor profiles
- [ ] Check back in 1 week

---

## 🚀 Marketing Hook for Doctors:

Once SEO is working, tell doctors:

> **"Your profile appeared in Google search 89 times last month!**
> 12 patients clicked through to view your profile.
> Claim it to see your full Google analytics."

This is POWERFUL motivation to join!

---

You're now set up for Google! 🎉

Next up: Deploy and submit to Google Search Console!
