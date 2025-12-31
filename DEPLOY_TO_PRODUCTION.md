# RateSewa - Production Deployment Guide

## 🚀 Ready to Launch!

Let's get RateSewa live on your production server.

---

## ✅ Pre-Deployment Checklist

### Critical (Must Do):
- [ ] Admin password changed from `admin123`
- [ ] SECRET_KEY is secure (not the default)
- [ ] Server has Python 3.8+ installed
- [ ] Domain name configured (DNS pointing to server)

### Important (Should Do):
- [ ] SSL certificate ready (HTTPS)
- [ ] Database backup plan
- [ ] Server has enough resources (2GB RAM minimum)

### Optional (Can Do Later):
- [ ] Logo added (or keep temporary)
- [ ] Facebook login configured
- [ ] Email service configured

---

## 📋 Deployment Methods

### Option 1: Simple VPS Deployment (Recommended)

**Works on:**
- DigitalOcean Droplet
- AWS EC2
- Linode
- Vultr
- Any Ubuntu/Debian VPS

### Option 2: Shared Hosting

**Works on:**
- PythonAnywhere
- Heroku
- Render.com

---

## 🖥️ Method 1: VPS Deployment (Most Common)

### Step 1: Prepare Your Server

**Connect to server:**
```bash
ssh user@your-server-ip
```

**Update system:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Install requirements:**
```bash
sudo apt install -y python3 python3-pip python3-venv nginx git
```

---

### Step 2: Upload Your Project

**Option A - Using Git (Recommended):**
```bash
# On your local machine, push to GitHub
cd /home/ppaudyal/Documents/drprofile/doctor_directory
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/ratesewa.git
git push -u origin main

# On server, clone
cd /var/www/
sudo git clone https://github.com/yourusername/ratesewa.git
cd ratesewa
```

**Option B - Using SCP:**
```bash
# On your local machine
cd /home/ppaudyal/Documents/drprofile/
tar -czf doctor_directory.tar.gz doctor_directory/
scp doctor_directory.tar.gz user@your-server-ip:/tmp/

# On server
cd /var/www/
sudo tar -xzf /tmp/doctor_directory.tar.gz
sudo mv doctor_directory ratesewa
cd ratesewa
```

---

### Step 3: Set Up Application

**Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
pip install gunicorn  # Production server
```

**Set up environment variables:**
```bash
nano .env
```

Add:
```env
SECRET_KEY=your_new_secure_random_key_here_make_it_long_and_random
SQLALCHEMY_DATABASE_URI=sqlite:///doctors.db
SESSION_COOKIE_SECURE=True

# Optional - Add if using Facebook login
# FACEBOOK_CLIENT_ID=your_facebook_app_id
# FACEBOOK_CLIENT_SECRET=your_facebook_app_secret
```

**Generate new SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and use it as SECRET_KEY in .env

**Initialize database:**
```bash
python3 seed_data.py
```

---

### Step 4: Configure Gunicorn

**Create Gunicorn config:**
```bash
sudo nano /etc/systemd/system/ratesewa.service
```

**Add:**
```ini
[Unit]
Description=RateSewa Gunicorn Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ratesewa
Environment="PATH=/var/www/ratesewa/venv/bin"
ExecStart=/var/www/ratesewa/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

**Set permissions:**
```bash
sudo chown -R www-data:www-data /var/www/ratesewa
sudo chmod -R 755 /var/www/ratesewa
```

**Start Gunicorn:**
```bash
sudo systemctl start ratesewa
sudo systemctl enable ratesewa
sudo systemctl status ratesewa
```

---

### Step 5: Configure Nginx

**Create Nginx config:**
```bash
sudo nano /etc/nginx/sites-available/ratesewa
```

**Add:**
```nginx
server {
    listen 80;
    server_name ratesewa.com www.ratesewa.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/ratesewa/static;
        expires 30d;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/ratesewa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Step 6: Set Up SSL (HTTPS)

**Install Certbot:**
```bash
sudo apt install -y certbot python3-certbot-nginx
```

**Get SSL certificate:**
```bash
sudo certbot --nginx -d ratesewa.com -d www.ratesewa.com
```

**Follow prompts:**
- Enter email address
- Agree to terms
- Choose "Redirect HTTP to HTTPS"

**Test auto-renewal:**
```bash
sudo certbot renew --dry-run
```

---

## 🎯 Method 2: Quick Deploy with PythonAnywhere

**Easier for beginners, free tier available!**

### Step 1: Sign Up
1. Go to: https://www.pythonanywhere.com
2. Create free account

### Step 2: Upload Code
1. Click "Files" tab
2. Upload your project ZIP file
3. Or use git clone

### Step 3: Set Up Web App
1. Click "Web" tab
2. "Add a new web app"
3. Choose "Flask"
4. Python 3.10
5. Path: `/home/yourusername/ratesewa/app.py`

### Step 4: Configure
1. Virtual environment: `/home/yourusername/ratesewa/venv`
2. Static files: `/static/` → `/home/yourusername/ratesewa/static/`
3. Reload web app

### Step 5: Go Live!
- Your site: `yourusername.pythonanywhere.com`
- Or use custom domain (paid plan)

---

## 🔒 Post-Deployment Security

### 1. Change Default Passwords
```bash
# On server, run:
cd /var/www/ratesewa
source venv/bin/activate
python3 change_admin_password.py
```

### 2. Set Up Firewall
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 3. Regular Backups
```bash
# Create backup script
sudo nano /usr/local/bin/backup-ratesewa.sh
```

**Add:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/ratesewa"
mkdir -p $BACKUP_DIR
cp /var/www/ratesewa/instance/doctors.db $BACKUP_DIR/doctors_$DATE.db
find $BACKUP_DIR -name "doctors_*.db" -mtime +7 -delete
```

**Make executable and schedule:**
```bash
sudo chmod +x /usr/local/bin/backup-ratesewa.sh
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-ratesewa.sh
```

---

## 📊 Monitoring & Maintenance

### Check Application Status
```bash
sudo systemctl status ratesewa
```

### View Logs
```bash
sudo journalctl -u ratesewa -f
```

### Restart Application
```bash
sudo systemctl restart ratesewa
```

### Update Application
```bash
cd /var/www/ratesewa
git pull origin main
sudo systemctl restart ratesewa
```

---

## 🐛 Troubleshooting

### Application Won't Start
```bash
# Check logs
sudo journalctl -u ratesewa -n 50

# Check syntax
cd /var/www/ratesewa
source venv/bin/activate
python3 app.py
```

### 502 Bad Gateway
```bash
# Check Gunicorn is running
sudo systemctl status ratesewa

# Check Nginx config
sudo nginx -t
```

### Database Errors
```bash
# Recreate database
cd /var/www/ratesewa
source venv/bin/activate
python3 seed_data.py
```

### Permission Errors
```bash
sudo chown -R www-data:www-data /var/www/ratesewa
sudo chmod -R 755 /var/www/ratesewa
```

---

## 🎯 Quick Deployment Checklist

### Before Deployment:
- [ ] Code tested locally
- [ ] Admin password changed
- [ ] SECRET_KEY generated
- [ ] Database seeded with data
- [ ] Logo added (or using temporary)

### On Server:
- [ ] Python 3.8+ installed
- [ ] Project uploaded
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Gunicorn configured
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] Firewall configured

### After Deployment:
- [ ] Test website loads (http://your-domain.com)
- [ ] Test login works
- [ ] Test doctor search
- [ ] Test admin panel
- [ ] Set up backups
- [ ] Monitor logs for errors

---

## 📱 Domain Configuration

### Update DNS Records:

**A Record:**
```
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 3600
```

**CNAME Record:**
```
Type: CNAME
Name: www
Value: @
TTL: 3600
```

**Wait 10-60 minutes for DNS propagation**

---

## 🚀 Alternative: One-Click Deploy

### Render.com (Free Tier Available)

1. **Push to GitHub**
2. **Go to:** https://render.com
3. **New** → **Web Service**
4. **Connect GitHub repo**
5. **Settings:**
   - Name: ratesewa
   - Environment: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
6. **Add Environment Variables** (SECRET_KEY, etc.)
7. **Deploy!**

---

## 💰 Hosting Recommendations

### Free Tier:
- **PythonAnywhere** (Free tier, easy)
- **Render.com** (Free tier, modern)
- **Railway.app** (Free tier, simple)

### Budget ($5-10/month):
- **DigitalOcean** ($6/month droplet)
- **Linode** ($5/month)
- **Vultr** ($5/month)

### Nepal-Based:
- **Websual** (Local support)
- **Nest Nepal** (Local hosting)
- **Mercantile** (Nepal servers)

---

## ✅ Final Checklist

- [ ] Server ready
- [ ] Code deployed
- [ ] Application running
- [ ] SSL configured (HTTPS working)
- [ ] Domain pointing to server
- [ ] Website loads: https://ratesewa.com ✨
- [ ] Admin panel accessible
- [ ] Users can register/login
- [ ] Doctors searchable
- [ ] Backups configured

---

## 🎉 Launch Day!

**When everything is ready:**

1. **Announce launch** on social media
2. **Test all features** one more time
3. **Monitor logs** for first few hours
4. **Collect user feedback**
5. **Plan next updates**

---

**Status:** Ready to deploy! Choose your method and follow the steps above.

**Need Help?** Follow this guide step-by-step or hire a DevOps expert on Fiverr ($20-50 for deployment help).

**Last Updated:** 2025-12-31

---

🚀 **GOOD LUCK WITH YOUR LAUNCH!** 🚀
