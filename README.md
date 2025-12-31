# RateSewa - Doctor Directory Nepal

Find and rate the best doctors in Nepal!

## 🚀 Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
./run_dev.sh
# OR
python3 app.py

# Access at http://localhost:5000
```

## 📊 Current Status

- **29 unique doctors** across 12 major Nepali cities
- **12 medical specialties** available
- **Clean MVP** ready for launch
- **All core features** working

## 🔑 Login Credentials

### Admin Account
- **Email:** admin@ratesewa.com
- **Password:** admin123
- **⚠️ CHANGE PASSWORD BEFORE LAUNCH!**

### Test User
- **Email:** test@ratesewa.com
- **Password:** test123

## ✅ Recent Fixes (2025-12-31)

1. ✅ **Removed duplicate doctors** (36 → 29 unique)
2. ✅ **Fixed login** - Added email/password form
3. ✅ **Hidden advertisements** - Clean MVP interface
4. ✅ **Fixed navigation** - Login/logout now accessible
5. ✅ **Verified admin features** - All working correctly

## 🎯 Core Features

### For Users:
- Browse 29 doctors by city and specialty
- View detailed doctor profiles with ratings
- Rate and review doctors (requires login)
- Book appointments
- Send messages to doctors
- View appointment and rating history

### For Admins:
- Manage doctors (add, edit, deactivate)
- Manage cities and specialties
- Manage users (activate/deactivate)
- View and manage appointments
- Toggle featured doctor status

## 📁 Important Files

### Documentation:
- **LAUNCH_GUIDE.md** - Complete deployment guide
- **PRE_LAUNCH_CHECKLIST.md** - Critical pre-launch tasks
- **FIXES_APPLIED.md** - Duplicate removal & login fix
- **ADVERTISEMENT_FIXES.md** - Navigation & ad fixes

### Scripts:
- **run_dev.sh** - Development server
- **run_production.sh** - Production server (Gunicorn)
- **seed_data.py** - Populate database with doctors
- **remove_duplicates.py** - Clean duplicate entries
- **test_admin_users.py** - Test admin functionality

## 🏗️ Tech Stack

- **Backend:** Flask 3.1.2, SQLAlchemy 2.0
- **Database:** SQLite (dev) / PostgreSQL-ready
- **Frontend:** Bootstrap 5.3.0, jQuery 3.6.0
- **Auth:** Flask sessions + OAuth (Facebook)

## 📍 Cities Covered

Kathmandu, Pokhara, Lalitpur, Bhaktapur, Biratnagar, Dharan, Birgunj, Hetauda, Butwal, Bharatpur, Chitwan, Birtamod

## 🏥 Specialties Available

General Practitioner, Cardiologist, Dermatologist, Pediatrician, Gynecologist, Orthopedic, Neurologist, Psychiatrist, Ophthalmologist, ENT Specialist, Dentist, Ayurvedic Practitioner

## 🚀 Production Deployment

```bash
# Use production server
./run_production.sh

# Server runs on port 8000
# Configure nginx as reverse proxy
# Add SSL certificate (Let's Encrypt)
```

## ⚠️ Pre-Launch Checklist

- [ ] Change admin password
- [ ] Review all doctor profiles
- [ ] Test on mobile devices
- [ ] Set up domain and SSL
- [ ] Configure email (for notifications)
- [ ] Set up backups

## 📞 Support

For issues or questions, refer to the documentation files or check the codebase comments.

## 🎉 Ready for Tomorrow's Launch!

All core features are working, data is clean, and the interface is professional. Good luck with RateSewa! 🚀

---

**Last Updated:** 2025-12-31
**Version:** 1.0.0 (MVP)
