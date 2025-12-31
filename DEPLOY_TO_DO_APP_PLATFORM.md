# Deploy RateSewa to DigitalOcean App Platform

## Quick Deployment for DO App Platform

Perfect choice! App Platform handles all the infrastructure for you.

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub

Your code needs to be in a GitHub repository for DO App Platform to access it.

```bash
cd /home/ppaudyal/Documents/drprofile/doctor_directory

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial RateSewa deployment"

# Create repo on GitHub, then push
git remote add origin https://github.com/yourusername/ratesewa.git
git branch -M main
git push -u origin main
```

---

### Step 2: Create App in DigitalOcean

1. Go to **DigitalOcean Dashboard**
2. Click **Apps** in left sidebar
3. Click **"Create App"**
4. Choose **GitHub** as source
5. Authorize DigitalOcean to access your GitHub
6. Select your **ratesewa** repository
7. Select **main** branch
8. Click **"Next"**

---

### Step 3: Configure App Settings

#### **Resources Configuration:**

When it asks to configure resources:

**Web Service:**
- **Name**: `ratesewa-web`
- **Environment**: `Python`
- **Build Command**:
  ```
  pip install -r requirements.txt
  ```
- **Run Command**:
  ```
  gunicorn --worker-tmp-dir /dev/shm --workers 2 --bind 0.0.0.0:8080 app:app
  ```
- **HTTP Port**: `8080`

---

### Step 4: Set Environment Variables

In the **Environment Variables** section, add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate with: `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `SESSION_COOKIE_SECURE` | `True` |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///doctors.db` |

**To generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and paste as the value.

---

### Step 5: Configure App Specs

**App Tier:**
- Choose **Basic** ($5/month) or **Pro** ($12/month)
- Basic is fine for MVP launch

**Region:**
- Choose closest to Nepal (likely Singapore or Bangalore)

**Domain:**
- You can use DO's free subdomain: `ratesewa-xxxxx.ondigitalocean.app`
- Or add your custom domain later

---

### Step 6: Add Required Files to Your Repo

DigitalOcean App Platform needs a few specific files. Let me create them:

#### Create `runtime.txt`:
```bash
cd /home/ppaudyal/Documents/drprofile/doctor_directory
echo "python-3.10" > runtime.txt
git add runtime.txt
```

#### Update `requirements.txt`:
Make sure it includes gunicorn:
```bash
echo "gunicorn==21.2.0" >> requirements.txt
git add requirements.txt
```

#### Create `app.yaml` (App Platform Spec):
This file tells DO exactly how to deploy your app.

```yaml
name: ratesewa
region: sgp
services:
  - name: web
    environment_slug: python
    github:
      branch: main
      deploy_on_push: true
      repo: yourusername/ratesewa
    build_command: pip install -r requirements.txt
    run_command: gunicorn --worker-tmp-dir /dev/shm --workers 2 --bind 0.0.0.0:8080 app:app
    http_port: 8080
    instance_count: 1
    instance_size_slug: basic-xxs
    routes:
      - path: /
    envs:
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
      - key: SESSION_COOKIE_SECURE
        value: "True"
      - key: SQLALCHEMY_DATABASE_URI
        value: "sqlite:///doctors.db"
```

---

### Step 7: Initialize Database After First Deploy

⚠️ **Important**: SQLite on App Platform has limitations - data will be lost on redeploy!

**For MVP/Testing:**
SQLite works fine, but you'll need to re-seed after each deploy.

**For Production (Recommended):**
Use DigitalOcean Managed Database (PostgreSQL):

1. In App Platform, click **"Create"** → **"Database"**
2. Choose **PostgreSQL**
3. DO will provide connection string
4. Update environment variable `SQLALCHEMY_DATABASE_URI` with the provided string

**If sticking with SQLite for now:**

After first deploy, you need to seed the database. Since App Platform is managed, you'll use the console:

1. Go to your app in DO dashboard
2. Click **"Console"** tab
3. Run:
   ```bash
   python3 seed_data.py
   python3 change_admin_password.py
   ```

---

### Step 8: Deploy!

1. Click **"Next"** to review settings
2. Click **"Create Resources"**
3. DO will build and deploy your app (takes 3-5 minutes)
4. Watch the build logs

---

### Step 9: Access Your App

Once deployed:

1. You'll get a URL like: `https://ratesewa-xxxxx.ondigitalocean.app`
2. Visit the URL
3. Login with your admin credentials
4. Test the application

---

## 🔧 Post-Deployment Configuration

### Add Custom Domain:

1. Go to **Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain: `ratesewa.com`
4. DO will provide DNS records to add
5. Add DNS records to your domain registrar:
   ```
   Type: CNAME
   Name: @
   Value: [provided by DO]
   ```
6. SSL certificate is automatic!

---

## 📦 Database Recommendations

### Option 1: SQLite (Current - Simple but Limited)
**Pros:**
- No additional cost
- Simple setup
- Works for MVP

**Cons:**
- ⚠️ Data lost on redeploy
- ⚠️ Not suitable for production
- ⚠️ No concurrent writes

**Use for:** Testing, MVP demo

### Option 2: PostgreSQL (Recommended for Production)
**Pros:**
- ✅ Data persists across deploys
- ✅ Better performance
- ✅ Production-ready
- ✅ Automatic backups

**Cons:**
- 💰 Costs $15/month for managed DB

**To migrate to PostgreSQL:**

1. **Create Database:**
   - In DO dashboard: **Databases** → **Create**
   - Choose **PostgreSQL**
   - Choose smallest size ($15/month)

2. **Update requirements.txt:**
   ```
   psycopg2-binary==2.9.9
   ```

3. **Update Environment Variable:**
   - Get connection string from DO database dashboard
   - Update `SQLALCHEMY_DATABASE_URI` to PostgreSQL connection string
   - Format: `postgresql://user:password@host:port/database?sslmode=require`

4. **Redeploy** - App Platform will automatically migrate

---

## 🔄 Update Your App

### Method 1: Auto-Deploy (Recommended)

Just push to GitHub:
```bash
cd /home/ppaudyal/Documents/drprofile/doctor_directory

# Make changes, then:
git add .
git commit -m "Update description"
git push origin main
```

DO App Platform automatically redeploys on push! ✨

### Method 2: Manual Deploy

In DO dashboard:
1. Go to your app
2. Click **"Create Deployment"**
3. Choose branch
4. Deploy

---

## 📊 Monitor Your App

### View Logs:
1. Go to your app in DO dashboard
2. Click **"Runtime Logs"**
3. See real-time application logs

### View Metrics:
- CPU usage
- Memory usage
- Request count
- Response times

### Alerts:
Set up alerts for downtime or errors in Settings.

---

## 💰 Pricing

**Basic Plan** ($5/month):
- 512 MB RAM
- Perfect for MVP with moderate traffic
- Includes SSL certificate

**Pro Plan** ($12/month):
- 1 GB RAM
- Better for production
- More concurrent connections

**Database** (Optional but recommended):
- PostgreSQL: $15/month
- Includes automatic backups

**Total recommended cost:** $20/month (Basic app + PostgreSQL)

---

## 🐛 Troubleshooting

### Build Failed:
1. Check **Build Logs** in DO dashboard
2. Common issues:
   - Missing dependencies in requirements.txt
   - Python version mismatch
   - Syntax errors

### App Crashes on Start:
1. Check **Runtime Logs**
2. Common issues:
   - Missing environment variables
   - Database connection errors
   - Port binding issues (must use 8080)

### Database Empty After Redeploy:
- This happens with SQLite
- Solution: Migrate to PostgreSQL or re-seed after each deploy

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] App created in DO App Platform
- [ ] Build and run commands configured
- [ ] Environment variables set (SECRET_KEY, etc.)
- [ ] First deployment successful
- [ ] Database seeded (run seed_data.py)
- [ ] Admin password changed
- [ ] Custom domain added (if using)
- [ ] SSL working (automatic with DO)
- [ ] Tested all features

---

## 🎯 Quick Commands Reference

### Local Development:
```bash
# Run locally
cd /home/ppaudyal/Documents/drprofile/doctor_directory
source venv/bin/activate
python3 app.py

# Generate new secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Seed database
python3 seed_data.py

# Change admin password
python3 change_admin_password.py
```

### Deploy Updates:
```bash
git add .
git commit -m "Your update message"
git push origin main
# DO automatically redeploys!
```

---

## 📞 Important Files for DO App Platform

Your repository should have:
- ✅ `app.py` (main Flask app)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `runtime.txt` (Python version) - **ADD THIS**
- ✅ `.gitignore` (exclude venv, *.pyc, .env)
- ✅ `seed_data.py` (database seeding)
- ✅ All templates and static files

**Don't commit:**
- ❌ `.env` file (use environment variables in DO dashboard)
- ❌ `venv/` folder
- ❌ `*.pyc` files
- ❌ `instance/doctors.db` (will be created on server)

---

## 🚀 You're Ready!

App Platform makes deployment super easy:
1. Push to GitHub
2. Configure in DO dashboard
3. Deploy automatically
4. SSL included
5. Automatic scaling

**Next step:** Push your code to GitHub and create the app!

---

**Last Updated:** 2025-12-31
**Platform:** DigitalOcean App Platform
