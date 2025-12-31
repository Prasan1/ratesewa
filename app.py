from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from sqlalchemy.orm import joinedload
import re
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from models import db, City, Specialty, Doctor, User, Rating, Appointment, ContactMessage, Advertisement
from config import Config
import ad_manager

# Load environment variables
load_dotenv()

# --- App Configuration ---
app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
db_url = os.environ.get('DATABASE_URL') or 'sqlite:///doctors.db'
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security configurations
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True when using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Initialize SQLAlchemy
db.init_app(app)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Initialize OAuth
oauth = OAuth(app)
facebook = oauth.register(
    name='facebook',
    client_id=os.environ.get('FACEBOOK_CLIENT_ID'),
    client_secret=os.environ.get('FACEBOOK_CLIENT_SECRET'),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/v19.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/v19.0/',
    client_kwargs={'scope': 'email,public_profile'}
)

# --- Authentication Decorators ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.clear()
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.clear()
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return redirect(url_for('login'))
        if not user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Helper Function for Slugs ---
def generate_slug(name):
    """Generates a URL-friendly slug from a name."""
    name = name.lower()
    name = re.sub(r'[^\w\s-]', '', name).strip()
    slug = re.sub(r'[-\s]+', '-', name)
    return slug

def admin_email_set():
    configured = app.config.get('ADMIN_EMAILS', set())
    if isinstance(configured, str):
        return {email.strip().lower() for email in configured.split(',') if email.strip()}
    if isinstance(configured, (list, tuple, set)):
        return {email.strip().lower() for email in configured if email.strip()}
    return set()

def is_admin_email(email):
    if not email:
        return False
    return email.strip().lower() in admin_email_set()

def generate_unique_slug(name, doctor_id=None):
    base_slug = generate_slug(name)
    slug = base_slug
    counter = 2
    while True:
        existing = Doctor.query.filter_by(slug=slug).first()
        if not existing or (doctor_id and existing.id == doctor_id):
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1

# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists.', 'danger')
            return redirect(url_for('register'))

        # Create new user
        user = User(name=name, email=email)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('login'))
            if is_admin_email(user.email) and not user.is_admin:
                user.is_admin = True
                db.session.commit()
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {user.name}!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/login/facebook')
def facebook_login():
    if not facebook.client_id or not facebook.client_secret:
        flash('Facebook login is not configured. Please contact the site admin.', 'warning')
        return redirect(url_for('login'))
    next_page = request.args.get('next')
    if next_page:
        session['oauth_next'] = next_page
    redirect_uri = url_for('facebook_callback', _external=True)
    return facebook.authorize_redirect(redirect_uri)

@app.route('/login/facebook/callback')
def facebook_callback():
    if not facebook.client_id or not facebook.client_secret:
        flash('Facebook login is not configured. Please contact the site admin.', 'warning')
        return redirect(url_for('login'))

    try:
        token = facebook.authorize_access_token()
    except Exception:
        flash('Facebook login failed. Please try again.', 'danger')
        return redirect(url_for('login'))

    if not token:
        flash('Facebook login failed. Please try again.', 'danger')
        return redirect(url_for('login'))

    profile_response = facebook.get('me?fields=id,name,email')
    profile = profile_response.json()

    email = profile.get('email')
    if not email:
        email = f"{profile.get('id')}@facebook.local"

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=profile.get('name') or 'Facebook User', email=email)
        user.set_password(os.urandom(16).hex())
        db.session.add(user)
        db.session.commit()

    if is_admin_email(user.email) and not user.is_admin:
        user.is_admin = True
        db.session.commit()

    if not user.is_active:
        flash('Your account has been deactivated. Please contact support.', 'danger')
        return redirect(url_for('login'))

    session['user_id'] = user.id
    session['user_name'] = user.name
    session['is_admin'] = user.is_admin
    flash(f'Welcome, {user.name}!', 'success')

    next_page = session.pop('oauth_next', None)
    return redirect(next_page or url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- SQLAlchemy Teardown ---
@app.teardown_appcontext
def shutdown_session(exception=None):
    """Remove database session at the end of request"""
    db.session.remove()


# --- Context Processor for Ads ---
@app.context_processor
def inject_ad_function():
    """Make ad manager function available to all templates"""
    return dict(get_ad=ad_manager.get_ad_for_position)

# --- Main App Routes ---
@app.route('/')
def index():
    cities = City.query.all()
    specialties = Specialty.query.all()
    sidebar_ad = ad_manager.get_ad_for_position('homepage_sidebar')
    return render_template('index.html', cities=cities, specialties=specialties, sidebar_ad=sidebar_ad)

@app.route('/clinics')
def clinics():
    return render_template('clinics.html')

@app.route('/doctors')
def get_doctors():
    city_id = request.args.get('city_id', '')
    specialty_id = request.args.get('specialty_id', '')

    # Build query with filters
    query = Doctor.query.filter_by(is_active=True)

    if city_id:
        query = query.filter(Doctor.city_id == int(city_id))

    if specialty_id:
        query = query.filter(Doctor.specialty_id == int(specialty_id))

    # Order by is_featured first, then avg_rating, then name
    # Note: We'll sort by avg_rating in Python since it's a property
    doctors = query.all()

    # Sort doctors: featured first, then by avg_rating, then by name
    doctors_sorted = sorted(doctors, key=lambda d: (-d.is_featured, -d.avg_rating, d.name))

    # Serialize to JSON
    doctors_list = [{
        'id': d.id,
        'name': d.name,
        'slug': d.slug,
        'city_id': d.city_id,
        'city_name': d.city.name,
        'specialty_id': d.specialty_id,
        'specialty_name': d.specialty.name,
        'experience': d.experience,
        'education': d.education,
        'college': d.college,
        'description': d.description,
        'photo_url': d.photo_url,
        'is_featured': d.is_featured,
        'is_verified': d.is_verified,
        'avg_rating': d.avg_rating,
        'rating_count': d.rating_count
    } for d in doctors_sorted]

    return jsonify(doctors_list)

@app.route('/admin/doctors')
@admin_required
def admin_doctors():
    query = Doctor.query.options(joinedload(Doctor.city), joinedload(Doctor.specialty))
    search = request.args.get('q', '').strip()
    if search:
        query = query.filter(Doctor.name.ilike(f"%{search}%"))
    doctors = query.order_by(Doctor.name.asc()).all()
    return render_template('admin_doctors.html', doctors=doctors, search=search)

@app.route('/admin/doctors/new', methods=['GET', 'POST'])
@admin_required
def admin_doctor_new():
    cities = City.query.order_by(City.name.asc()).all()
    specialties = Specialty.query.order_by(Specialty.name.asc()).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city_id = request.form.get('city_id')
        specialty_id = request.form.get('specialty_id')
        experience_raw = request.form.get('experience', '').strip()
        education = request.form.get('education', '').strip()
        college = request.form.get('college', '').strip()
        description = request.form.get('description', '').strip()
        photo_url = request.form.get('photo_url', '').strip()
        is_featured = bool(request.form.get('is_featured'))
        is_active = bool(request.form.get('is_active'))
        is_verified = bool(request.form.get('is_verified'))

        if not name or not city_id or not specialty_id:
            flash('Name, city, and specialty are required.', 'danger')
            return render_template('admin_doctor_form.html', doctor=None, cities=cities, specialties=specialties)

        experience = int(experience_raw) if experience_raw.isdigit() else None
        slug = generate_unique_slug(name)

        doctor = Doctor(
            name=name,
            slug=slug,
            city_id=int(city_id),
            specialty_id=int(specialty_id),
            experience=experience,
            education=education or None,
            college=college or None,
            description=description or None,
            photo_url=photo_url or None,
            is_featured=is_featured,
            is_active=is_active,
            is_verified=is_verified
        )
        db.session.add(doctor)
        db.session.commit()
        flash('Doctor added successfully.', 'success')
        return redirect(url_for('admin_doctors'))

    return render_template('admin_doctor_form.html', doctor=None, cities=cities, specialties=specialties)

@app.route('/admin/doctors/<int:doctor_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_doctor_edit(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    cities = City.query.order_by(City.name.asc()).all()
    specialties = Specialty.query.order_by(Specialty.name.asc()).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city_id = request.form.get('city_id')
        specialty_id = request.form.get('specialty_id')
        experience_raw = request.form.get('experience', '').strip()
        education = request.form.get('education', '').strip()
        college = request.form.get('college', '').strip()
        description = request.form.get('description', '').strip()
        photo_url = request.form.get('photo_url', '').strip()
        is_featured = bool(request.form.get('is_featured'))
        is_active = bool(request.form.get('is_active'))
        is_verified = bool(request.form.get('is_verified'))

        if not name or not city_id or not specialty_id:
            flash('Name, city, and specialty are required.', 'danger')
            return render_template('admin_doctor_form.html', doctor=doctor, cities=cities, specialties=specialties)

        if name != doctor.name:
            doctor.slug = generate_unique_slug(name, doctor_id=doctor.id)

        doctor.name = name
        doctor.city_id = int(city_id)
        doctor.specialty_id = int(specialty_id)
        doctor.experience = int(experience_raw) if experience_raw.isdigit() else None
        doctor.education = education or None
        doctor.college = college or None
        doctor.description = description or None
        doctor.photo_url = photo_url or None
        doctor.is_featured = is_featured
        doctor.is_active = is_active
        doctor.is_verified = is_verified

        db.session.commit()
        flash('Doctor updated successfully.', 'success')
        return redirect(url_for('admin_doctors'))

    return render_template('admin_doctor_form.html', doctor=doctor, cities=cities, specialties=specialties)

@app.route('/admin/doctors/<int:doctor_id>/status', methods=['POST'])
@admin_required
def admin_doctor_status(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    action = request.form.get('action', 'deactivate')
    doctor.is_active = action == 'activate'
    db.session.commit()
    if doctor.is_active:
        flash('Doctor reactivated successfully.', 'success')
    else:
        flash('Doctor deactivated successfully.', 'warning')
    return redirect(url_for('admin_doctors'))

@app.route('/admin/cities')
@admin_required
def admin_cities():
    cities = City.query.order_by(City.name.asc()).all()
    return render_template('admin_cities.html', cities=cities)

@app.route('/admin/cities/new', methods=['GET', 'POST'])
@admin_required
def admin_city_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('City name is required.', 'danger')
            return render_template('admin_city_form.html', city=None)

        city = City(name=name, description=description or None)
        db.session.add(city)
        db.session.commit()
        flash('City added successfully.', 'success')
        return redirect(url_for('admin_cities'))

    return render_template('admin_city_form.html', city=None)

@app.route('/admin/cities/<int:city_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_city_edit(city_id):
    city = City.query.get_or_404(city_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('City name is required.', 'danger')
            return render_template('admin_city_form.html', city=city)

        city.name = name
        city.description = description or None
        db.session.commit()
        flash('City updated successfully.', 'success')
        return redirect(url_for('admin_cities'))

    return render_template('admin_city_form.html', city=city)

@app.route('/admin/cities/<int:city_id>/delete', methods=['POST'])
@admin_required
def admin_city_delete(city_id):
    city = City.query.get_or_404(city_id)
    if Doctor.query.filter_by(city_id=city.id).count() > 0:
        flash('City cannot be deleted while doctors are assigned.', 'warning')
        return redirect(url_for('admin_cities'))

    db.session.delete(city)
    db.session.commit()
    flash('City deleted successfully.', 'success')
    return redirect(url_for('admin_cities'))

@app.route('/admin/specialties')
@admin_required
def admin_specialties():
    specialties = Specialty.query.order_by(Specialty.name.asc()).all()
    return render_template('admin_specialties.html', specialties=specialties)

@app.route('/admin/specialties/new', methods=['GET', 'POST'])
@admin_required
def admin_specialty_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Specialty name is required.', 'danger')
            return render_template('admin_specialty_form.html', specialty=None)

        specialty = Specialty(name=name, description=description or None)
        db.session.add(specialty)
        db.session.commit()
        flash('Specialty added successfully.', 'success')
        return redirect(url_for('admin_specialties'))

    return render_template('admin_specialty_form.html', specialty=None)

@app.route('/admin/specialties/<int:specialty_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_specialty_edit(specialty_id):
    specialty = Specialty.query.get_or_404(specialty_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Specialty name is required.', 'danger')
            return render_template('admin_specialty_form.html', specialty=specialty)

        specialty.name = name
        specialty.description = description or None
        db.session.commit()
        flash('Specialty updated successfully.', 'success')
        return redirect(url_for('admin_specialties'))

    return render_template('admin_specialty_form.html', specialty=specialty)

@app.route('/admin/specialties/<int:specialty_id>/delete', methods=['POST'])
@admin_required
def admin_specialty_delete(specialty_id):
    specialty = Specialty.query.get_or_404(specialty_id)
    if Doctor.query.filter_by(specialty_id=specialty.id).count() > 0:
        flash('Specialty cannot be deleted while doctors are assigned.', 'warning')
        return redirect(url_for('admin_specialties'))

    db.session.delete(specialty)
    db.session.commit()
    flash('Specialty deleted successfully.', 'success')
    return redirect(url_for('admin_specialties'))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.name.asc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<int:user_id>/status', methods=['POST'])
@admin_required
def admin_user_status(user_id):
    if session.get('user_id') == user_id:
        flash('You cannot change your own account status while logged in.', 'warning')
        return redirect(url_for('admin_users'))

    user = User.query.get_or_404(user_id)
    action = request.form.get('action', 'deactivate')
    user.is_active = action == 'activate'
    db.session.commit()
    if user.is_active:
        flash('User reactivated successfully.', 'success')
    else:
        flash('User deactivated successfully.', 'warning')
    return redirect(url_for('admin_users'))

# --- Admin Route: Toggle Featured Status ---
@app.route('/admin/toggle_featured/<int:doctor_id>')
@admin_required
def toggle_featured(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if doctor:
        doctor.is_featured = not doctor.is_featured
        db.session.commit()
        flash(f"Doctor's featured status has been updated.", 'info')
    else:
        flash('Doctor not found.', 'danger')
    return redirect(url_for('index'))

# --- DOCTOR PROFILE ROUTE (USES SLUG) ---
@app.route('/doctor/<slug>')
def doctor_profile(slug):
    # Query doctor by slug with eager loading to avoid N+1 queries
    from sqlalchemy.orm import joinedload

    doctor = Doctor.query.options(
        joinedload(Doctor.ratings).joinedload(Rating.user),
        joinedload(Doctor.specialty),
        joinedload(Doctor.city)
    ).filter(Doctor.slug == slug, Doctor.is_active.is_(True)).first()

    if not doctor:
        flash('Doctor not found.', 'danger')
        return redirect(url_for('index'))

    # Get ratings sorted by ID descending
    ratings = sorted(doctor.ratings, key=lambda r: r.id, reverse=True)

    # Calculate average rating (use property)
    avg_rating = doctor.avg_rating

    # Get ads for this page
    banner_ad = ad_manager.get_ad_for_position('profile_top',
                                                specialty_id=doctor.specialty_id,
                                                city_id=doctor.city_id)
    inline_ad = ad_manager.get_ad_for_position('profile_inline',
                                                specialty_id=doctor.specialty_id)

    return render_template('doctor_profile.html', doctor=doctor, ratings=ratings, avg_rating=avg_rating, banner_ad=banner_ad, inline_ad=inline_ad)

@app.route('/rate_doctor', methods=['POST'])
@login_required
def rate_doctor():
    doctor_id = request.form.get('doctor_id')
    rating_value = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session['user_id']

    if not doctor_id or not rating_value:
        flash('Please provide a rating.', 'danger')
        return redirect(url_for('index'))

    existing_rating = Rating.query.filter_by(
        doctor_id=doctor_id,
        user_id=user_id
    ).first()

    if existing_rating:
        flash('You have already reviewed this doctor.', 'warning')
        doctor = Doctor.query.get(doctor_id)
        return redirect(url_for('doctor_profile', slug=doctor.slug))

    try:
        rating_value = int(rating_value)
    except (TypeError, ValueError):
        flash('Please provide a valid rating.', 'danger')
        doctor = Doctor.query.get(doctor_id)
        return redirect(url_for('doctor_profile', slug=doctor.slug))

    if rating_value < 1 or rating_value > 5:
        flash('Ratings must be between 1 and 5 stars.', 'warning')
        doctor = Doctor.query.get(doctor_id)
        return redirect(url_for('doctor_profile', slug=doctor.slug))

    # Create new rating
    new_rating = Rating(
        doctor_id=doctor_id,
        user_id=user_id,
        rating=rating_value,
        comment=comment
    )
    db.session.add(new_rating)
    db.session.commit()
    flash('Your review has been submitted!', 'success')

    # Get the doctor's slug to redirect correctly
    doctor = Doctor.query.get(doctor_id)
    return redirect(url_for('doctor_profile', slug=doctor.slug))

@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    doctor_id = request.form.get('doctor_id')
    appointment_date = request.form.get('appointment_date')
    appointment_time = request.form.get('appointment_time')
    message = request.form.get('message')
    user_id = session['user_id']

    # Create new appointment
    appointment = Appointment(
        doctor_id=doctor_id,
        user_id=user_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        message=message,
        status='pending'
    )
    db.session.add(appointment)
    db.session.commit()

    # Get doctor's slug to redirect correctly
    doctor = Doctor.query.get(doctor_id)

    flash('Your appointment request has been sent successfully!', 'success')
    return redirect(url_for('doctor_profile', slug=doctor.slug))

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    doctor_id = request.form.get('doctor_id')
    message = request.form.get('message')
    user_id = session['user_id']

    # Get user's name and email
    user = User.query.get(user_id)

    # Create new contact message
    contact_message = ContactMessage(
        doctor_id=doctor_id,
        user_id=user_id,
        name=user.name,
        email=user.email,
        message=message
    )
    db.session.add(contact_message)
    db.session.commit()

    # Get doctor's slug to redirect correctly
    doctor = Doctor.query.get(doctor_id)

    flash('Your message has been sent to the doctor!', 'success')
    return redirect(url_for('doctor_profile', slug=doctor.slug))


# --- Advertisement Routes ---
@app.route('/ad/click/<int:ad_id>')
def ad_click(ad_id):
    """Track ad click and redirect to advertiser URL"""
    ad = Advertisement.query.get(ad_id)
    if ad:
        ad_manager.track_ad_click(ad_id)
        return redirect(ad.link_url)
    else:
        flash('Advertisement not found.', 'danger')
        return redirect(url_for('index'))


@app.route('/ad/impression/<int:ad_id>', methods=['POST'])
def ad_impression(ad_id):
    """Track ad impression"""
    success = ad_manager.track_ad_impression(ad_id)
    return jsonify({'success': success})


# --- Admin Appointment Management Routes ---
@app.route('/admin/appointments')
@admin_required
def admin_appointments():
    """View all appointments for admin"""
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    return render_template('admin_appointments.html', appointments=appointments)


@app.route('/admin/appointment/<int:appointment_id>/confirm')
@admin_required
def confirm_appointment(appointment_id):
    """Confirm an appointment"""
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = 'confirmed'
        db.session.commit()
        flash(f'Appointment #{appointment_id} has been confirmed.', 'success')
    else:
        flash('Appointment not found.', 'danger')
    return redirect(url_for('admin_appointments'))


@app.route('/admin/appointment/<int:appointment_id>/cancel')
@admin_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = 'cancelled'
        db.session.commit()
        flash(f'Appointment #{appointment_id} has been cancelled.', 'success')
    else:
        flash('Appointment not found.', 'danger')
    return redirect(url_for('admin_appointments'))


# --- User Profile Route ---
@app.route('/profile')
@login_required
def user_profile():
    """View user's own appointments and ratings"""
    user_id = session['user_id']
    user = User.query.get(user_id)

    # Get user's appointments
    appointments = Appointment.query.filter_by(user_id=user_id).order_by(Appointment.created_at.desc()).all()

    # Get user's ratings
    ratings = Rating.query.filter_by(user_id=user_id).order_by(Rating.created_at.desc()).all()

    return render_template('user_profile.html', user=user, appointments=appointments, ratings=ratings)

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user's password"""
    user_id = session['user_id']
    user = User.query.get(user_id)

    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    # Validate current password
    if not user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('user_profile'))

    # Validate new password
    if len(new_password) < 6:
        flash('New password must be at least 6 characters long.', 'danger')
        return redirect(url_for('user_profile'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('user_profile'))

    # Update password
    user.set_password(new_password)
    db.session.commit()

    flash('Password changed successfully!', 'success')
    return redirect(url_for('user_profile'))


if __name__ == '__main__':
    app.run(debug=True)
