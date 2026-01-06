# Doctor Import Summary - January 5, 2026

## Overview

Successfully imported **73 new doctors** from hospital website scraping into the local database.

### Database Statistics
- **Before import:** 23,997 doctors
- **After import:** 24,070 doctors
- **Doctors added:** 73
- **Doctors excluded:** 3 (non-medical professionals)

---

## Import Breakdown by Hospital

### Om Hospital - 45 doctors
High-value senior consultants and professors across multiple specialties.

**Notable additions:**
- **19 Professors** including:
  - Prof. Dr. A.K. Jha (ENT)
  - Prof. Dr. Pushpa Prasad Sharma (Psychiatry)
  - Prof. Dr. Pawan Kumar Sultaniya (Neurosurgery)
  - Prof. Dr. Chandramani Poudel (Interventional Cardiology)
  - Prof. Dr. Nabees M.S. Pradhan (Orthopedic Surgery/Sports Medicine)

**Specialties covered:**
- ENT, Psychiatry, Neurosurgery, Neurology
- Cardiology, Gastroenterology, Nephrology
- Obstetrics & Gynecology, Pediatrics
- Oncology, Urology, Dermatology
- Orthopedics, Internal Medicine, Anesthesiology

**Verification status:** All added without NMC numbers (will need verification later)

---

### B&B Hospital - 23 doctors
Major orthopedic and surgical specialists.

**Notable additions:**
- Prof. Dr. Ashok Kumar Banskota (Orthopedic Surgery - Chief)
- Prof. Dr. Jagdish Lal Baidya (General & Laparoscopic Surgery - Chief)
- Prof. Dr. Kundu Yangzom (Obstetrics & Gynecology)
- Prof. Dr. Sudarshan Narsingh Pradhan (Psychiatry)
- Prof. Dr. Dwarika Prasad Shrestha (Dermatology)

**Specialties covered:**
- Orthopedics (4 doctors including spine and arthroscopy subspecialties)
- General Surgery (4 doctors)
- Cardiology (3 doctors)
- Oncology (2 doctors: Gynecologic and Medical)
- ENT (2 doctors)
- Obstetrics & Gynecology, Pulmonology, Hepatology
- Plastic Surgery, Psychiatry, Dermatology, Anesthesiology

**Verification status:** All added without NMC numbers

---

### DISHARC (DI Skin Hospital) - 2 doctors ✅
**HIGH PRIORITY - Have NMC numbers**

1. **Asst. Prof. Dr. Bishal Karki**
   - NMC: 6863
   - Specialty: Plastic & Cosmetic Surgery
   - Status: ✅ Added with NMC number

2. **Assoc. Prof. Dr. Suchana Marahatta**
   - NMC: 8368
   - Specialty: Aesthetic Dermatology (mapped to Dermatology)
   - Status: ✅ Added with NMC number

---

### STEM Center KTM - 1 doctor ✅
**HIGH PRIORITY - Has NMC number**

1. **Dr. Kristi Gupta**
   - NMC: 30126
   - Specialty: Dental Surgery (mapped to Dentistry)
   - Education: Bachelor of Dental Surgery (Chitwan Medical College, TU)
   - Status: ✅ Added with NMC number

---

### Kantipur Hospital - 2 doctors
Minimal information available.

1. Dr. Avesh Koirala (General Practice)
2. Dr. Rohit Chaudhary (General Practice)

**Note:** These doctors had no specialty information on the hospital website, defaulted to General Practice. May need individual profile scraping for more details.

---

## New Specialties Created

The following new specialty categories were created during import:

1. **Dentistry** (for dental surgeons)
2. **Plastic Surgery** (for plastic & cosmetic surgeons)
3. **Obstetrics and Gynecology** (standardized from various OB/GYN variations)
4. **Internal Medicine** (for general internal medicine doctors)
5. **Neurology** (distinct from Neurosurgery)
6. **Gastroenterology** (for GI specialists and hepatologists)
7. **General & GI Surgery** (for combined surgical practices)
8. **Orthopedic Surgery/Sports Medicine & Shoulder Surgery** (subspecialty)
9. **Oncology** (consolidated from surgical, medical, gynecologic oncology)
10. **General Practice** (for doctors without specified specialty)
11. **Endocrinology** (for endocrine specialists)
12. **Ophthalmology/Neuro-ophthalmology** (for eye specialists)
13. **General & Laparoscopic Surgery (Chief)** (for department chiefs)
14. **ENT (Head & Neck/Allergy Specialist)** (subspecialty)

---

## Specialty Mapping Applied

The import script automatically mapped hospital specialty descriptions to standard categories:

- "Dental Surgery" → Dentistry
- "Plastic & Cosmetic Surgery" → Plastic Surgery
- "Aesthetic Dermatology" → Dermatology
- "Orthopedic Surgery (Spine/Arthroscopy)" → Orthopedics
- "General & Laparoscopic Surgery" → General Surgery
- "IVF & Reproductive Medicine" → Obstetrics and Gynecology
- "ENT Head and Neck Surgery" → ENT
- "Surgical/Medical/Gynecologic Oncology" → Oncology
- "Internal Medicine & Cardiology" → Cardiology
- And many more...

---

## Data Quality Summary

### Doctors with NMC Numbers (Ready for Verification)
**3 doctors (4.1%)**
- Dr. Kristi Gupta - NMC 30126
- Dr. Bishal Karki - NMC 6863
- Dr. Suchana Marahatta - NMC 8368

These doctors can be verified immediately and marked as "RankSewa Verified."

### Doctors without NMC Numbers
**70 doctors (95.9%)**

These doctors will need:
1. Manual NMC number lookup from Nepal Medical Council website
2. Cross-verification before marking as verified
3. Self-verification when doctors claim their profiles

### Excluded (Non-doctors)
**3 entries**
- Bhupal Baniya (Nutritionist)
- Pt. Pravin Yadav (Physiotherapist)
- Pt. Sumi Shakya (Physiotherapist)

---

## City/Location Assignment

All doctors assigned to cities based on hospital location:
- **STEM Center** → Kathmandu
- **Om Hospital** → Chabahil
- **B&B Hospital** → Gwarko
- **Kantipur Hospital** → Kathmandu
- **DISHARC** → Kathmandu

---

## Potential Data Issues

### Possible Duplicates (Flagged in Scraping Report)
Two doctors appeared in multiple hospitals and should be verified:

1. **Dr. Bajrang Kumar Rauniyar**
   - Appears in: STEM Center (NMC: 6895) AND Om Hospital (no NMC)
   - Resolution: Only the Om Hospital version was added (STEM Center version already in DB)
   - Action needed: Verify if same person working at both hospitals

2. **Dr. Deepak Raj Pandey**
   - Appears in: STEM Center (NMC: 5257) AND Om Hospital (no NMC)
   - Resolution: Only the Om Hospital version was added (STEM Center version already in DB)
   - Action needed: Verify if same person working at both hospitals

---

## Files Generated

1. **hospital_scraping_report.md** - Detailed scraping analysis
2. **NEW_DOCTORS_LIST.md** - Complete list of 76 scraped doctors
3. **new_doctors.csv** - CSV format of all scraped doctors (77 rows including header)
4. **import_new_doctors.py** - Import script
5. **IMPORT_SUMMARY_2026-01-05.md** - This summary report

---

## Next Steps

### Immediate (Production Deployment)
When these changes are deployed to production:
1. ✅ Run existing pending production scripts:
   - `python3 add_external_clinic_url.py`
   - `python3 fix_articles_production.py`
   - `python3 fix_uppercase_names_production.py`

2. ✅ Run new import on production:
   - Transfer `new_doctors.csv` and `import_new_doctors.py` to production
   - Run: `python3 import_new_doctors.py --live`
   - Note: Production may have more/fewer doctors to import depending on its current state

### High Priority (This Week)
1. **Verify the 3 doctors with NMC numbers:**
   - Use `verify_nmc_number.py` to confirm:
     ```bash
     python3 verify_nmc_number.py 30126 "Dr. Kristi Gupta"
     python3 verify_nmc_number.py 6863 "Dr. Bishal Karki"
     python3 verify_nmc_number.py 8368 "Dr. Suchana Marahatta"
     ```
   - If verified, mark as verified in admin panel

2. **NMC Lookup for High-Value Doctors:**
   - Start with 19 Om Hospital professors (senior consultants)
   - Then B&B Hospital consultants (23 doctors)
   - Use NMC website: https://www.nmc.org.np/

3. **Resolve Potential Duplicates:**
   - Verify Dr. Bajrang Kumar Rauniyar (NMC 6895)
   - Verify Dr. Deepak Raj Pandey (NMC 5257)

### Medium Priority
4. **Failed Hospital Scrapes:**
   - Norvic Hospital: Set up browser automation (Selenium/Puppeteer)
   - Grande Hospital: Contact IT about SSL certificate issue

5. **Kantipur Hospital Details:**
   - Scrape individual profile pages for Dr. Avesh Koirala and Dr. Rohit Chaudhary
   - Get proper specialty information

### Future Enhancements
6. **Automated NMC Verification:**
   - Consider building NMC website scraper for automated verification
   - Would help with bulk verification of the 70 doctors without NMC numbers

7. **Regular Hospital Scraping:**
   - Set up monthly scraping schedule
   - Monitor for new doctors added to hospital websites

---

## Technical Notes

### Import Script Features
- ✅ Duplicate detection by NMC number and normalized name
- ✅ Automatic slug generation with uniqueness checking
- ✅ Specialty mapping and normalization
- ✅ City assignment based on hospital location
- ✅ Exclusion of non-medical professionals
- ✅ Dry-run mode for safe testing
- ✅ Detailed reporting and logging

### Database Changes
- No schema changes required
- All new doctors use existing table structure
- New specialty records created as needed
- All doctors added with `is_verified=False`, `is_featured=False`

---

## Summary Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Scraped** | 76 | 100% |
| **Successfully Added** | 73 | 96.1% |
| **Excluded (Non-doctors)** | 3 | 3.9% |
| **With NMC Numbers** | 3 | 4.1% of added |
| **Without NMC Numbers** | 70 | 95.9% of added |
| **From Om Hospital** | 45 | 61.6% of added |
| **From B&B Hospital** | 23 | 31.5% of added |
| **From DISHARC** | 2 | 2.7% of added |
| **From STEM Center** | 1 | 1.4% of added |
| **From Kantipur** | 2 | 2.7% of added |

---

## Impact on Database

### Before Import
- Total doctors: 23,997
- Database size: ~23k doctors in dev, ~27k in production

### After Import (Local)
- Total doctors: 24,070
- New doctors: +73 (+0.3% growth)
- New specialties: +14

### Expected Production Impact
- Production database (27k doctors) may already have some of these doctors
- Duplicate detection will prevent re-adding existing doctors
- Estimated addition: 50-73 doctors (depending on production data freshness)

---

**Import completed:** January 5, 2026
**Script:** import_new_doctors.py
**Executed by:** Claude Code (Sonnet 4.5)
