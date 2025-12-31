# 🚀 Deploy RateSewa to DigitalOcean App Platform - NOW!

## ✅ Files Ready for Deployment

I've added the required files for DO App Platform:
- ✅ `runtime.txt` - Specifies Python 3.10
- ✅ `requirements.txt` - Updated with gunicorn
- ✅ `app.yaml` - DO App Platform configuration
- ✅ `.gitignore` - Properly configured

---

## Step 1: Generate SECRET_KEY (2 minutes)

Run this command to generate a secure secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Copy the output** - you'll need it in Step 4!

---

## Step 2: Push Code to GitHub (3 minutes)

```bash
cd /home/ppaudyal/Documents/drprofile/doctor_directory

# Check current status
git status

# Add all files
git add .

# Commit
git commit -m "Ready for DigitalOcean App Platform deployment"

# Push to your repo
git push origin main
```

If you haven't set up the remote yet:
```bash
git remote add origin git@github.com:Prasan1/ratesewa.git
git branch -M main
git push -u origin main
```

---

## Step 3: Create App in DigitalOcean (5 minutes)

### 3.1 Create New App

1. Go to **https://cloud.digitalocean.com/apps**
2. Click **"Create App"** button
3. Choose **"GitHub"** as source
4. If prompted, click **"Manage Access"** and authorize DO to access your repos
5. Select repository: **Prasan1/ratesewa**
6. Select branch: **main**
7. Check **"Autodeploy"** (deploys automatically on push)
8. Click **"Next"**

### 3.2 Configure Resources

DO should auto-detect your app from `app.yaml`. Verify:

**Web Service:**
- Name: `web`
- Environment: `Python`
- Build Command: `pip install -r requirements.txt`
- Run Command: `gunicorn --worker-tmp-dir /dev/shm --workers 2 --bind 0.0.0.0:8080 app:app`
- HTTP Port: `8080`

Click **"Next"**

### 3.3 Set Environment Variables

**CRITICAL:** Update these environment variables:

Click **"Edit"** next to environment variables and set:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | **Paste the key you generated in Step 1** |
| `SESSION_COOKIE_SECURE` | `True` |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///doctors.db` |

Click **"Save"**

### 3.4 Choose Plan

- **Name**: `ratesewa`
- **Region**: Singapore (sgp) or nearest to Nepal
- **Plan**: Basic ($5/month) or Pro ($12/month)
  - Basic is fine for MVP
  - Can upgrade later

Click **"Next"**

### 3.5 Review & Launch

Review all settings and click **"Create Resources"**

---

## Step 4: Wait for Deployment (3-5 minutes)

DO will now:
1. ✅ Clone your GitHub repo
2. ✅ Install dependencies
3. ✅ Build your app
4. ✅ Deploy it
5. ✅ Provide HTTPS URL

Watch the **build logs** in real-time. You'll see:
```
=====> Building web
=====> Installing dependencies from requirements.txt
=====> Collecting Flask==3.1.2
...
=====> Build successful!
=====> Deploying...
=====> Deployment successful!
```

---

## Step 5: Initialize Database (5 minutes)

⚠️ **Important:** After first deployment, you need to seed the database.

### 5.1 Access Console

1. In DO dashboard, go to your **ratesewa** app
2. Click **"Console"** tab
3. Click **"Run Console"**
4. Wait for terminal to load

### 5.2 Seed Database

In the console, run:

```bash
python3 seed_data.py
```

You should see:
```
✅ Database seeded successfully!
✅ Added 29 doctors across 12 cities
```

### 5.3 Change Admin Password

Still in console, run:

```bash
python3 change_admin_password.py
```

Follow prompts:
- Enter new password (at least 6 characters)
- Confirm password

You should see:
```
✅ Admin password changed successfully!
```

---

## Step 6: Test Your Live App! (5 minutes)

### 6.1 Get Your URL

In DO dashboard, you'll see your app URL:
```
https://ratesewa-xxxxx.ondigitalocean.app
```

### 6.2 Test Features

Visit your URL and test:

1. **Homepage loads** ✅
   - Should show "Find & Rate the Best Doctors in Nepal"

2. **Search works** ✅
   - Filter by city (Kathmandu, Pokhara, etc.)
   - Filter by specialty

3. **Doctor profiles** ✅
   - Click on a doctor
   - See full details

4. **Login** ✅
   - Email: `admin@ratesewa.com`
   - Password: [the one you just set]

5. **Admin panel** ✅
   - Click your username dropdown → Admin
   - Manage Doctors, Cities, Specialties, Users

---

## Step 7: Add Custom Domain (Optional - 10 minutes)

If you have a domain (like ratesewa.com):

### 7.1 Add Domain in DO

1. In your app settings, go to **"Settings"** → **"Domains"**
2. Click **"Add Domain"**
3. Enter: `ratesewa.com`
4. DO will show DNS records to add

### 7.2 Update DNS

In your domain registrar (Namecheap, GoDaddy, etc.):

**Add CNAME record:**
```
Type: CNAME
Name: @
Value: [value provided by DO]
TTL: 3600
```

**Add CNAME for www:**
```
Type: CNAME
Name: www
Value: [value provided by DO]
TTL: 3600
```

### 7.3 Wait for SSL

- DNS propagation: 10-60 minutes
- SSL certificate: Automatic (DO provides free SSL)
- Your site will be live at: `https://ratesewa.com`

---

## 🎉 You're Live!

### What You Have Now:

✅ **Live app**: https://ratesewa-xxxxx.ondigitalocean.app (or your custom domain)
✅ **29 doctors** searchable across Nepal
✅ **User registration** and login
✅ **Doctor ratings** and reviews
✅ **Admin panel** for management
✅ **HTTPS enabled** (secure)
✅ **Auto-deploy** on git push

---

## 📊 Monitor Your App

### View Logs

1. Go to your app in DO dashboard
2. Click **"Runtime Logs"**
3. See real-time application activity

### View Metrics

Monitor:
- Request count
- Response time
- Memory usage
- CPU usage

---

## 🔄 Update Your App

Making changes is easy:

```bash
cd /home/ppaudyal/Documents/drprofile/doctor_directory

# Make your changes to code
# Then:

git add .
git commit -m "Your update description"
git push origin main

# DO automatically redeploys! ✨
```

Watch deployment in DO dashboard. Takes 2-3 minutes.

---

## ⚠️ Important Notes

### Database Limitation (SQLite)

**Current setup uses SQLite:**
- ✅ Works for MVP/testing
- ⚠️ **Data is lost on redeploy!**
- You'll need to re-seed after each deployment

**To keep data permanently:**

1. **Create PostgreSQL Database** in DO:
   - Apps → Databases → Create
   - Choose PostgreSQL
   - Smallest size ($15/month)

2. **Update environment variable**:
   - Get connection string from database
   - Update `SQLALCHEMY_DATABASE_URI` to PostgreSQL string
   - Format: `postgresql://user:password@host:port/database?sslmode=require`

3. **Add to requirements.txt**:
   ```
   psycopg2-binary==2.9.9
   ```

4. **Push changes** - app will auto-migrate!

---

## 🐛 Troubleshooting

### Build Failed?

Check build logs for errors:
- Missing dependencies?
- Syntax errors?
- Python version mismatch?

### App Won't Start?

Check runtime logs for:
- Missing environment variables
- Database connection errors
- Port binding issues

### Database Empty?

- Re-run `python3 seed_data.py` in console
- Consider upgrading to PostgreSQL

---

## ✅ Quick Checklist

- [ ] SECRET_KEY generated
- [ ] Code pushed to GitHub
- [ ] App created in DO
- [ ] Environment variables set
- [ ] App deployed successfully
- [ ] Database seeded
- [ ] Admin password changed
- [ ] Tested login
- [ ] Tested search/filtering
- [ ] Tested admin panel
- [ ] (Optional) Custom domain added

---

## 💰 Cost Summary

**Minimum (MVP):**
- App Platform Basic: **$5/month**
- Total: **$5/month**

**Recommended (Production):**
- App Platform Basic: **$5/month**
- PostgreSQL Database: **$15/month**
- Total: **$20/month**

**Can upgrade to:**
- App Platform Pro: $12/month (better performance)
- Larger database: $30+/month

---

## 🚀 Ready to Deploy?

**Your next command:**

```bash
cd /home/ppaudyal/Documents/drprofile/doctor_directory
git add .
git commit -m "Ready for DigitalOcean App Platform deployment"
git push origin main
```

Then follow Step 3 above to create your app in DigitalOcean!

---

**Good luck with your launch! 🎉**

**After deployment, your app will be live at:**
`https://ratesewa-xxxxx.ondigitalocean.app`

---

**Last Updated:** 2025-12-31
