#!/bin/bash
# RateSewa - Production Deployment Commands
# Quick reference for copy-paste deployment

echo "======================================"
echo "RateSewa Production Deployment"
echo "======================================"
echo ""

# ==========================================
# OPTION 1: VPS DEPLOYMENT (Ubuntu/Debian)
# ==========================================

echo "--- STEP 1: UPDATE SYSTEM ---"
echo "sudo apt update && sudo apt upgrade -y"
echo ""

echo "--- STEP 2: INSTALL REQUIREMENTS ---"
echo "sudo apt install -y python3 python3-pip python3-venv nginx git"
echo ""

echo "--- STEP 3: CREATE PROJECT DIRECTORY ---"
echo "sudo mkdir -p /var/www/ratesewa"
echo "cd /var/www/ratesewa"
echo ""

echo "--- STEP 4: UPLOAD CODE (Choose One) ---"
echo "# Option A: Git Clone"
echo "sudo git clone https://github.com/yourusername/ratesewa.git ."
echo ""
echo "# Option B: SCP from local machine"
echo "# On local machine:"
echo "cd /home/ppaudyal/Documents/drprofile/"
echo "tar -czf ratesewa.tar.gz doctor_directory/"
echo "scp ratesewa.tar.gz user@your-server-ip:/tmp/"
echo "# On server:"
echo "cd /var/www/"
echo "sudo tar -xzf /tmp/ratesewa.tar.gz"
echo "sudo mv doctor_directory ratesewa"
echo ""

echo "--- STEP 5: SET UP VIRTUAL ENVIRONMENT ---"
echo "cd /var/www/ratesewa"
echo "python3 -m venv venv"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
echo "pip install gunicorn"
echo ""

echo "--- STEP 6: CREATE .ENV FILE ---"
echo "nano .env"
echo "# Add to .env:"
echo "# SECRET_KEY=\$(python3 -c \"import secrets; print(secrets.token_hex(32))\")"
echo "# SQLALCHEMY_DATABASE_URI=sqlite:///doctors.db"
echo "# SESSION_COOKIE_SECURE=True"
echo ""

echo "--- STEP 7: GENERATE SECRET KEY ---"
echo "python3 -c \"import secrets; print(secrets.token_hex(32))\""
echo "# Copy output and add to .env as SECRET_KEY"
echo ""

echo "--- STEP 8: INITIALIZE DATABASE ---"
echo "cd /var/www/ratesewa"
echo "source venv/bin/activate"
echo "python3 seed_data.py"
echo "python3 change_admin_password.py"
echo ""

echo "--- STEP 9: SET PERMISSIONS ---"
echo "sudo chown -R www-data:www-data /var/www/ratesewa"
echo "sudo chmod -R 755 /var/www/ratesewa"
echo ""

echo "--- STEP 10: CREATE GUNICORN SERVICE ---"
echo "sudo nano /etc/systemd/system/ratesewa.service"
echo ""
echo "# Add this content:"
cat << 'EOF'
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
EOF
echo ""

echo "--- STEP 11: START GUNICORN ---"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl start ratesewa"
echo "sudo systemctl enable ratesewa"
echo "sudo systemctl status ratesewa"
echo ""

echo "--- STEP 12: CONFIGURE NGINX ---"
echo "sudo nano /etc/nginx/sites-available/ratesewa"
echo ""
echo "# Add this content (replace ratesewa.com with your domain):"
cat << 'EOF'
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
EOF
echo ""

echo "--- STEP 13: ENABLE NGINX SITE ---"
echo "sudo ln -s /etc/nginx/sites-available/ratesewa /etc/nginx/sites-enabled/"
echo "sudo nginx -t"
echo "sudo systemctl restart nginx"
echo ""

echo "--- STEP 14: SETUP FIREWALL ---"
echo "sudo ufw allow 22"
echo "sudo ufw allow 80"
echo "sudo ufw allow 443"
echo "sudo ufw enable"
echo ""

echo "--- STEP 15: INSTALL SSL CERTIFICATE ---"
echo "sudo apt install -y certbot python3-certbot-nginx"
echo "sudo certbot --nginx -d ratesewa.com -d www.ratesewa.com"
echo ""

echo "======================================"
echo "DEPLOYMENT COMPLETE!"
echo "======================================"
echo "Visit: https://ratesewa.com"
echo ""

# ==========================================
# MAINTENANCE COMMANDS
# ==========================================

echo ""
echo "--- USEFUL MAINTENANCE COMMANDS ---"
echo ""
echo "# Check application status:"
echo "sudo systemctl status ratesewa"
echo ""
echo "# View logs:"
echo "sudo journalctl -u ratesewa -f"
echo ""
echo "# Restart application:"
echo "sudo systemctl restart ratesewa"
echo ""
echo "# Restart Nginx:"
echo "sudo systemctl restart nginx"
echo ""
echo "# Update application:"
echo "cd /var/www/ratesewa"
echo "git pull origin main"
echo "sudo systemctl restart ratesewa"
echo ""
echo "# Test SSL renewal:"
echo "sudo certbot renew --dry-run"
echo ""
echo "# Backup database:"
echo "cp /var/www/ratesewa/instance/doctors.db ~/doctors_backup_\$(date +%Y%m%d).db"
echo ""

# ==========================================
# TROUBLESHOOTING
# ==========================================

echo ""
echo "--- TROUBLESHOOTING ---"
echo ""
echo "# Application won't start:"
echo "sudo journalctl -u ratesewa -n 50"
echo ""
echo "# 502 Bad Gateway:"
echo "sudo systemctl status ratesewa"
echo "sudo nginx -t"
echo ""
echo "# Permission errors:"
echo "sudo chown -R www-data:www-data /var/www/ratesewa"
echo "sudo chmod -R 755 /var/www/ratesewa"
echo ""

echo "======================================"
echo "For detailed instructions, see:"
echo "- QUICK_DEPLOY.md (quick start)"
echo "- DEPLOY_TO_PRODUCTION.md (full guide)"
echo "======================================"
