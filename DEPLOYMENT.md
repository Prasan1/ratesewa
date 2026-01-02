# RankSewa Deployment Guide

**Last Updated:** January 2, 2026

---

## Production Environment

**Platform:** DigitalOcean App Platform
**Database:** Managed PostgreSQL
**CDN/Storage:** Cloudflare R2
**Domain:** ranksewa.com
**Auto-Deploy:** Enabled (pushes to `main` branch auto-deploy)

---

## Initial Setup (One-Time)

### 1. DigitalOcean App Platform Setup

1. Create new App in DO dashboard
2. Connect GitHub repository
3. Configure build settings:
   - **Build Command:** None needed (Flask app)
   - **Run Command:** `gunicorn app:app`
4. Add managed PostgreSQL database
5. Set environment variables (see below)

### 2. Environment Variables

Add these in DO App Settings → Environment Variables:

```bash
# Database (auto-added by DO when you attach database)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Flask
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production

# Cloudflare R2 (for doctor photos)
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_ACCESS_KEY=your-access-key
CLOUDFLARE_SECRET_KEY=your-secret-key
CLOUDFLARE_BUCKET_NAME=your-bucket-name

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Stripe (when payments are added)
# STRIPE_SECRET_KEY=sk_live_...
# STRIPE_PUBLISHABLE_KEY=pk_live_...

# Email (when email notifications added)
# SENDGRID_API_KEY=SG....
```

### 3. Initial Database Setup

Access DO Console and run:

```bash
# Create all tables
python3 << 'EOF'
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ All tables created")
EOF
```

### 4. Run Migrations

```bash
# Gamification tables (points, badges, leaderboard)
python migrate_gamification_postgres.py

# Health Digest tables (articles, categories)
python migrate_health_digest_postgres.py

# Clinic tables (hidden but intact for future)
python migrate_clinic_postgres.py
```

### 5. Seed Initial Data

```bash
# Seed article categories and badges
# (already done in migrations above)

# Seed articles
python seed_articles.py
python seed_more_articles.py

# Award retroactive points to existing users (if any)
python3 << 'EOF'
from app import app, db
from models import User
from gamification import check_and_award_badges

with app.app_context():
    users = User.query.filter(User.points == 0).all()
    for user in users:
        if user.review_count > 0:
            points = user.review_count * 10
            for rating in user.ratings:
                if rating.comment and len(rating.comment) >= 100:
                    points += 5
                points += rating.helpful_count * 2
            user.points = points
            check_and_award_badges(user, db_commit=False)
    db.session.commit()
    print(f"✅ Updated {len(users)} users")
EOF
```

---

## Regular Deployment Process

### Automatic Deployment (Current)

Every push to `main` branch triggers auto-deploy:

```bash
git add .
git commit -m "Your commit message"
git push origin main

# DO automatically:
# 1. Pulls latest code
# 2. Installs dependencies
# 3. Restarts application
# 4. Deploys in ~2-3 minutes
```

### Manual Deployment (If needed)

In DO App Platform dashboard:
1. Go to your app
2. Click "Actions" → "Force Rebuild and Deploy"

---

## Database Migrations

### When You Add New Features

1. **Create migration script locally:**
   ```bash
   # Test with SQLite first
   python migrate_new_feature.py
   ```

2. **Create PostgreSQL version:**
   ```bash
   cp migrate_new_feature.py migrate_new_feature_postgres.py
   # Edit to use PostgreSQL-specific SQL (information_schema instead of pragma)
   ```

3. **Test locally with PostgreSQL:**
   ```bash
   # If you have local PostgreSQL
   DATABASE_URL=postgresql://localhost/test_db python migrate_new_feature_postgres.py
   ```

4. **Commit migration script:**
   ```bash
   git add migrate_new_feature_postgres.py
   git commit -m "Add migration for new feature"
   git push origin main
   ```

5. **Run on production:**
   ```bash
   # Access DO Console
   python migrate_new_feature_postgres.py
   ```

### Migration Best Practices

- ✅ Always use `IF NOT EXISTS` / `IF EXISTS` checks
- ✅ Make migrations idempotent (safe to run multiple times)
- ✅ Test locally before running on production
- ✅ Keep both SQLite and PostgreSQL versions
- ✅ Never delete old migration scripts
- ✅ Document what each migration does
- ❌ Don't modify old migrations (create new ones instead)

---

## Database Backup & Restore

### Automatic Backups (DO)
- Daily automatic backups by DigitalOcean
- Retained for 7 days
- Restore via DO dashboard

### Manual Backup

```bash
# Via DO Console
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Or download via DO dashboard:
# Database → Settings → Backups → Download
```

### Restore from Backup

```bash
# Via DO Console (CAREFUL - this overwrites!)
psql $DATABASE_URL < backup_20260102.sql
```

### Recommended: External Backup

Set up weekly external backups to S3/R2:

```bash
# Add to cron or GitHub Actions
pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m%d).sql.gz
# Upload to S3/R2
```

---

## Monitoring & Logs

### View Logs (DO Console)

```bash
# Real-time logs
# In DO dashboard: App → Runtime Logs

# Or via CLI
doctl apps logs <app-id> --follow
```

### Key Things to Monitor

- **Error rate:** Spike in 500 errors
- **Response time:** Slowness issues
- **Database connections:** Connection pool exhaustion
- **Memory usage:** Memory leaks
- **Disk usage:** Database size growing fast

### Recommended Tools

- **Error Tracking:** Sentry (add in Q1 2026)
- **Uptime:** UptimeRobot (free tier)
- **Performance:** New Relic or DataDog
- **Analytics:** Google Analytics

---

## Rollback Procedure

### If Deployment Breaks Something

**Option 1: Revert via Git**
```bash
git revert HEAD
git push origin main
# Auto-deploys previous working version
```

**Option 2: Rollback in DO Dashboard**
```bash
# App → Settings → Rollback
# Select previous successful deployment
```

**Option 3: Database Rollback**
```bash
# If migration broke something:
# 1. Restore from backup (see above)
# 2. Revert code to before migration
# 3. Deploy
```

---

## Scaling Considerations

### Current Capacity
- **App:** 1 basic container (512MB RAM, 1 vCPU)
- **Database:** 1GB RAM, 1 vCPU, 10GB storage
- **Estimated capacity:** ~1,000 concurrent users

### When to Scale Up

**App Tier:**
- CPU usage >80% sustained
- Memory usage >80%
- Response times >2 seconds

**Database:**
- Storage >80% full
- Connection pool exhausted
- Slow query performance

### Scaling Options

**Vertical (Increase Resources):**
- DO App Platform: Increase container size
- Database: Upgrade to larger plan

**Horizontal (Add More Instances):**
- DO auto-scales app containers
- Database: Read replicas for heavy read workloads

**Optimization Before Scaling:**
- Add Redis for caching
- Optimize database queries
- Add CDN for static assets
- Implement pagination

---

## Security Checklist

### Pre-Launch
- [x] Environment variables not in code
- [x] CSRF protection enabled
- [x] Passwords hashed
- [x] HTTPS enforced
- [ ] Rate limiting on sensitive endpoints
- [ ] SQL injection prevention (using ORM)
- [ ] XSS prevention (Jinja2 auto-escapes)

### Regular Security Tasks
- [ ] Update dependencies monthly
- [ ] Review access logs for suspicious activity
- [ ] Rotate secrets annually
- [ ] Security audit quarterly
- [ ] Backup test quarterly

### Incident Response Plan
1. Identify issue (user report, monitoring alert)
2. Assess severity (data breach vs minor bug)
3. Rollback if needed (see above)
4. Fix issue
5. Deploy fix
6. Post-mortem (what happened, how to prevent)

---

## Performance Optimization

### Current Optimizations
- ✅ Lazy loading images
- ✅ Compressed images (85% quality)
- ✅ Database indexes on key columns
- ✅ CDN for uploaded images (R2)

### Next Optimizations (When Needed)
- [ ] Redis for session storage
- [ ] Redis for caching expensive queries
- [ ] Database query optimization (EXPLAIN ANALYZE)
- [ ] Pagination on long lists
- [ ] API response caching
- [ ] Minify CSS/JS
- [ ] Enable gzip compression

---

## Troubleshooting Common Issues

### Issue: App Won't Start
**Check:**
- Environment variables set correctly?
- Database accessible?
- Runtime logs for error messages

### Issue: OAuth Not Working
**Check:**
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` set?
- Redirect URI matches in Google Console?
- Production domain whitelisted?

### Issue: Images Not Loading
**Check:**
- Cloudflare R2 credentials correct?
- Bucket permissions set to public read?
- CORS configured on R2 bucket?

### Issue: Database Connection Errors
**Check:**
- Database is running (DO dashboard)?
- Connection pool not exhausted?
- `DATABASE_URL` correct (postgres:// vs postgresql://)?

### Issue: Slow Performance
**Check:**
- Database query performance (slow query log)
- Memory usage (app containers)
- External API timeouts (Google OAuth)

---

## Deployment Checklist

### Before Every Deploy

- [ ] Test locally
- [ ] Review code changes
- [ ] Check for hardcoded secrets
- [ ] Update version in ROADMAP.md if major
- [ ] Write commit message with clear description

### After Deploy

- [ ] Verify app is running (visit homepage)
- [ ] Check error logs (first 5 minutes)
- [ ] Test critical user flows:
  - [ ] Search doctors
  - [ ] Login
  - [ ] Write review
  - [ ] Doctor profile loads
- [ ] Check database migrations ran successfully

### For Major Releases

- [ ] Announce in advance (email to doctors)
- [ ] Deploy during low-traffic time
- [ ] Have rollback plan ready
- [ ] Monitor closely for first hour
- [ ] Send follow-up email with changes

---

## Database Maintenance

### Weekly Tasks
- [ ] Review slow query log
- [ ] Check database size growth
- [ ] Verify backups succeeded

### Monthly Tasks
- [ ] Review and optimize indexes
- [ ] Clean up old data if needed (flagged reviews, etc.)
- [ ] Update statistics (ANALYZE in PostgreSQL)

### As Needed
- [ ] Vacuum database (PostgreSQL)
- [ ] Rebuild indexes if fragmented

---

## Cost Breakdown (Current)

### Monthly Costs
- **DigitalOcean App:** $12/month (Basic tier)
- **Managed Database:** $15/month (1GB plan)
- **Domain:** ~$1/month ($15/year)
- **Cloudflare R2:** $0-5/month (usage-based)
- **Total:** ~$30-35/month

### When to Upgrade
- App tier: When CPU/memory consistently high
- Database: When >8GB or need more connections
- Expected at: ~500 active doctors or 5,000 MAU

---

## Emergency Contacts

**Developer:** [Your Contact]
**DO Support:** support.digitalocean.com
**Cloudflare Support:** dash.cloudflare.com

**Important URLs:**
- Production: https://ranksewa.com
- Admin: https://ranksewa.com/admin/doctors
- DO Dashboard: https://cloud.digitalocean.com
- GitHub Repo: https://github.com/Prasan1/ratesewa

---

## Useful Commands

### DO Console Quick Commands

```bash
# Check database size
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size(current_database()));"

# Check table sizes
psql $DATABASE_URL -c "SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"

# Count records in each table
python3 << 'EOF'
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    for table in inspector.get_table_names():
        count = db.session.execute(f"SELECT COUNT(*) FROM {table}").scalar()
        print(f"{table}: {count}")
EOF

# Clear all sessions (logout all users)
python3 << 'EOF'
from app import app, db
with app.app_context():
    # Sessions are stored in Flask, not DB
    # Restart app to clear sessions
    print("Restart app to clear sessions")
EOF
```

---

**Document Maintenance:**
Update this file when:
- Infrastructure changes
- New services added
- Deployment process changes
- New monitoring tools added
