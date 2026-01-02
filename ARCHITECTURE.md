# RankSewa Architecture Documentation

**Last Updated:** January 2, 2026
**Version:** 1.0 (MVP Launch)

## Table of Contents
1. [System Overview](#system-overview)
2. [Tech Stack](#tech-stack)
3. [Database Schema](#database-schema)
4. [Key Features](#key-features)
5. [File Structure](#file-structure)
6. [Data Flow](#data-flow)
7. [Infrastructure](#infrastructure)
8. [Security & Privacy](#security--privacy)

---

## System Overview

RankSewa is a doctor review and discovery platform for Nepal, helping patients find trusted healthcare providers based on real patient experiences.

### Core Value Propositions
- **For Patients:** Find and review doctors, earn rewards for contributions
- **For Doctors:** Manage online presence, respond to reviews, get discovered
- **For Platform:** SEO-driven content attracts traffic, gamification drives engagement

### Current Stage
- **MVP Launch:** Individual doctor profiles, patient reviews, gamification, health content
- **Next Phase:** Clinic management, advanced analytics, appointment booking integration

---

## Tech Stack

### Backend
- **Framework:** Flask (Python 3.10+)
- **Database:** PostgreSQL (Production), SQLite (Local dev)
- **ORM:** SQLAlchemy
- **Authentication:** OAuth 2.0 (Google), session-based auth
- **File Storage:** Cloudflare R2 (doctor photos)

### Frontend
- **Templates:** Jinja2
- **CSS:** Bootstrap 5.3 + Custom CSS
- **JavaScript:** jQuery 3.6.0 + Vanilla JS
- **Icons:** Font Awesome 6.0

### Infrastructure
- **Hosting:** DigitalOcean App Platform
- **Version Control:** Git + GitHub
- **CDN/Assets:** Cloudflare R2
- **Domain:** ranksewa.com

### Third-Party Services
- **Payments:** Stripe (planned, not yet integrated)
- **Email:** Not configured yet (planned: SendGrid or similar)
- **Analytics:** None yet (planned: Google Analytics)

---

## Database Schema

### Core Tables

#### Users
```sql
users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password VARCHAR(200),  -- hashed
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(20),  -- 'patient', 'doctor', 'admin'
    doctor_id INTEGER FK -> doctors.id,
    points INTEGER DEFAULT 0,  -- gamification
    created_at TIMESTAMP
)
```

#### Doctors
```sql
doctors (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(250) UNIQUE NOT NULL,
    city_id INTEGER FK -> cities.id,
    specialty_id INTEGER FK -> specialties.id,
    clinic_id INTEGER FK -> clinics.id,  -- nullable
    experience INTEGER,
    education TEXT,
    workplace VARCHAR(200),
    description TEXT,
    phone_number VARCHAR(20),
    photo_url TEXT,  -- Cloudflare R2 URL
    is_verified BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP
)
```

#### Ratings (Reviews)
```sql
ratings (
    id INTEGER PRIMARY KEY,
    doctor_id INTEGER FK -> doctors.id,
    user_id INTEGER FK -> users.id,
    rating INTEGER,  -- 1-5 stars
    comment TEXT,
    user_name VARCHAR(200),
    user_email VARCHAR(200),
    is_verified_patient BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,  -- gamification
    created_at TIMESTAMP
)
```

#### Clinics
```sql
clinics (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(250) UNIQUE NOT NULL,
    city_id INTEGER FK -> cities.id,
    address TEXT,
    phone_number VARCHAR(20),
    description TEXT,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
)
```

### Reference Data Tables

```sql
cities (id, name, slug)
specialties (id, name, slug, icon)
```

### Gamification Tables

```sql
badge_definitions (id, name, slug, description, icon, tier, display_order)
user_badges (id, user_id FK, badge_id FK, earned_at TIMESTAMP)
review_helpful (id, rating_id FK, user_id FK, created_at TIMESTAMP)
```

### Health Digest Tables

```sql
article_categories (id, name, slug, icon, description, display_order)
articles (
    id, title, slug, category_id FK, content TEXT,
    summary, featured_image, meta_description, meta_keywords,
    related_specialty_id FK, author_name,
    is_published BOOLEAN, is_featured BOOLEAN,
    view_count, published_at, created_at
)
```

### Pending Features Tables (Hidden from MVP)

```sql
clinic_accounts (id, manager_user_id FK, subscription_tier, max_doctors)
clinic_manager_doctors (id, manager_user_id FK, doctor_id FK)
appointments (id, user_id FK, doctor_id FK, date, time, status)
contact_messages (id, name, email, message, created_at)
verification_requests (id, user_id FK, doctor_id FK, status, documents)
doctor_responses (id, rating_id FK, response TEXT, created_at)
review_flags (id, rating_id FK, reason, created_at)
advertisements (id, title, image_url, link_url, placement, is_active)
```

---

## Key Features

### 1. Doctor Search & Discovery
- **Location:** `app.py` - `/` route, `get_doctors()` API
- **How it works:**
  - Users filter by city, specialty, or search by name/clinic
  - AJAX call to `/doctors` returns filtered results
  - Results sorted by featured status, then verification, then name
  - Lazy-loaded images for performance

### 2. Review System
- **Location:** `app.py` - `/doctor/<slug>/review` route
- **Flow:**
  1. User must be logged in
  2. Submit rating (1-5) + optional comment
  3. Gamification system awards points and badges automatically
  4. Review appears on doctor profile
  5. Doctor can respond (if verified)

### 3. Gamification System
- **Location:** `gamification.py`
- **How it works:**
  - Points awarded automatically when users:
    - Write a review: 10 points
    - Write detailed review (100+ words): +5 bonus
    - First to review a doctor: +5 bonus
    - Someone marks review helpful: 2 points
    - Doctor responds to their review: 3 points
  - Badges auto-awarded when thresholds met
  - Tiers: Bronze (0-50), Silver (51-150), Gold (151-300), Platinum (301+)
  - User tier badge shows on all their reviews

### 4. Health Digest (SEO Content)
- **Location:** `app.py` - `/health-digest` routes
- **Purpose:** Drive organic traffic via health content
- **Features:**
  - 7 initial articles (diabetes, BP, cholesterol, women's health, nutrition, mental health)
  - Category filtering and search
  - Related doctors shown on relevant articles
  - Social sharing (Facebook, Twitter, WhatsApp)
  - SEO optimized (meta tags, Open Graph)
  - Images locally hosted and lazy-loaded

### 5. Doctor Profile Management
- **Location:** `app.py` - `/doctor/profile/edit`
- **Features:**
  - Upload profile photo (Cloudflare R2)
  - Edit bio, education, workplace
  - View analytics (views, reviews)
  - Respond to reviews (if verified)
  - See verification status

### 6. Admin Panel
- **Location:** `app.py` - `/admin/*` routes
- **Access:** Only users with `is_admin=True`
- **Capabilities:**
  - Manage doctors (CRUD, verify, feature)
  - Manage articles (CRUD, publish)
  - Manage cities and specialties
  - Review verification requests
  - View all users

---

## File Structure

```
doctor_directory/
├── app.py                          # Main Flask app, all routes
├── models.py                       # SQLAlchemy models
├── config.py                       # Configuration
├── gamification.py                 # Points and badge logic
├── upload_utils.py                 # Photo upload handling
├── r2_storage.py                   # Cloudflare R2 integration
├── subscription_config.py          # Doctor subscription tiers
├── promo_config.py                 # Promotional banners
├── ad_manager.py                   # Advertisement management (unused)
│
├── templates/                      # Jinja2 templates
│   ├── base.html                   # Base layout
│   ├── index.html                  # Homepage
│   ├── doctor_profile.html         # Doctor detail page
│   ├── user_profile.html           # Patient profile
│   ├── health_digest.html          # Article listing
│   ├── article_detail.html         # Individual article
│   ├── pricing.html                # Pricing page
│   ├── leaderboard.html            # Gamification leaderboard
│   ├── admin_*.html                # Admin panel templates
│   └── ...
│
├── static/
│   ├── css/style.css               # Custom styles
│   ├── js/main.js                  # JavaScript
│   ├── img/                        # Local images (articles, logo)
│   └── favicon.svg
│
├── migrations/                     # Database migration scripts
│   ├── migrate_gamification_postgres.py
│   ├── migrate_health_digest_postgres.py
│   └── ...
│
├── seed scripts/                   # Data population
│   ├── seed_articles.py
│   ├── seed_more_articles.py
│   └── retroactive_points.py
│
├── docs/                           # Documentation
│   ├── ARCHITECTURE.md             # This file
│   ├── ROADMAP.md                  # Future plans
│   ├── CLINIC_FEATURE_GUIDE.md     # Re-enable clinic features
│   └── DEPLOYMENT.md               # Deployment guide
│
└── .env                            # Environment variables (gitignored)
```

---

## Data Flow

### 1. User Writes a Review
```
User clicks "Write Review" on doctor profile
  ↓
Check if logged in → Redirect to login if not
  ↓
Submit review form (POST /doctor/<id>/review)
  ↓
app.py: create Rating object
  ↓
gamification.py: process_new_review()
  ↓
Award points based on:
  - Base: 10 points
  - Detailed (100+ words): +5 points
  - First review for doctor: +5 points
  ↓
check_and_award_badges()
  ↓
Check if user qualifies for badges:
  - First Review (1 review)
  - Detailed Reviewer (100+ word review)
  - Community Champion (5, 10, 25 reviews)
  - Specialty Explorer (3+ specialties)
  - City Guide (3+ cities)
  ↓
Commit to database
  ↓
Flash success message with points earned
  ↓
Redirect back to doctor profile
```

### 2. Doctor Claims Profile
```
User visits /claim-profile
  ↓
Search for their doctor profile
  ↓
Submit verification request with documents
  ↓
VerificationRequest created (status: pending)
  ↓
Admin reviews at /admin/verification_requests
  ↓
Admin approves → User.role = 'doctor', User.doctor_id = doctor.id
  ↓
Doctor can now:
  - Edit profile
  - Upload photo
  - Respond to reviews
  - View analytics
```

### 3. Search Workflow
```
User enters filters (city, specialty, name search)
  ↓
JavaScript triggers AJAX call on filter change
  ↓
GET /doctors?city_id=X&specialty_id=Y&name=Z
  ↓
app.py: query doctors with filters
  ↓
Join with clinics for clinic name search
  ↓
Order by: is_featured DESC, is_verified DESC, name
  ↓
Return JSON with doctor data
  ↓
JavaScript renders doctor cards
  ↓
Images lazy-loaded as user scrolls
```

---

## Infrastructure

### Production (DigitalOcean App Platform)
- **Platform:** Managed App Platform (auto-scaling)
- **Database:** Managed PostgreSQL database
- **Static Files:** Served via Cloudflare R2
- **Deployment:** Auto-deploy on git push to main branch
- **Environment Variables:** Set in DO dashboard
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `CLOUDFLARE_*` (R2 credentials)
  - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
  - `STRIPE_*` (when payments added)

### Local Development
- **Database:** SQLite (`doctors.db`)
- **Run:** `python app.py` (Flask dev server)
- **Access:** http://localhost:5000

### Key Environment Variables
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_ACCESS_KEY=...
CLOUDFLARE_SECRET_KEY=...
CLOUDFLARE_BUCKET_NAME=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

---

## Security & Privacy

### Authentication
- Session-based for regular login (password hashed with Werkzeug)
- OAuth 2.0 for Google login
- CSRF protection enabled (Flask-WTF)

### Authorization
- Role-based: 'patient', 'doctor', 'admin'
- Decorators: `@login_required`, `@admin_required`, `@doctor_required`

### Data Protection
- Passwords hashed before storage
- No sensitive data in logs
- Doctor photos stored on separate CDN (R2)
- Reviews can be flagged for moderation

### Privacy Considerations
- User emails not shown publicly
- Review authors shown as names only
- Doctors must verify to respond to reviews
- Admin access logged (should add audit trail)

### Known Security TODOs
- [ ] Add rate limiting (prevent spam reviews)
- [ ] Add email verification for new users
- [ ] Add 2FA for admin accounts
- [ ] Add audit logging for admin actions
- [ ] Add CAPTCHA on review submission
- [ ] Add review edit/delete for users (currently permanent)

---

## Performance Optimizations

### Current Optimizations
✅ Lazy loading images (`loading="lazy"` attribute)
✅ Image compression (85% quality JPEG)
✅ Database indexes on frequently queried columns (slug, email)
✅ Eager loading relationships with `joinedload()` where needed
✅ Static assets cached by CDN (Cloudflare R2)

### Future Optimizations
- [ ] Add Redis for session storage and caching
- [ ] Add database connection pooling
- [ ] Implement full-text search (PostgreSQL FTS or Elasticsearch)
- [ ] Add CDN for all static assets (not just images)
- [ ] Implement pagination on long lists (reviews, doctors)
- [ ] Add browser caching headers
- [ ] Minify CSS/JS in production

---

## Error Handling & Monitoring

### Current State
- Basic Flask error handlers (404, 500)
- Flash messages for user feedback
- No centralized logging
- No error tracking service

### Recommended Additions
- [ ] Sentry or Rollbar for error tracking
- [ ] Structured logging (JSON logs)
- [ ] Uptime monitoring (UptimeRobot, Pingdom)
- [ ] Performance monitoring (New Relic, DataDog)
- [ ] Database query monitoring
- [ ] Alert system for critical errors

---

## Backup & Disaster Recovery

### Current Backup Strategy
⚠️ **Relies on DigitalOcean automatic backups**

### Recommended Improvements
- [ ] Daily automated database dumps to external storage
- [ ] Point-in-time recovery capability
- [ ] Test restoration process quarterly
- [ ] Document recovery procedures
- [ ] Backup environment variables securely
- [ ] Version control for all code (already done via Git)

---

## API Documentation (Internal)

### GET /doctors
**Purpose:** Filter and search doctors
**Parameters:**
- `city_id` (optional): Filter by city
- `specialty_id` (optional): Filter by specialty
- `name` (optional): Search by doctor or clinic name

**Returns:** JSON array of doctor objects

### POST /doctor/<slug>/review
**Purpose:** Submit a review for a doctor
**Auth:** Required (logged in user)
**Body:**
- `rating`: 1-5 (required)
- `comment`: Text (optional)

**Side Effects:**
- Creates Rating record
- Awards points to user
- Awards badges if thresholds met

### POST /mark_helpful
**Purpose:** Mark a review as helpful
**Auth:** Required
**Body:**
- `rating_id`: ID of rating
- `doctor_slug`: For redirect

**Side Effects:**
- Creates ReviewHelpful record
- Awards 2 points to review author

---

## Testing Strategy

### Current State
⚠️ **No automated tests**

### Recommended Test Coverage
- [ ] Unit tests for gamification logic
- [ ] Integration tests for review submission
- [ ] E2E tests for critical user flows:
  - Sign up → Write review → Earn badge
  - Doctor claims profile → Responds to review
  - Search → Filter → View profile
- [ ] Load testing for concurrent users
- [ ] Security testing (OWASP Top 10)

---

## Versioning & Changelog

### Version History
- **v1.0** (Jan 2026): MVP Launch
  - Doctor profiles and reviews
  - Gamification system
  - Health Digest
  - OAuth login

### Future Versions
See ROADMAP.md for planned features

---

## Contributing & Development Workflow

### Git Workflow
1. Always work on `main` branch (small team)
2. Commit messages follow format:
   ```
   Category: Brief description

   Detailed explanation

   🤖 Generated with Claude Code
   Co-Authored-By: Claude Sonnet 4.5
   ```
3. Push to GitHub triggers auto-deploy to DigitalOcean

### Database Migrations
1. Create migration script in `migrations/`
2. Test locally with SQLite
3. Create PostgreSQL version with `_postgres.py` suffix
4. Run on production via DO console
5. Never delete migration scripts

### Deployment Checklist
- [ ] Test locally
- [ ] Run migrations on production
- [ ] Push to GitHub
- [ ] Verify auto-deploy succeeded
- [ ] Smoke test critical features
- [ ] Check error logs

---

## Contacts & Resources

**Developer:** [Your Name]
**Repository:** https://github.com/Prasan1/ratesewa
**Production:** https://ranksewa.com
**Admin Panel:** https://ranksewa.com/admin/doctors

**Key Documentation:**
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Bootstrap 5: https://getbootstrap.com/docs/5.3/
- Cloudflare R2: https://developers.cloudflare.com/r2/

---

**Document Maintenance:**
Update this file whenever:
- Major features added or removed
- Database schema changes
- Infrastructure changes
- New dependencies added
