# Quick Deployment - Start Here!

## ❓ Where Do You Want to Deploy?

### Option 1: I Have a VPS Server (DigitalOcean, AWS, Linode, etc.)
**→ Go to:** Section A below

### Option 2: I Want Easy Free Hosting
**→ Go to:** Section B below

### Option 3: I Have Shared Hosting
**→ Contact your hosting support - they'll help!**

---

## 🅰️ SECTION A: Deploy to VPS Server

### Prerequisites:
- Ubuntu/Debian server with root/sudo access
- Domain name pointing to server IP
- SSH access to server

### Super Quick Steps:

**1. Connect to your server:**
```bash
ssh user@your-server-ip
```

**2. Run this one-liner setup:**
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/ratesewa/main/deploy.sh | bash
```

**OR manually:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install requirements
sudo apt install -y python3 python3-pip python3-venv nginx git

# Create directory
sudo mkdir -p /var/www/ratesewa
cd /var/www/ratesewa

# Upload your code (use SCP or git clone)
```

**3. Set up application:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
nano .env
```

Add to .env:
```env
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
SESSION_COOKIE_SECURE=True
```

**4. Initialize database:**
```bash
python3 seed_data.py
python3 change_admin_password.py  # Change from admin123
```

**5. Start with Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**6. Set up Nginx** (see full guide: DEPLOY_TO_PRODUCTION.md)

**7. Get SSL certificate:**
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

**Done!** Visit: https://yourdomain.com

---

## 🅱️ SECTION B: Easy Free Deployment (PythonAnywhere)

**Perfect for beginners! No server management needed.**

### Step 1: Sign Up (2 minutes)
1. Go to: **https://www.pythonanywhere.com**
2. Click **"Start running Python online in less than a minute!"**
3. Create free account (no credit card needed)

### Step 2: Upload Code (5 minutes)
1. Click **"Files"** tab
2. Click **"Upload a file"**
3. Create ZIP of your project:
   ```bash
   cd /home/ppaudyal/Documents/drprofile/
   zip -r ratesewa.zip doctor_directory/
   ```
4. Upload `ratesewa.zip`
5. Open **"Bash"** console
6. Unzip:
   ```bash
   unzip ratesewa.zip
   cd doctor_directory
   ```

### Step 3: Install Dependencies (3 minutes)
```bash
mkvirtualenv ratesewa --python=/usr/bin/python3.10
pip install -r requirements.txt
```

### Step 4: Set Up Web App (5 minutes)
1. Click **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Flask"**
4. Python version: **3.10**
5. Path to Flask app: `/home/yourusername/doctor_directory/app.py`

### Step 5: Configure (3 minutes)
1. **Source code:** `/home/yourusername/doctor_directory`
2. **Working directory:** `/home/yourusername/doctor_directory`
3. **Virtualenv:** `/home/yourusername/.virtualenvs/ratesewa`
4. **Static files:**
   - URL: `/static/`
   - Directory: `/home/yourusername/doctor_directory/static`

### Step 6: Environment Variables
1. Scroll to **"Environment variables"** section
2. Add:
   ```
   SECRET_KEY = [generate random key]
   ```

### Step 7: Initialize Database
```bash
cd ~/doctor_directory
python3 seed_data.py
python3 change_admin_password.py
```

### Step 8: Reload & Launch!
1. Scroll to top of Web tab
2. Click big green **"Reload"** button
3. Visit: **yourusername.pythonanywhere.com**

**🎉 You're live!**

**Upgrade to custom domain:** $5/month for ratesewa.com

---

## ✅ Pre-Deployment Checklist

Before going live, make sure:

- [ ] Admin password changed from `admin123`
- [ ] New SECRET_KEY generated (not default)
- [ ] Database has doctors (run `seed_data.py`)
- [ ] All features tested locally
- [ ] Domain name configured (if using custom domain)
- [ ] SSL certificate ready (HTTPS)

---

## 🚀 After Deployment

### Test These:
1. **Homepage loads:** https://yoursite.com ✅
2. **Login works:** Login with admin credentials ✅
3. **Search doctors:** Filter by city/specialty ✅
4. **Doctor profile:** Click on a doctor ✅
5. **Admin panel:** Manage doctors/users ✅
6. **Mobile view:** Test on phone ✅

### Monitor:
- Check for error logs
- Watch user registrations
- Test all features
- Collect feedback

### Next Steps:
- Announce on social media
- Share with doctor communities
- Add more doctors based on demand
- Enable Facebook login (if wanted)

---

## 🆘 Quick Help

### Site won't load?
- Check DNS propagation (takes 10-60 min)
- Verify server is running: `sudo systemctl status ratesewa`
- Check Nginx: `sudo nginx -t`

### 500 Internal Server Error?
- Check logs: `sudo journalctl -u ratesewa -n 50`
- Verify .env file exists with SECRET_KEY
- Check database file permissions

### Admin can't login?
- Run: `python3 change_admin_password.py`
- Clear browser cache
- Check if user is active in database

### Need Professional Help?
- **Fiverr:** Search "deploy flask app" ($20-50)
- **Upwork:** Hire DevOps expert
- **Local:** Nepal IT freelancers on Facebook groups

---

## 💡 Recommended Path for You

**If you're comfortable with terminal:**
→ Use VPS (DigitalOcean $6/month)
→ Full control, better performance

**If you want it simple:**
→ Use PythonAnywhere (Free tier)
→ No server management, just upload & go

**If you want fastest:**
→ Hire someone on Fiverr for $20-30
→ They deploy in 1-2 hours

---

## 📞 What Information to Share (If Hiring Help)

Give them:
1. This project folder (ZIP file)
2. Your server SSH credentials (if VPS)
3. Your domain name
4. Admin email you want to use

They'll handle the rest!

---

## ✨ You're Almost There!

RateSewa is **production-ready**. Choose your deployment method and follow the steps above.

**Full detailed guide:** DEPLOY_TO_PRODUCTION.md

**Good luck! You've built something great!** 🚀

---

**Last Updated:** 2025-12-31
