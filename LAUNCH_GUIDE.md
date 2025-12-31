# RateSewa - Doctor Directory Nepal
## Quick Launch Guide

### What is RateSewa?
RateSewa is a minimal doctor directory platform for Nepal where users can:
- Find doctors by city and specialty
- Read and write reviews and ratings
- Book appointments with doctors
- Send messages to doctors

### Current Database
- **36 Doctors** across 12 major Nepali cities
- **12 Specialties** including General Practitioner, Cardiologist, Pediatrician, etc.
- **12 Cities** including Kathmandu, Pokhara, Lalitpur, Biratnagar, and more

---

## Running the Application

### Prerequisites
- Python 3.8+
- Virtual environment already set up in `.venv`

### Quick Start

1. **Activate virtual environment:**
```bash
source .venv/bin/activate
```

2. **Run the application:**
```bash
python3 app.py
# OR
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

3. **Access the application:**
```
http://localhost:5000
```

---

## Login Credentials

### Admin Account
- **Email:** admin@ratesewa.com
- **Password:** admin123
- **Access:** Full admin panel for managing doctors, cities, specialties, users, appointments

### Test User Account
- **Email:** test@ratesewa.com
- **Password:** test123
- **Access:** Regular user with ability to rate doctors, book appointments

---

## Key Features Implemented

### For Users:
- Browse doctors by city and specialty
- View detailed doctor profiles
- Rate and review doctors (1-5 stars)
- Book appointments
- Send messages to doctors
- User profile showing appointment history and reviews

### For Admins:
- Manage doctors (add, edit, deactivate)
- Manage cities and specialties
- Manage users
- View and manage appointments
- Toggle featured doctor status

### Hidden for MVP:
- "For Clinics" premium listing section (can be enabled later)

---

## Database Management

### Current Database
The SQLite database is located at: `instance/doctors.db`

### Re-seed Database (if needed)
```bash
python3 seed_data.py
```

This will add additional doctors if not already present without duplicating data.

---

## Project Structure

```
doctor_directory/
├── app.py                  # Main Flask application
├── models.py               # Database models
├── database.py             # Database initialization
├── config.py               # Configuration
├── seed_data.py            # Database seeding script
├── .env                    # Environment variables (secret key)
├── instance/
│   └── doctors.db          # SQLite database
├── templates/              # HTML templates
│   ├── base.html           # Base template with RateSewa branding
│   ├── index.html          # Homepage
│   ├── doctor_profile.html # Doctor profile page
│   └── admin_*.html        # Admin pages
└── static/
    ├── css/
    │   └── style.css       # Custom styles
    └── js/
        └── main.js         # JavaScript
```

---

## Production Deployment Notes

### Before Going Live:

1. **Change Secret Key:**
   Edit `.env` and generate a new secret key

2. **Use Production WSGI Server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

3. **Database:**
   - For production, consider migrating to PostgreSQL
   - Current SQLite works fine for MVP

4. **HTTPS:**
   - Deploy behind nginx with SSL certificate
   - Set `SESSION_COOKIE_SECURE=True` in `.env`

5. **Change Admin Password:**
   Use the admin panel to change the default admin password

6. **Environment Variables:**
   - Never commit `.env` to version control
   - Set environment-specific variables on production server

---

## Facebook Login (HIGHLY RECOMMENDED for Nepal!)

**Current Status:**
- ✅ Facebook login is fully implemented and ready
- ⚠️ Facebook credentials NOT configured yet
- 📱 Button visible on login page (shows warning when clicked)

**Why Enable This:**
- Facebook has 9+ million users in Nepal
- Increases user signups significantly
- Most Nepali users prefer Facebook login
- One-click registration without passwords

**Quick Setup (10-15 minutes):**
1. Create Facebook App at https://developers.facebook.com/apps/
2. Get App ID and App Secret
3. Add to `.env`:
   ```env
   FACEBOOK_CLIENT_ID=your_app_id
   FACEBOOK_CLIENT_SECRET=your_app_secret
   ```
4. Restart server

**📖 Complete Guide:** See `FACEBOOK_LOGIN_SETUP.md` for detailed step-by-step instructions.

**Note:** You can launch without Facebook login, but enabling it is HIGHLY recommended for Nepal market!

---

## Domain Configuration

The app is designed for **ratesewa** domain. Update the following if using different domain:
- `.env` file (if deploying with different base URL)
- Email templates (when implemented)

---

## Support

For issues or questions, refer to the code comments or contact the development team.

---

## What's Hidden for MVP

The following features exist in the code but are currently hidden:
- "For Clinics" navigation link and premium listing page
- Advertisement system (fully functional but not actively used)

These can be enabled later by uncommenting in `templates/base.html`.

---

## Next Steps for Future Releases

1. Email notifications for appointments
2. Doctor dashboard for managing their profiles
3. Advanced search filters
4. Pagination for doctor lists
5. Payment integration for premium listings
6. SMS notifications
7. Doctor availability calendar
8. Enable "For Clinics" premium features

---

## Technical Stack

- **Backend:** Flask 3.1.2
- **Database:** SQLAlchemy + SQLite
- **Frontend:** Bootstrap 5.3.0 + jQuery
- **Authentication:** Flask sessions + OAuth (Facebook)
- **Icons:** Font Awesome 6.0

---

**Ready to launch! Good luck with RateSewa!**
