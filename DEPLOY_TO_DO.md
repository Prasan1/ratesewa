# Deploy RateSewa to Your Existing DigitalOcean Droplet

## Quick Deployment for Existing DO Server

Since you already have apps running on DO, you're familiar with the process. Here's a streamlined guide for RateSewa.

---

## 🚀 Deployment Steps

### Step 1: Package Your App Locally

```bash
# Create tarball of your application
cd /home/ppaudyal/Documents/drprofile/
tar -czf ratesewa.tar.gz doctor_directory/

# Transfer to your DO server
scp ratesewa.tar.gz your-user@your-server-ip:/tmp/
```

**Or use Git** (if you have a repo):
```bash
# On local machine
cd /home/ppaudyal/Documents/drprofile/doctor_directory
git init
git add .
git commit -m "Initial RateSewa deployment"
git remote add origin https://github.com/yourusername/ratesewa.git
git push -u origin main
```

---

### Step 2: Extract on Server

```bash
# SSH to your DO server
ssh your-user@your-server-ip

# Create directory for RateSewa
sudo mkdir -p /var/www/ratesewa
cd /var/www/

# Extract uploaded file
sudo tar -xzf /tmp/ratesewa.tar.gz
sudo mv doctor_directory ratesewa

# Or if using git
cd /var/www/
sudo git clone https://github.com/yourusername/ratesewa.git
```

---

### Step 3: Set Up Virtual Environment

```bash
cd /var/www/ratesewa

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

---

### Step 4: Create Environment Variables

```bash
cd /var/www/ratesewa
nano .env
```

**Add to .env:**
```env
SECRET_KEY=your_generated_secret_key_here
SQLALCHEMY_DATABASE_URI=sqlite:///doctors.db
SESSION_COOKIE_SECURE=True
```

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and paste it as SECRET_KEY in .env file.

---

### Step 5: Initialize Database

```bash
cd /var/www/ratesewa
source venv/bin/activate

# Seed database with 29 doctors
python3 seed_data.py

# Change admin password from admin123
python3 change_admin_password.py
```

**Default admin credentials** (before password change):
- Email: `admin@ratesewa.com`
- Password: `admin123`

---

### Step 6: Set Permissions

```bash
sudo chown -R www-data:www-data /var/www/ratesewa
sudo chmod -R 755 /var/www/ratesewa

# Make sure database directory is writable
sudo chmod 775 /var/www/ratesewa/instance
```

---

### Step 7: Create Systemd Service

```bash
sudo nano /etc/systemd/system/ratesewa.service
```

**Add this configuration:**
```ini
[Unit]
Description=RateSewa Doctor Directory Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ratesewa
Environment="PATH=/var/www/ratesewa/venv/bin"
ExecStart=/var/www/ratesewa/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start the service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start ratesewa
sudo systemctl enable ratesewa
sudo systemctl status ratesewa
```

---

### Step 8: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/ratesewa
```

**Add this configuration** (replace `ratesewa.com` with your domain):
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
        add_header Cache-Control "public, immutable";
    }

    # Prevent access to .env and sensitive files
    location ~ /\. {
        deny all;
    }
}
```

**Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/ratesewa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### Step 9: Set Up SSL with Let's Encrypt

```bash
# Install certbot (if not already installed)
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d ratesewa.com -d www.ratesewa.com
```

Follow the prompts:
- Enter email address
- Agree to terms
- Choose "Redirect HTTP to HTTPS"

**Test auto-renewal:**
```bash
sudo certbot renew --dry-run
```

---

### Step 10: Configure Firewall (If needed)

```bash
# Check current rules
sudo ufw status

# If firewall is active, ensure these are allowed:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
```

---

## ✅ Deployment Complete!

### Test Your Site:

1. **Visit**: https://ratesewa.com (or your domain)
2. **Login** with admin credentials you just set
3. **Test features**:
   - Browse doctors
   - Search by city/specialty
   - View doctor profile
   - Admin panel → Manage Doctors

---

## 🔧 Useful Management Commands

### Check Application Status:
```bash
sudo systemctl status ratesewa
```

### View Logs:
```bash
# Application logs
sudo journalctl -u ratesewa -f

# Last 50 lines
sudo journalctl -u ratesewa -n 50
```

### Restart Application:
```bash
sudo systemctl restart ratesewa
```

### Update Application:
```bash
cd /var/www/ratesewa

# If using git
git pull origin main

# If uploading new files
# (upload tar.gz to /tmp/ first)
sudo systemctl stop ratesewa
cd /var/www/
sudo rm -rf ratesewa
sudo tar -xzf /tmp/ratesewa.tar.gz
sudo mv doctor_directory ratesewa
sudo chown -R www-data:www-data /var/www/ratesewa

# Restart
sudo systemctl start ratesewa
```

### Backup Database:
```bash
# Create backup
cp /var/www/ratesewa/instance/doctors.db ~/backup_doctors_$(date +%Y%m%d_%H%M%S).db

# Download to local machine
scp your-user@your-server-ip:~/backup_doctors_*.db ~/Downloads/
```

---

## 🐛 Troubleshooting

### Application won't start:
```bash
# Check logs
sudo journalctl -u ratesewa -n 50

# Test manually
cd /var/www/ratesewa
source venv/bin/activate
python3 app.py
```

### 502 Bad Gateway:
```bash
# Check Gunicorn is running
sudo systemctl status ratesewa

# Check Nginx config
sudo nginx -t

# Restart both
sudo systemctl restart ratesewa
sudo systemctl restart nginx
```

### Permission errors:
```bash
sudo chown -R www-data:www-data /var/www/ratesewa
sudo chmod -R 755 /var/www/ratesewa
sudo chmod 775 /var/www/ratesewa/instance
```

### Database errors:
```bash
# Re-seed database
cd /var/www/ratesewa
source venv/bin/activate
python3 seed_data.py
sudo systemctl restart ratesewa
```

---

## 🔒 Security Checklist

- [x] Admin password changed from default
- [x] SECRET_KEY set to random value
- [x] SSL certificate installed (HTTPS)
- [x] Firewall configured
- [ ] Regular database backups set up
- [ ] Monitor application logs

---

## 📊 Port Information

**RateSewa uses:**
- Gunicorn: `127.0.0.1:8000` (internal only)
- Nginx: Port 80 (HTTP) and 443 (HTTPS)

Since you have other apps running, make sure:
- No other app is using port 8000
- Nginx is routing different domains to different apps correctly

---

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| Start app | `sudo systemctl start ratesewa` |
| Stop app | `sudo systemctl stop ratesewa` |
| Restart app | `sudo systemctl restart ratesewa` |
| Check status | `sudo systemctl status ratesewa` |
| View logs | `sudo journalctl -u ratesewa -f` |
| Test Nginx | `sudo nginx -t` |
| Reload Nginx | `sudo systemctl reload nginx` |
| Backup DB | `cp /var/www/ratesewa/instance/doctors.db ~/backup.db` |

---

## 📞 DNS Configuration

Make sure your domain DNS has:

**A Record:**
```
Type: A
Name: @
Value: YOUR_DROPLET_IP
TTL: 3600
```

**CNAME Record (for www):**
```
Type: CNAME
Name: www
Value: @
TTL: 3600
```

Wait 10-60 minutes for DNS propagation.

---

**You're all set! Deploy and go live! 🚀**
