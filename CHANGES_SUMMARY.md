# Recent Changes Summary
**Date:** January 2, 2026
**Version:** MVP Launch Preparation

---

## Changes Made

### 1. Pricing Updates

#### Featured Tier Price Reduction
- **Old:** NPR 5,000/month
- **New:** NPR 2,999/month
- **Reason:** More competitive with Nepal market rates, 50% increase over Premium instead of 2.5x

#### Photo Upload Moved to Basic Tier
- **Old:** Photo upload only in Premium (NPR 2,000) and Featured tiers
- **New:** Photo upload included in Basic (Free) tier
- **Reason:**
  - Modern expectation - profile photos are standard in 2026
  - R2 storage costs are negligible (NPR 5-10/month total)
  - Better patient experience
  - Premium tier still valuable (verified badge, review responses, analytics)

**Updated Tier Features:**

**Basic (Free):**
- ✅ Profile listing
- ✅ Patient reviews
- ✅ Contact information
- ✅ Search visibility
- ✅ **Profile photo upload** ← NEW
- ❌ Verified badge
- ❌ Reply to reviews
- ❌ Analytics

**Premium (NPR 2,000/month):**
- ✅ All Basic features
- ✅ Verified badge
- ✅ Reply to reviews
- ✅ Profile analytics
- ✅ Priority support
- ✅ Edit profile details

**Featured (NPR 2,999/month):**
- ✅ All Premium features
- ✅ Featured placement
- ✅ Homepage visibility
- ✅ Top of search results
- ✅ Enhanced analytics
- ✅ Dedicated support

---

### 2. Clinic Menu Items Hidden

**What Was Visible:**
1. "Clinics" link in main navigation menu
2. "For Clinics" button next to "For Doctors" button
3. "Clinic Manager" dropdown menu item for users with role='clinic_manager'

**What Changed:**
All clinic menu items are now commented out in `templates/base.html`:
- Lines 61-67: Clinics navigation link (hidden)
- Lines 79-85: For Clinics button (hidden)
- Lines 117-122: Clinic Manager dropdown item (hidden)

**Why:**
- Simplify MVP launch
- Focus on individual doctors first
- Validate market before adding clinic complexity
- Wait for 50+ active doctors + 3 clinics expressing interest

---

### 3. What Happens If Someone Accesses Clinic Routes Now?

Even though menu items are hidden, the routes still exist and are functional:

#### Accessible Routes:
- `/clinics` - Public clinic listing
- `/clinic/<slug>` - Individual clinic profile
- `/clinic/manager` - Clinic manager login/signup
- `/clinic/manager/dashboard` - Clinic manager dashboard

#### Current Behavior:

**Scenario 1: Someone discovers `/clinics` URL**
- Page loads successfully
- Shows list of all clinics (probably empty if none created)
- Can view individual clinic profiles
- **Impact:** Low - just a listing page with no content

**Scenario 2: Someone discovers `/clinic/manager` URL**
- Page loads successfully
- Shows clinic manager signup/login form
- Can create clinic account and add doctors
- **Problem:** No pricing shown, could be confusing

**Scenario 3: User already has `role='clinic_manager'`**
- Can access full clinic manager dashboard
- Can manage multiple doctors
- Can see analytics
- **Problem:** No subscription enforcement yet

#### Recommendations:

**Option A: Leave As Silent Beta (CURRENT - Recommended)**
- Routes functional but not advertised
- Perfect for collecting 2-3 beta clinics naturally
- If someone asks, manually onboard as beta tester
- Fits your criteria: "50+ doctors + 3 interested clinics"

**Option B: Add "Beta" Warning Banner**
Add to clinic manager pages:
```html
<div class="alert alert-warning">
    <h5>⚠️ Beta Feature</h5>
    <p>Clinic management is in beta testing.
    Contact support@ranksewa.com for early access.</p>
</div>
```

**Option C: Disable Completely**
Add to `app.py`:
```python
@app.route('/clinic/manager')
def clinic_manager():
    abort(404)  # Pretend it doesn't exist
```

**Current Approach:** Option A - silent beta, manual onboarding if discovered

---

## Files Modified

1. `templates/pricing.html`
   - Changed Featured price: NPR 5,000 → NPR 2,999
   - Added photo upload to Basic tier features
   - Removed photo upload from Premium tier (since it's now in Basic)

2. `templates/base.html`
   - Commented out "Clinics" navigation link
   - Commented out "For Clinics" button
   - Commented out "Clinic Manager" dropdown menu item

3. `subscription_config.py`
   - Set `'can_upload_photos': True` for free tier (was False)
   - Set `'max_photos': 1` for free tier (was 0)
   - Added 'Profile photo upload' to free tier features list
   - Updated locked_features to clarify "Photo gallery (multiple photos)" is Premium+

4. `migrate_clinic_postgres.py` (NEW)
   - Consolidated clinic migration script
   - Creates all clinic tables in single run
   - Replaces local scripts: `init_db.py` and `migrate_add_clinic_support.py`

---

## Migration Script Created

**File:** `migrate_clinic_postgres.py`

**What It Does:**
1. Creates `clinics` table
2. Adds `clinic_id` column to `doctors` table
3. Creates `clinic_accounts` table
4. Creates `clinic_manager_doctors` junction table

**When to Run:**
Only run this when you're ready to re-enable clinic features (after 50+ active doctors).

**How to Run:**
```bash
# On DigitalOcean Console
python migrate_clinic_postgres.py
```

---

## Next Steps

### Before Launch (Immediate)
- [ ] Test pricing page displays correctly
- [ ] Verify no clinic menu items visible
- [x] Update code to allow photo upload in Basic tier
- [ ] Test photo upload in Basic tier works correctly
- [ ] Push all changes to production

### Photo Upload Code - ✅ COMPLETED
Updated `subscription_config.py` to allow photo uploads in Basic (free) tier:

**Changes made:**
```python
# Line 122: Changed from False to True
'can_upload_photos': True,  # Now allowed in Basic tier

# Line 126: Changed from 0 to 1
'max_photos': 1  # Allow 1 profile photo in Basic tier
```

**Also updated:**
- Added 'Profile photo upload' to free tier features list
- Updated locked_features: "Photo gallery (multiple photos)" clarifies Premium+ gets multiple photos

**Note:** The actual photo upload code in `app.py` (lines 2917-2936) doesn't enforce tier restrictions - it only uses `@doctor_required` decorator. This feature flag is now available for future enforcement if needed.

### After Launch
- Monitor if anyone discovers clinic routes
- Collect beta testers (aim for 3 clinics)
- Re-enable clinic features when criteria met (50+ doctors, 3+ clinics interested)

---

## How to Re-Enable Clinic Features Later

See `CLINIC_FEATURE_GUIDE.md` for full instructions.

**Quick steps:**
1. Uncomment sections in `templates/base.html` (lines 61-67, 79-85, 117-122)
2. Uncomment clinic pricing in `templates/pricing.html` (check git history)
3. Run `migrate_clinic_postgres.py` on production
4. Create sample clinics via `/admin/clinics/new`
5. Test full flow before announcing publicly

---

**Document Updated:** January 2, 2026
