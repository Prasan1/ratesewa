# Clinic Manager Feature - Implementation Guide

## Current Status (MVP)
✅ **Hidden for launch** - Code exists but not advertised publicly
📅 **Add Later** - After you have 50+ active doctors and clinic interest

## What's Already Built (Don't Delete!)

### Database Models (`models.py`):
- `Clinic` - Basic clinic info (name, slug, city, featured flag)
- `ClinicAccount` - Subscription tier for clinic managers
- `ClinicManagerDoctor` - Links managers to multiple doctors
- `Doctor.clinic_id` - FK to link doctors to clinics

### Routes (`app.py`):
- `/clinics` - Public clinic listing
- `/clinic/<slug>` - Individual clinic profile
- `/clinic/manager` - Manager dashboard
- `/admin/clinics/*` - Admin CRUD operations

### Templates:
- `clinic_profile.html` - Public clinic page
- `clinic_manager_dashboard.html` - Manager interface
- `clinics.html` - Clinic listing page

## How to Re-Enable Clinic Manager Features

### Step 1: Pricing Page
Edit `templates/pricing.html` - Uncomment clinic pricing section (it's been removed but saved in git history)

Or add new section:
```html
<div class="text-center mb-4 mt-5">
    <h2 class="fw-bold">Clinic Manager Plans</h2>
    <p class="text-muted">For clinics managing multiple doctors</p>
</div>
<!-- Add pricing cards here -->
```

### Step 2: Homepage
Edit `templates/index.html` - Remove comment markers around line 65:
```html
{# Featured Clinics - Hidden for MVP, can enable later
... (code is commented out) ...
#}
```

Change to:
```html
<!-- Featured Clinics -->
{% if featured_clinics %}
...
{% endif %}
```

### Step 3: Migration (if needed)
If you've never run clinic migrations on production:
```bash
python3 << 'EOF'
from app import app, db
from models import Clinic, ClinicAccount
with app.app_context():
    db.create_all()
    print("✅ Clinic tables created")
EOF
```

### Step 4: Create Sample Clinics
Via admin panel at `/admin/clinics/new` or programmatically:
```python
from app import app, db
from models import Clinic, City

with app.app_context():
    city = City.query.filter_by(name='Kathmandu').first()

    clinic = Clinic(
        name='Sample Medical Center',
        slug='sample-medical-center',
        city_id=city.id,
        description='Multi-specialty clinic in Kathmandu',
        is_featured=True
    )
    db.session.add(clinic)
    db.session.commit()
```

## Pricing Research (Nepal Market 2025-2026)

Based on research:
- **Digital marketing for clinics:** NPR 8,000-15,000/month
- **Clinic management software:** NPR 4,000-13,000/month

### Recommended Pricing (When You Add It Back):
- **Starter** (3 doctors): NPR 3,999/month
- **Growth** (8 doctors): NPR 7,999/month
- **Pro** (15 doctors): NPR 11,999/month

## Marketing Message (When Ready)

**Target:** Receptionists and clinic managers, NOT doctors

**Hook:** "Stop losing patients to other clinics. Your doctors work hard - let us fill their appointment books."

**Features that matter to THEM:**
- ✅ Featured placement = More appointment bookings
- ✅ Priority support = Less tech headaches
- ✅ Multi-doctor management = Manage 3-15 doctors from one dashboard
- ✅ Analytics = Prove ROI to clinic owner

## When to Re-Enable

Wait until you have:
1. **50+ active doctors** using individual accounts
2. **Clinics asking for bulk management** (proof of demand)
3. **2-3 beta clinics** willing to test the feature
4. **Clear feedback** on what features clinic managers actually want

## Git History

All clinic code changes are saved in git:
- Commit: [hash] - "Add clinic manager feature"
- Can always `git show [hash]` to see what was there

**Don't rush this!** Get doctors using it first, then add clinic features when there's proven demand.
