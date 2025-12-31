# Switch RateSewa from SQLite to PostgreSQL

## Why PostgreSQL?

✅ **Data persists** across deployments (no data loss!)
✅ **Better performance** for production
✅ **Concurrent users** - handles multiple writes
✅ **Automatic backups** with DO Managed Database
✅ **Production-ready**

---

## 🚀 Quick Migration (15 minutes)

### Step 1: Create PostgreSQL Database in DO (5 minutes)

#### 1.1 Create Database:

1. In DO dashboard, click **Databases** (left sidebar)
2. Click **Create Database Cluster**
3. Choose:
   - **Database engine:** PostgreSQL
   - **Version:** 16 (or latest)
   - **Datacenter:** Same region as your app (Singapore for you)
   - **Plan:** Basic (starts at $15/month)
     - **Dev Database** ($15/month) - Perfect for MVP
     - DB Size: 1 GB RAM, 10 GB Disk
     - 1 Node

4. **Database name:** `ratesewa-db` (or any name)
5. Click **Create Database Cluster**

⏱️ **Wait 3-5 minutes** for database to provision.

#### 1.2 Get Connection String:

Once created:

1. Click on your **ratesewa-db** database
2. Go to **Connection Details** tab
3. Under **Connection Parameters**, select:
   - **User:** `doadmin` (default)
   - **Database:** `defaultdb` (or create new database)
4. **Copy the Connection String** - looks like:
   ```
   postgresql://doadmin:AVNS_xxx@ratesewa-db-do-user-xxx.db.ondigitalocean.com:25060/defaultdb?sslmode=require
   ```

**Save this!** You'll need it in Step 3.

---

### Step 2: Update Application Code (5 minutes)

#### 2.1 Add PostgreSQL Driver:

Add this line to `requirements.txt`:

```bash
echo "psycopg2-binary==2.9.9" >> requirements.txt
```

Commit and push:
```bash
git add requirements.txt
git commit -m "Add PostgreSQL support"
git push origin main
```

---

### Step 3: Update Environment Variable in DO (2 minutes)

#### 3.1 Update DATABASE_URL:

1. Go to your **ratesewa** app in DO
2. Click **Settings** tab
3. Scroll to **App-Level Environment Variables**
4. Find `DATABASE_URL`
5. Click **Edit**
6. **Replace** the SQLite value with your PostgreSQL connection string:
   ```
   postgresql://doadmin:AVNS_xxx@ratesewa-db-do-user-xxx.db.ondigitalocean.com:25060/defaultdb?sslmode=require
   ```
7. Click **Save**

#### 3.2 Deploy Changes:

DO will ask to redeploy:
1. Click **Deploy** or **Redeploy**
2. Wait 3-5 minutes for deployment

---

### Step 4: Initialize Database Tables (3 minutes)

After deployment completes:

#### 4.1 Open Console:

1. In your app, click **Console** tab
2. Click **Run Console**
3. Wait for terminal to load

#### 4.2 Seed Database:

In the console, run:

```bash
# Create tables (automatically done by wsgi.py, but verify)
python3 init_db.py

# Add 29 doctors
python3 seed_data.py

# Change admin password
python3 change_admin_password.py
```

You should see:
```
✅ Database tables created successfully!
✅ Database seeded successfully!
✅ Added 29 doctors across 12 cities
```

---

## ✅ Verification (2 minutes)

### Test Your App:

1. **Visit your app** URL
2. **Login** with admin credentials
3. **Check doctors** are visible (29 doctors)
4. **Create a test user** (register)
5. **Leave a rating** on a doctor
6. **Redeploy your app** (to test persistence):
   - Settings → Redeploy
   - Wait for deployment
   - **Check if data is still there** ✅

**If data persists after redeploy → PostgreSQL is working!** 🎉

---

## 🔧 Optional: Create Dedicated Database (Better Practice)

Instead of using `defaultdb`, create a dedicated database:

### In PostgreSQL Console (DO Dashboard):

1. Go to your **ratesewa-db** database
2. Click **Users & Databases** tab
3. Click **Add new database**
4. Name: `ratesewa_production`
5. Click **Save**

### Update Connection String:

Replace `defaultdb` with `ratesewa_production`:
```
postgresql://doadmin:AVNS_xxx@ratesewa-db-do-user-xxx.db.ondigitalocean.com:25060/ratesewa_production?sslmode=require
```

Update `DATABASE_URL` in your app and redeploy.

---

## 💾 Automatic Backups (Included Free!)

DO Managed Database includes:

✅ **Daily backups** (automatic)
✅ **7-day retention** (can extend)
✅ **Point-in-time recovery**
✅ **Automatic failover** (for higher tiers)

### View Backups:

1. Go to your database in DO
2. Click **Backups & Restore** tab
3. See all daily backups

### Restore from Backup:

1. In **Backups & Restore** tab
2. Click **Restore** on any backup
3. Choose to restore to:
   - Same database (overwrites)
   - New database cluster

---

## 📊 Database Monitoring

### Check Performance:

1. Go to your **ratesewa-db** in DO
2. Click **Metrics** tab
3. Monitor:
   - CPU usage
   - Memory usage
   - Connection count
   - Queries per second

### Connection Pooling:

For better performance with multiple users, consider enabling connection pooling:

**In DO Database:**
1. Go to **Connection Pools** tab
2. Create new pool:
   - Name: `ratesewa-pool`
   - Database: `ratesewa_production`
   - Pool Mode: Transaction
   - Pool Size: 10

3. Use the **pool connection string** instead of direct database connection

---

## 💰 Cost Breakdown

### With PostgreSQL:

**Current Setup (SQLite):**
- App Platform Basic: $5/month
- **Total: $5/month**

**New Setup (PostgreSQL):**
- App Platform Basic: $5/month
- PostgreSQL Dev DB: $15/month
- **Total: $20/month**

### Is It Worth It?

**YES for production:**
- ✅ No data loss on redeploys
- ✅ Real user accounts persist
- ✅ Doctor ratings saved permanently
- ✅ Automatic backups
- ✅ Better performance
- ✅ Scalable for growth

---

## 🔄 Migration Checklist

- [ ] PostgreSQL database created in DO
- [ ] Connection string copied
- [ ] `psycopg2-binary` added to requirements.txt
- [ ] Code committed and pushed
- [ ] `DATABASE_URL` environment variable updated
- [ ] App redeployed successfully
- [ ] Database tables created (init_db.py)
- [ ] Data seeded (seed_data.py)
- [ ] Admin password changed
- [ ] Tested app - doctors visible
- [ ] Tested persistence - redeploy and check data
- [ ] Backups verified in DO dashboard

---

## 🐛 Troubleshooting

### "Could not connect to server" error:

**Check:**
1. Connection string is correct
2. Database cluster is running (green in DO)
3. SSL mode is `sslmode=require` in connection string

### "relation does not exist" error:

**Fix:**
```bash
# In console
python3 init_db.py
python3 seed_data.py
```

### Performance is slow:

**Check:**
1. Database metrics in DO dashboard
2. Consider upgrading to larger database plan
3. Enable connection pooling

### Can't access console:

**Alternative - Run locally then import:**

1. **Export SQLite data** (if you had any):
   ```bash
   sqlite3 instance/doctors.db .dump > backup.sql
   ```

2. **Connect to PostgreSQL locally:**
   ```bash
   pip install psycopg2-binary
   # Use connection string from DO
   DATABASE_URL="postgresql://..." python3 seed_data.py
   ```

---

## 🎯 Quick Command Reference

### Create Tables:
```bash
python3 init_db.py
```

### Seed Database:
```bash
python3 seed_data.py
```

### Change Admin Password:
```bash
python3 change_admin_password.py
```

### Check Database Connection:
```bash
python3 -c "from app import db, app; app.app_context().push(); print('✅ Connected to:', db.engine.url)"
```

---

## 🚀 You're Ready!

After migration:
- ✅ Data persists forever
- ✅ Production-ready setup
- ✅ Automatic backups
- ✅ Can handle real traffic
- ✅ Scale as you grow

**Total migration time: ~15 minutes**
**Cost increase: +$15/month**
**Value: Priceless for production app!**

---

**Let me know when you're ready to start and I'll walk you through each step!**
