# NMC Doctor Import Plan - 40K Doctors

## Overview
You're importing 40,000 doctors from NMC website scraper data. This will be a huge increase from the current ~200 doctors.

**Current State:**
- ~200 doctors in database (manually added)
- No pagination implemented
- All doctors load on one page

**Target State:**
- 40,000+ doctors total
- Efficient pagination
- Fast search/filtering
- Skip duplicates by NMC number

---

## Phase 1: Data Import (Do This First)

### Step 1: Prepare Your CSV Data
Your NMC scraper CSV should have these columns (adjust import script if different):

```csv
nmc_number,name,city,specialty,education,workplace,phone
NMC12345,Dr. Ram Sharma,Kathmandu,Cardiology,MBBS MD,Tribhuvan Teaching Hospital,9841234567
NMC67890,Dr. Sita Thapa,Pokhara,Pediatrics,MBBS DCH,Manipal Hospital,9851234567
```

**Required columns:**
- `nmc_number` (unique identifier - prevents duplicates)
- `name`
- `city`
- `specialty`

**Optional columns:**
- `education`
- `workplace`
- `phone`

### Step 2: Test Import with Dry Run
First, test without actually importing:

```bash
python import_nmc_doctors.py \
  --file /Documents/scraper/nmc_doctors.csv \
  --batch-size 500 \
  --dry-run
```

This will:
- ✓ Show you what would be imported
- ✓ Validate data format
- ✓ Check for missing cities/specialties
- ✓ Count duplicates vs new records
- ✓ Identify data quality issues

### Step 3: Run Actual Import
Once dry run looks good:

```bash
python import_nmc_doctors.py \
  --file /Documents/scraper/nmc_doctors.csv \
  --batch-size 500
```

**Import Performance:**
- Batch size 500 = ~80 batches for 40K doctors
- Estimated time: 10-20 minutes (depending on server)
- Uses bulk inserts for performance
- Progress updates every 1000 rows

**What It Does:**
1. Skips doctors already in DB (by NMC number)
2. Creates missing cities automatically
3. Creates missing specialties automatically
4. Inserts in batches of 500 for speed
5. Shows progress and summary

---

## Phase 2: Database Optimization (After Import)

### Add Indexes for Fast Queries

Create this migration: `migrate_add_indexes_postgres.py`

```python
from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        conn = db.session.connection()

        # Index on nmc_number (already unique, but ensure it's indexed)
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_doctors_nmc_number
            ON doctors(nmc_number)
        """))

        # Index on city_id for filtering
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_doctors_city_id
            ON doctors(city_id)
        """))

        # Index on specialty_id for filtering
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_doctors_specialty_id
            ON doctors(specialty_id)
        """))

        # Index on is_active for filtering
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_doctors_is_active
            ON doctors(is_active)
        """))

        # Index on is_verified for filtering featured doctors
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_doctors_is_verified
            ON doctors(is_verified)
        """))

        # Composite index for common query (city + specialty + active)
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_doctors_city_specialty_active
            ON doctors(city_id, specialty_id, is_active)
        """))

        # Full-text search index on name
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_doctors_name_trgm
            ON doctors USING gin(name gin_trgm_ops)
        """))

        db.session.commit()
        print("✅ All indexes created successfully")

if __name__ == '__main__':
    run_migration()
```

Run on DigitalOcean: `python migrate_add_indexes_postgres.py`

---

## Phase 3: Implement Pagination (Critical!)

### Why Pagination is Essential:
- **40K doctors = huge page load time without pagination**
- **Browser will freeze rendering 40K rows**
- **Database query will be slow without LIMIT**
- **User experience will be terrible**

### Recommended Pagination Settings:

```python
# In app.py
DOCTORS_PER_PAGE = 20  # Show 20 doctors per page
```

### Update `/doctors` Route:

```python
@app.route('/doctors')
def doctors():
    page = request.args.get('page', 1, type=int)
    city_id = request.args.get('city_id', type=int)
    specialty_id = request.args.get('specialty_id', type=int)
    name_query = request.args.get('name', '').strip()

    # Base query
    query = Doctor.query.filter_by(is_active=True)

    # Apply filters
    if city_id:
        query = query.filter_by(city_id=city_id)
    if specialty_id:
        query = query.filter_by(specialty_id=specialty_id)
    if name_query:
        query = query.filter(Doctor.name.ilike(f'%{name_query}%'))

    # Pagination
    pagination = query.order_by(
        Doctor.is_verified.desc(),  # Verified first
        Doctor.profile_views.desc()  # Then by popularity
    ).paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    doctors = pagination.items

    return render_template('doctors.html',
                         doctors=doctors,
                         pagination=pagination,
                         cities=City.query.all(),
                         specialties=Specialty.query.all())
```

### Update `templates/doctors.html` with Pagination UI:

Add this after the doctor cards:

```html
<!-- Pagination -->
{% if pagination.pages > 1 %}
<nav aria-label="Doctor pagination" class="mt-4">
    <ul class="pagination justify-content-center">
        <!-- Previous -->
        <li class="page-item {% if not pagination.has_prev %}disabled{% endif %}">
            <a class="page-link" href="{{ url_for('doctors', page=pagination.prev_num, city_id=request.args.get('city_id'), specialty_id=request.args.get('specialty_id'), name=request.args.get('name')) }}">
                <i class="fas fa-chevron-left"></i> Previous
            </a>
        </li>

        <!-- Page numbers (show max 5 pages) -->
        {% for p in pagination.iter_pages(left_edge=1, right_edge=1, left_current=2, right_current=2) %}
            {% if p %}
                <li class="page-item {% if p == pagination.page %}active{% endif %}">
                    <a class="page-link" href="{{ url_for('doctors', page=p, city_id=request.args.get('city_id'), specialty_id=request.args.get('specialty_id'), name=request.args.get('name')) }}">
                        {{ p }}
                    </a>
                </li>
            {% else %}
                <li class="page-item disabled"><span class="page-link">...</span></li>
            {% endif %}
        {% endfor %}

        <!-- Next -->
        <li class="page-item {% if not pagination.has_next %}disabled{% endif %}">
            <a class="page-link" href="{{ url_for('doctors', page=pagination.next_num, city_id=request.args.get('city_id'), specialty_id=request.args.get('specialty_id'), name=request.args.get('name')) }}">
                Next <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    </ul>

    <!-- Results info -->
    <p class="text-center text-muted small">
        Showing {{ pagination.per_page * (pagination.page - 1) + 1 }} to
        {{ [pagination.per_page * pagination.page, pagination.total]|min }}
        of {{ pagination.total }} doctors
    </p>
</nav>
{% endif %}
```

---

## Phase 4: Update Homepage Stats (After Import)

The homepage shows doctor count:

```python
@app.route('/')
def index():
    total_doctors = Doctor.query.filter_by(is_active=True).count()
    # ... rest of code
```

After importing 40K doctors, this will show **40,000+ Doctors Listed** on homepage - great for social proof!

---

## Phase 5: Performance Monitoring

### After import, monitor:

1. **Database size:**
```sql
SELECT pg_size_pretty(pg_database_size('your_db_name'));
```

2. **Query performance:**
```sql
EXPLAIN ANALYZE
SELECT * FROM doctors
WHERE city_id = 1 AND specialty_id = 5
LIMIT 20;
```

Should be < 50ms with proper indexes.

3. **Page load time:**
- With pagination: Should load in < 1 second
- Without pagination: Will timeout/crash

---

## Data Quality Considerations

### Expect These Issues:

1. **Duplicate cities with different names:**
   - "Kathmandu" vs "Kathmandu Metropolitan City"
   - Solution: Normalize city names before import

2. **Specialty name variations:**
   - "Cardiology" vs "Cardiologist" vs "Heart Specialist"
   - Solution: Create mapping dictionary

3. **Missing data:**
   - Some doctors may have no phone/workplace
   - Solution: Script handles this with NULL values

4. **Inactive doctors:**
   - Some NMC registered doctors may have retired
   - Solution: All imported as is_active=True, is_verified=False
   - They can claim profile to update status

---

## Testing Checklist

Before going live:

- [ ] Dry run shows expected counts
- [ ] Pagination works on `/doctors` page
- [ ] Filters work (city, specialty, name search)
- [ ] Doctor profile pages load correctly
- [ ] Homepage stats update correctly
- [ ] Search is fast (< 1 second)
- [ ] No duplicate NMC numbers in database
- [ ] Database indexes created
- [ ] Page load time acceptable

---

## Rollback Plan

If something goes wrong:

### Option 1: Delete imported doctors
```sql
-- Delete all doctors without reviews (imported, not claimed)
DELETE FROM doctors
WHERE id IN (
    SELECT d.id FROM doctors d
    LEFT JOIN ratings r ON d.id = r.doctor_id
    WHERE r.id IS NULL AND d.is_verified = FALSE
);
```

### Option 2: Full database restore
Keep a backup before import:
```bash
# On DigitalOcean before import
pg_dump $DATABASE_URL > backup_before_nmc_import.sql
```

---

## Expected Results

**Before:**
- ~200 doctors
- 1 page loads everything
- Limited search results

**After:**
- ~40,000 doctors
- 2,000 pages (20 per page)
- Comprehensive coverage of Nepal
- Better SEO (more doctor pages = more content)
- More credibility (40K+ doctors listed!)

---

## Next Steps

1. **Today:** Test dry run with your CSV
2. **After dry run passes:** Run actual import (10-20 min)
3. **After import:** Add database indexes
4. **After indexes:** Implement pagination in app.py
5. **After pagination:** Update doctors.html template
6. **After UI update:** Test thoroughly
7. **Deploy:** Push to production

Let me know your CSV structure and I can adjust the import script!
