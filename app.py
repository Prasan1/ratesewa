from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from sqlalchemy.orm import joinedload
import re
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from models import db, City, Specialty, Doctor, User, Rating, Appointment, ContactMessage, Advertisement, VerificationRequest, DoctorResponse
from config import Config
import ad_manager
import upload_utils
import stripe
import subscription_config
import promo_config

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

# File upload configurations
app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png'}

# Initialize SQLAlchemy
db.init_app(app)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Initialize OAuth
oauth = OAuth(app)

# Facebook OAuth
facebook = oauth.register(
    name='facebook',
    client_id=os.environ.get('FACEBOOK_CLIENT_ID'),
    client_secret=os.environ.get('FACEBOOK_CLIENT_SECRET'),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/v19.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/v19.0/',
    client_kwargs={'scope': 'email,public_profile'}
)

# Google OAuth
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Stripe Payment Configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

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


def doctor_required(f):
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
        if user.role != 'doctor' or not user.doctor_id:
            flash('Doctor access required. Please claim your profile first.', 'warning')
            return redirect(url_for('claim_profile'))
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
            session['role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')

            next_page = request.values.get('next')
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

    # Ensure user has a role (fix for users created before migration)
    if not user.role:
        user.role = 'patient'
        db.session.commit()

    session['user_id'] = user.id
    session['user_name'] = user.name
    session['is_admin'] = user.is_admin
    session['role'] = user.role
    flash(f'Welcome, {user.name}!', 'success')

    next_page = session.pop('oauth_next', None)
    return redirect(next_page or url_for('index'))

@app.route('/login/google')
def google_login():
    if not google.client_id or not google.client_secret:
        flash('Google login is not configured. Please contact the site admin.', 'warning')
        return redirect(url_for('login'))
    next_page = request.args.get('next')
    if next_page:
        session['oauth_next'] = next_page
    redirect_uri = url_for('google_authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorized')
def google_authorized():
    if not google.client_id or not google.client_secret:
        flash('Google login is not configured. Please contact the site admin.', 'warning')
        return redirect(url_for('login'))

    try:
        token = google.authorize_access_token()
    except Exception as e:
        flash('Google login failed. Please try again.', 'danger')
        return redirect(url_for('login'))

    if not token:
        flash('Google login failed. Please try again.', 'danger')
        return redirect(url_for('login'))

    # Get user info from Google
    user_info = token.get('userinfo')
    if not user_info:
        flash('Failed to get user information from Google.', 'danger')
        return redirect(url_for('login'))

    email = user_info.get('email')
    name = user_info.get('name') or 'Google User'

    if not email:
        flash('Email not provided by Google. Please try again.', 'danger')
        return redirect(url_for('login'))

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create new user
        user = User(name=name, email=email)
        user.set_password(os.urandom(16).hex())  # Random password for OAuth users
        db.session.add(user)
        db.session.commit()

    # Check if user is admin
    if is_admin_email(user.email) and not user.is_admin:
        user.is_admin = True
        db.session.commit()

    # Check if user is active
    if not user.is_active:
        flash('Your account has been deactivated. Please contact support.', 'danger')
        return redirect(url_for('login'))

    # Log user in
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['is_admin'] = user.is_admin
    session['role'] = user.role
    flash(f'Welcome, {user.name}!', 'success')

    next_page = session.pop('oauth_next', None)
    return redirect(next_page or url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

# --- Doctor Verification Routes ---
@app.route('/claim-profile', methods=['GET'])
def claim_profile():
    """Search for unclaimed doctor profiles"""
    search_query = request.args.get('search', '').strip()
    unclaimed_doctors = []

    if search_query:
        # Find doctors without a linked user account
        unclaimed_doctors = Doctor.query.outerjoin(User, User.doctor_id == Doctor.id)\
            .filter(Doctor.name.ilike(f'%{search_query}%'))\
            .filter(User.id.is_(None))\
            .filter(Doctor.is_active == True)\
            .all()

    return render_template('claim_profile_search.html',
                          search_query=search_query,
                          unclaimed_doctors=unclaimed_doctors)


@app.route('/claim-profile/<int:doctor_id>', methods=['GET'])
@login_required
def claim_profile_form(doctor_id):
    """Show verification form for claiming a doctor profile"""
    doctor = Doctor.query.get_or_404(doctor_id)

    # Check if doctor is already claimed
    if doctor.user_account:
        flash('This profile has already been claimed.', 'warning')
        return redirect(url_for('claim_profile'))

    # Check if user already has a pending verification request for this doctor
    existing_request = VerificationRequest.query.filter_by(
        doctor_id=doctor_id,
        user_id=session['user_id'],
        status='pending'
    ).first()

    if existing_request:
        flash('You already have a pending verification request for this profile.', 'info')
        return redirect(url_for('claim_profile'))

    # Get all cities for the dropdown
    cities = City.query.order_by(City.name).all()

    return render_template('claim_profile_form.html',
                          doctor=doctor,
                          cities=cities,
                          current_user=User.query.get(session['user_id']))


@app.route('/claim-profile/<int:doctor_id>/submit', methods=['POST'])
@login_required
def claim_profile_submit(doctor_id):
    """Process verification request submission"""
    doctor = Doctor.query.get_or_404(doctor_id)

    # Check if doctor is already claimed
    if doctor.user_account:
        flash('This profile has already been claimed.', 'warning')
        return redirect(url_for('claim_profile'))

    try:
        # Get form data
        nmc_number = request.form.get('nmc_number', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        email = request.form.get('email', '').strip()
        practice_address = request.form.get('practice_address', '').strip()
        practice_city_id = request.form.get('practice_city_id')

        # Validate required fields
        if not all([nmc_number, phone_number, email, practice_address, practice_city_id]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('claim_profile_form', doctor_id=doctor_id))

        # Handle file uploads
        medical_degree = request.files.get('medical_degree')
        govt_id = request.files.get('govt_id')
        practice_license = request.files.get('practice_license')

        # Validate required file uploads
        if not medical_degree or not govt_id:
            flash('Medical degree and government ID are required.', 'danger')
            return redirect(url_for('claim_profile_form', doctor_id=doctor_id))

        # Save files
        upload_folder = app.config['UPLOAD_FOLDER']
        medical_degree_path = upload_utils.save_verification_document(
            medical_degree, upload_folder, doctor_id, 'medical_degree'
        )
        govt_id_path = upload_utils.save_verification_document(
            govt_id, upload_folder, doctor_id, 'govt_id'
        )

        # Optional practice license
        practice_license_path = None
        if practice_license and practice_license.filename:
            practice_license_path = upload_utils.save_verification_document(
                practice_license, upload_folder, doctor_id, 'practice_license'
            )

        # Create verification request
        verification_request = VerificationRequest(
            doctor_id=doctor_id,
            user_id=session['user_id'],
            nmc_number=nmc_number,
            phone_number=phone_number,
            email=email,
            practice_address=practice_address,
            practice_city_id=practice_city_id,
            medical_degree_path=medical_degree_path,
            govt_id_path=govt_id_path,
            practice_license_path=practice_license_path,
            email_verified=True,  # Email is already verified through user account
            status='pending'
        )

        db.session.add(verification_request)
        db.session.commit()

        flash('Verification request submitted successfully! Our admin team will review it within 2-3 business days.', 'success')
        return redirect(url_for('user_profile'))

    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('claim_profile_form', doctor_id=doctor_id))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while processing your request: {str(e)}', 'danger')
        return redirect(url_for('claim_profile_form', doctor_id=doctor_id))


@app.route('/doctor/self-register', methods=['GET'])
@login_required
def doctor_self_register():
    """Show self-registration form for doctors not in the database"""
    cities = City.query.order_by(City.name).all()
    specialties = Specialty.query.order_by(Specialty.name).all()
    return render_template('doctor_self_register.html', cities=cities, specialties=specialties)


@app.route('/doctor/self-register/submit', methods=['POST'])
@login_required
def doctor_self_register_submit():
    """Process doctor self-registration submission"""
    try:
        # Get form data - all fields are mandatory
        name = request.form.get('name', '').strip()
        specialty_id = request.form.get('specialty_id')
        city_id = request.form.get('city_id')
        education = request.form.get('education', '').strip()
        college = request.form.get('college', '').strip()
        experience = request.form.get('experience')
        nmc_number = request.form.get('nmc_number', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        email = request.form.get('email', '').strip()
        practice_address = request.form.get('practice_address', '').strip()

        # Validate all required fields
        if not all([name, specialty_id, city_id, education, college, experience,
                   nmc_number, phone_number, email, practice_address]):
            flash('All fields are required. Please complete the form.', 'danger')
            return redirect(url_for('doctor_self_register'))

        # Convert experience to integer
        try:
            experience = int(experience)
            if experience < 0 or experience > 60:
                raise ValueError("Experience must be between 0 and 60 years")
        except ValueError:
            flash('Please enter a valid experience (0-60 years).', 'danger')
            return redirect(url_for('doctor_self_register'))

        # Validate specialty and city exist
        specialty = Specialty.query.get(specialty_id)
        city = City.query.get(city_id)
        if not specialty or not city:
            flash('Invalid specialty or city selected.', 'danger')
            return redirect(url_for('doctor_self_register'))

        # Check if NMC number already exists
        existing_doctor = Doctor.query.filter_by(nmc_number=nmc_number).first()
        if existing_doctor:
            flash('This NMC number is already registered. Please claim your existing profile instead.', 'warning')
            return redirect(url_for('claim_profile'))

        # Check for pending verification request with this NMC
        existing_request = VerificationRequest.query.filter_by(
            nmc_number=nmc_number,
            status='pending'
        ).first()
        if existing_request:
            flash('A verification request with this NMC number is already pending review.', 'warning')
            return redirect(url_for('user_profile'))

        # Handle file uploads - all are mandatory
        medical_degree = request.files.get('medical_degree')
        govt_id = request.files.get('govt_id')
        practice_license = request.files.get('practice_license')

        if not medical_degree or not govt_id or not practice_license:
            flash('All document uploads are required.', 'danger')
            return redirect(url_for('doctor_self_register'))

        # Create a temporary doctor ID for file storage (use user_id as placeholder)
        temp_doctor_id = f"new_{session['user_id']}"

        # Save files
        upload_folder = app.config['UPLOAD_FOLDER']
        medical_degree_path = upload_utils.save_verification_document(
            medical_degree, upload_folder, temp_doctor_id, 'medical_degree'
        )
        govt_id_path = upload_utils.save_verification_document(
            govt_id, upload_folder, temp_doctor_id, 'govt_id'
        )
        practice_license_path = upload_utils.save_verification_document(
            practice_license, upload_folder, temp_doctor_id, 'practice_license'
        )

        # Create verification request with is_new_doctor=True
        verification_request = VerificationRequest(
            doctor_id=None,  # No doctor profile yet
            user_id=session['user_id'],
            is_new_doctor=True,
            proposed_name=name,
            proposed_specialty_id=specialty_id,
            proposed_city_id=city_id,
            proposed_education=education,
            proposed_college=college,
            proposed_experience=experience,
            nmc_number=nmc_number,
            phone_number=phone_number,
            email=email,
            practice_address=practice_address,
            practice_city_id=city_id,  # Using same city for practice
            medical_degree_path=medical_degree_path,
            govt_id_path=govt_id_path,
            practice_license_path=practice_license_path,
            email_verified=True,  # Email is already verified through user account
            status='pending'
        )

        db.session.add(verification_request)
        db.session.commit()

        flash('Registration submitted successfully! Our admin team will review your application within 2-3 business days. You will receive an email notification once reviewed.', 'success')
        return redirect(url_for('user_profile'))

    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('doctor_self_register'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while processing your registration: {str(e)}', 'danger')
        return redirect(url_for('doctor_self_register'))


# ============================================================================
# SUBSCRIPTION & PAYMENT ROUTES
# ============================================================================

@app.route('/subscription/pricing')
@doctor_required
def subscription_pricing():
    """Show subscription pricing page for doctors"""
    user = User.query.get(session['user_id'])
    doctor = user.doctor_profile

    # Get current tier info
    current_tier_info = subscription_config.get_tier_info(doctor.subscription_tier or 'free')

    # Get upgrade options
    upgrade_options = subscription_config.get_upgrade_options(doctor.subscription_tier or 'free')

    return render_template('subscription_pricing.html',
                          doctor=doctor,
                          current_tier=doctor.subscription_tier or 'free',
                          current_tier_info=current_tier_info,
                          upgrade_options=upgrade_options,
                          all_tiers=subscription_config.SUBSCRIPTION_TIERS)


@app.route('/subscription/create-checkout/<tier>')
@doctor_required
def create_checkout_session(tier):
    """Create Stripe checkout session for subscription (or grant free during promo)"""
    try:
        user = User.query.get(session['user_id'])
        doctor = user.doctor_profile

        # Validate tier
        if tier not in ['premium', 'featured']:
            flash('Invalid subscription tier.', 'danger')
            return redirect(url_for('subscription_pricing'))

        # Check if already subscribed to this tier
        if doctor.subscription_tier == tier:
            flash(f'You are already on {tier.title()}!', 'info')
            return redirect(url_for('doctor_dashboard'))

        # PROMOTIONAL PERIOD: Grant features for free!
        if promo_config.is_promotion_active():
            # Auto-grant tier during promotion
            doctor.subscription_tier = tier

            # Set featured status if featured tier
            if tier == 'featured':
                doctor.is_featured = True

            # Set promo end date as subscription expiry
            doctor.subscription_expires_at = promo_config.CURRENT_PROMOTION['end_date']

            db.session.commit()

            promo = promo_config.get_promotion_banner()
            flash(f'🎉 {promo["message"]} You now have {tier.title()} access - enjoy all features FREE for {promo["days_left"]} days!', 'success')
            return redirect(url_for('doctor_dashboard'))

        # PAYMENT ENABLED: Create Stripe checkout
        if not promo_config.should_charge_payment():
            flash('Payment system is currently disabled. Please check back later!', 'info')
            return redirect(url_for('subscription_pricing'))

        # Get tier info
        tier_info = subscription_config.SUBSCRIPTION_TIERS[tier]

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=subscription_config.STRIPE_CONFIG['payment_method_types'],
            line_items=[{
                'price_data': {
                    'currency': subscription_config.STRIPE_CONFIG['currency'],
                    'product_data': {
                        'name': f'RankSewa {tier_info["name"]} Subscription',
                        'description': f'Monthly subscription - {tier_info["name"]} tier',
                    },
                    'unit_amount': tier_info['price_usd'] * 100,  # Amount in cents
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + f'subscription/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=request.host_url + 'subscription/cancel',
            client_reference_id=str(doctor.id),
            customer_email=user.email,
            metadata={
                'doctor_id': doctor.id,
                'user_id': user.id,
                'tier': tier
            }
        )

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        flash(f'Error creating checkout session: {str(e)}', 'danger')
        return redirect(url_for('subscription_pricing'))


@app.route('/subscription/success')
@doctor_required
def subscription_success():
    """Handle successful subscription payment"""
    session_id = request.args.get('session_id')

    if session_id:
        try:
            # Retrieve the session from Stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)

            # Get doctor and tier from metadata
            doctor_id = int(checkout_session.metadata['doctor_id'])
            tier = checkout_session.metadata['tier']

            # Update doctor subscription (will be confirmed by webhook)
            doctor = Doctor.query.get(doctor_id)
            if doctor and checkout_session.payment_status == 'paid':
                flash(f'🎉 Success! You are now subscribed to {tier.title()}. Welcome to premium features!', 'success')
            else:
                flash('Payment is being processed. Your subscription will be activated shortly.', 'info')

        except Exception as e:
            flash(f'Error retrieving session: {str(e)}', 'warning')

    return render_template('subscription_success.html')


@app.route('/subscription/cancel')
@doctor_required
def subscription_cancel():
    """Handle cancelled subscription checkout"""
    flash('Subscription checkout was cancelled. You can upgrade anytime!', 'info')
    return render_template('subscription_cancel.html')


@app.route('/subscription/portal')
@doctor_required
def subscription_portal():
    """Redirect to Stripe customer portal for subscription management"""
    try:
        user = User.query.get(session['user_id'])
        doctor = user.doctor_profile

        # Check if doctor has a Stripe customer ID (stored after first payment)
        if not hasattr(doctor, 'stripe_customer_id') or not doctor.stripe_customer_id:
            flash('No active subscription found. Please subscribe first.', 'info')
            return redirect(url_for('subscription_pricing'))

        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=doctor.stripe_customer_id,
            return_url=request.host_url + 'doctor/dashboard',
        )

        return redirect(portal_session.url, code=303)

    except Exception as e:
        flash(f'Error accessing subscription portal: {str(e)}', 'danger')
        return redirect(url_for('doctor_dashboard'))


@app.route('/stripe/webhook', methods=['POST'])
@csrf.exempt  # Stripe webhooks don't include CSRF token
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']

        # Get doctor and tier from metadata
        doctor_id = int(session_obj['metadata']['doctor_id'])
        tier = session_obj['metadata']['tier']
        customer_id = session_obj['customer']

        # Update doctor subscription
        doctor = Doctor.query.get(doctor_id)
        if doctor:
            doctor.subscription_tier = tier
            doctor.stripe_customer_id = customer_id

            # Set is_featured based on tier
            if tier == 'featured':
                doctor.is_featured = True

            db.session.commit()
            print(f"✅ Subscription activated: Doctor {doctor.id} -> {tier}")

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        customer_id = subscription['customer']

        # Find doctor by stripe customer ID
        doctor = Doctor.query.filter_by(stripe_customer_id=customer_id).first()
        if doctor:
            # Update subscription status
            if subscription['status'] == 'active':
                print(f"✅ Subscription updated for doctor {doctor.id}")
            else:
                print(f"⚠️  Subscription status changed to {subscription['status']} for doctor {doctor.id}")

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription['customer']

        # Find doctor and downgrade to free
        doctor = Doctor.query.filter_by(stripe_customer_id=customer_id).first()
        if doctor:
            doctor.subscription_tier = 'free'
            doctor.is_featured = False
            db.session.commit()
            print(f"⬇️  Subscription cancelled: Doctor {doctor.id} -> free")

    return jsonify({'success': True}), 200


# --- SQLAlchemy Teardown ---
@app.teardown_appcontext
def shutdown_session(exception=None):
    """Remove database session at the end of request"""
    db.session.remove()


# --- Context Processor for Ads ---
@app.context_processor
def inject_global_functions():
    """Make global functions available to all templates"""
    return dict(
        get_ad=ad_manager.get_ad_for_position,
        get_promotion_banner=promo_config.get_promotion_banner,
        is_promotion_active=promo_config.is_promotion_active
    )

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
            photo_url=None,  # Will be set after photo upload
            is_featured=is_featured,
            is_active=is_active,
            is_verified=is_verified
        )
        db.session.add(doctor)
        db.session.flush()  # Get doctor ID before photo upload

        # Handle photo upload
        if 'profile_photo' in request.files:
            photo_file = request.files['profile_photo']
            if photo_file and photo_file.filename:
                try:
                    photo_path = upload_utils.save_profile_photo(
                        photo_file,
                        app.config['UPLOAD_FOLDER'],
                        doctor.id
                    )
                    doctor.photo_url = photo_path
                except ValueError as e:
                    flash(f'Error uploading photo: {str(e)}', 'warning')

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
        doctor.is_featured = is_featured
        doctor.is_active = is_active
        doctor.is_verified = is_verified

        # Handle profile photo removal
        if 'remove_photo' in request.form and doctor.photo_url:
            upload_utils.delete_profile_photo(app.config['UPLOAD_FOLDER'], doctor.photo_url)
            doctor.photo_url = None

        # Handle photo upload
        if 'profile_photo' in request.files:
            photo_file = request.files['profile_photo']
            if photo_file and photo_file.filename:
                try:
                    # Delete old photo if exists
                    if doctor.photo_url:
                        upload_utils.delete_profile_photo(app.config['UPLOAD_FOLDER'], doctor.photo_url)

                    photo_path = upload_utils.save_profile_photo(
                        photo_file,
                        app.config['UPLOAD_FOLDER'],
                        doctor.id
                    )
                    doctor.photo_url = photo_path
                except ValueError as e:
                    flash(f'Error uploading photo: {str(e)}', 'warning')

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

    # Track profile views (skip if doctor is viewing own profile)
    user_is_doctor = False
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.doctor_id == doctor.id:
            user_is_doctor = True

    if not user_is_doctor:
        doctor.profile_views = (doctor.profile_views or 0) + 1
        db.session.commit()

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


# --- Admin Verification Routes ---
@app.route('/admin/verification-requests')
@admin_required
def admin_verification_requests():
    """List all doctor verification requests"""
    status_filter = request.args.get('status', 'all')

    # Get counts for each status
    counts = {
        'all': VerificationRequest.query.count(),
        'pending': VerificationRequest.query.filter_by(status='pending').count(),
        'approved': VerificationRequest.query.filter_by(status='approved').count(),
        'rejected': VerificationRequest.query.filter_by(status='rejected').count()
    }

    # Filter by status
    if status_filter == 'pending':
        verification_requests = VerificationRequest.query.filter_by(status='pending')\
            .order_by(VerificationRequest.created_at.desc()).all()
    elif status_filter == 'approved':
        verification_requests = VerificationRequest.query.filter_by(status='approved')\
            .order_by(VerificationRequest.reviewed_at.desc()).all()
    elif status_filter == 'rejected':
        verification_requests = VerificationRequest.query.filter_by(status='rejected')\
            .order_by(VerificationRequest.reviewed_at.desc()).all()
    else:
        verification_requests = VerificationRequest.query\
            .order_by(VerificationRequest.created_at.desc()).all()

    return render_template('admin_verification_requests.html',
                         requests=verification_requests,
                         status_filter=status_filter,
                         counts=counts)


@app.route('/admin/verification-requests/<int:request_id>', methods=['GET', 'POST'])
@admin_required
def admin_verification_detail(request_id):
    """View and process a verification request"""
    verification_request = VerificationRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'approve':
            try:
                user = verification_request.user

                # Check if this is a new doctor registration
                if verification_request.is_new_doctor:
                    # Create new doctor profile from verification data
                    from slugify import slugify

                    # Generate unique slug
                    base_slug = slugify(verification_request.proposed_name)
                    slug = base_slug
                    counter = 1
                    while Doctor.query.filter_by(slug=slug).first():
                        slug = f"{base_slug}-{counter}"
                        counter += 1

                    # Create new doctor
                    new_doctor = Doctor(
                        name=verification_request.proposed_name,
                        slug=slug,
                        city_id=verification_request.proposed_city_id,
                        specialty_id=verification_request.proposed_specialty_id,
                        education=verification_request.proposed_education,
                        college=verification_request.proposed_college,
                        experience=verification_request.proposed_experience,
                        nmc_number=verification_request.nmc_number,
                        phone_number=verification_request.phone_number,
                        practice_address=verification_request.practice_address,
                        is_verified=True,  # Immediately verified upon approval
                        is_active=True,
                        is_featured=False,
                        subscription_tier='free',  # Start with free tier
                        description=f"Verified doctor with {verification_request.proposed_experience} years of experience."
                    )

                    db.session.add(new_doctor)
                    db.session.flush()  # Get the doctor ID

                    # Link user to the new doctor profile
                    user.doctor_id = new_doctor.id
                    user.role = 'doctor'

                    # Update verification request with the new doctor_id
                    verification_request.doctor_id = new_doctor.id
                    verification_request.status = 'approved'
                    verification_request.reviewed_by = session['user_id']
                    verification_request.reviewed_at = datetime.utcnow()

                    db.session.commit()

                    flash(f'New doctor profile created and verified! {new_doctor.name} is now live and linked to {user.name}.', 'success')
                    return redirect(url_for('admin_verification_requests'))

                else:
                    # Existing flow: claiming an existing profile
                    user.doctor_id = verification_request.doctor_id
                    user.role = 'doctor'

                    # Mark doctor as verified
                    doctor = verification_request.doctor
                    doctor.is_verified = True
                    doctor.nmc_number = verification_request.nmc_number
                    doctor.phone_number = verification_request.phone_number
                    doctor.practice_address = verification_request.practice_address

                    # Update verification request
                    verification_request.status = 'approved'
                    verification_request.reviewed_by = session['user_id']
                    verification_request.reviewed_at = datetime.utcnow()

                    db.session.commit()

                    flash(f'Verification approved! {doctor.name} is now verified and linked to {user.name}.', 'success')
                    return redirect(url_for('admin_verification_requests'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error approving verification: {str(e)}', 'danger')

        elif action == 'reject':
            admin_notes = request.form.get('admin_notes', '').strip()

            if not admin_notes:
                flash('Please provide a reason for rejection.', 'danger')
            else:
                try:
                    verification_request.status = 'rejected'
                    verification_request.admin_notes = admin_notes
                    verification_request.reviewed_by = session['user_id']
                    verification_request.reviewed_at = datetime.utcnow()

                    db.session.commit()

                    flash(f'Verification request rejected.', 'info')
                    return redirect(url_for('admin_verification_requests'))

                except Exception as e:
                    db.session.rollback()
                    flash(f'Error rejecting verification: {str(e)}', 'danger')

    return render_template('admin_verification_detail.html', request=verification_request)


@app.route('/verification/document/<int:request_id>/<doc_type>')
@admin_required
def serve_verification_document(request_id, doc_type):
    """Serve verification documents (admin only)"""
    from flask import send_from_directory
    import os

    verification_request = VerificationRequest.query.get_or_404(request_id)

    # Get the document path based on type
    if doc_type == 'medical_degree':
        doc_path = verification_request.medical_degree_path
    elif doc_type == 'govt_id':
        doc_path = verification_request.govt_id_path
    elif doc_type == 'practice_license':
        doc_path = verification_request.practice_license_path
    else:
        flash('Invalid document type.', 'danger')
        return redirect(url_for('admin_verification_detail', request_id=request_id))

    if not doc_path:
        flash('Document not found.', 'danger')
        return redirect(url_for('admin_verification_detail', request_id=request_id))

    # Construct full path
    upload_folder = app.config['UPLOAD_FOLDER']
    full_path = os.path.join(upload_folder, doc_path)

    if not os.path.exists(full_path):
        flash('Document file not found on server.', 'danger')
        return redirect(url_for('admin_verification_detail', request_id=request_id))

    # Serve the file
    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)

    return send_from_directory(directory, filename)


@app.route('/uploads/photos/<filename>')
def serve_photo(filename):
    """Serve profile photos (publicly accessible)"""
    from flask import send_from_directory
    import os

    photos_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'photos')

    # Security: Prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        abort(404)

    return send_from_directory(photos_folder, filename)


# --- Doctor Dashboard Routes ---
@app.route('/doctor/dashboard')
@doctor_required
def doctor_dashboard():
    """Doctor dashboard - overview of profile and analytics"""
    user = User.query.get(session['user_id'])
    doctor = user.doctor_profile

    # Get review statistics
    review_count = len(doctor.ratings)
    avg_rating = doctor.avg_rating

    # Count responses
    response_count = DoctorResponse.query.filter_by(doctor_id=doctor.id).count()
    response_rate = (response_count / review_count * 100) if review_count > 0 else 0

    # Get verification status
    verification_request = VerificationRequest.query.filter_by(
        doctor_id=doctor.id,
        user_id=user.id
    ).order_by(VerificationRequest.created_at.desc()).first()

    return render_template('doctor_dashboard.html',
                         doctor=doctor,
                         user=user,
                         review_count=review_count,
                         avg_rating=avg_rating,
                         response_count=response_count,
                         response_rate=response_rate,
                         verification_request=verification_request)


@app.route('/doctor/profile/edit', methods=['GET', 'POST'])
@doctor_required
def doctor_profile_edit():
    """Edit doctor profile information"""
    user = User.query.get(session['user_id'])
    doctor = user.doctor_profile

    if request.method == 'POST':
        try:
            # Allow editing only certain fields
            doctor.description = request.form.get('description', '').strip()
            doctor.education = request.form.get('education', '').strip()
            doctor.college = request.form.get('college', '').strip()
            doctor.practice_address = request.form.get('practice_address', '').strip()

            # Handle profile photo removal
            if 'remove_photo' in request.form and doctor.photo_url:
                # Delete old photo
                upload_utils.delete_profile_photo(app.config['UPLOAD_FOLDER'], doctor.photo_url)
                doctor.photo_url = None
                flash('Profile photo removed.', 'info')

            # Handle photo upload
            if 'profile_photo' in request.files:
                photo_file = request.files['profile_photo']
                if photo_file and photo_file.filename:
                    try:
                        # Delete old photo if exists
                        if doctor.photo_url:
                            upload_utils.delete_profile_photo(app.config['UPLOAD_FOLDER'], doctor.photo_url)

                        # Save new photo
                        photo_path = upload_utils.save_profile_photo(
                            photo_file,
                            app.config['UPLOAD_FOLDER'],
                            doctor.id
                        )
                        doctor.photo_url = photo_path
                        flash('Profile photo updated successfully!', 'success')

                    except ValueError as e:
                        flash(f'Error uploading photo: {str(e)}', 'warning')

            db.session.commit()
            if 'remove_photo' not in request.form and 'profile_photo' not in request.files:
                flash('Profile updated successfully!', 'success')
            return redirect(url_for('doctor_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('doctor_profile_edit.html', doctor=doctor, user=user)


@app.route('/doctor/reviews')
@doctor_required
def doctor_reviews():
    """View all reviews for doctor's profile"""
    user = User.query.get(session['user_id'])
    doctor = user.doctor_profile

    # Get all ratings with responses
    ratings = Rating.query.filter_by(doctor_id=doctor.id)\
        .order_by(Rating.created_at.desc()).all()

    return render_template('doctor_reviews.html',
                         doctor=doctor,
                         ratings=ratings)


@app.route('/doctor/reviews/<int:rating_id>/respond', methods=['POST'])
@doctor_required
def doctor_respond_to_review(rating_id):
    """Add or update response to a review"""
    user = User.query.get(session['user_id'])
    doctor = user.doctor_profile

    rating = Rating.query.get_or_404(rating_id)

    # Verify this review is for the doctor's profile
    if rating.doctor_id != doctor.id:
        flash('You can only respond to reviews of your profile.', 'danger')
        return redirect(url_for('doctor_reviews'))

    response_text = request.form.get('response_text', '').strip()

    if not response_text:
        flash('Response cannot be empty.', 'danger')
        return redirect(url_for('doctor_reviews'))

    try:
        # Check if response already exists
        existing_response = DoctorResponse.query.filter_by(rating_id=rating_id).first()

        if existing_response:
            # Update existing response
            existing_response.response_text = response_text
            existing_response.updated_at = datetime.utcnow()
            flash('Response updated successfully!', 'success')
        else:
            # Create new response
            new_response = DoctorResponse(
                rating_id=rating_id,
                doctor_id=doctor.id,
                user_id=user.id,
                response_text=response_text
            )
            db.session.add(new_response)
            flash('Response added successfully!', 'success')

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Error saving response: {str(e)}', 'danger')

    return redirect(url_for('doctor_reviews'))


@app.route('/doctor/analytics')
@doctor_required
def doctor_analytics():
    """View profile analytics"""
    user = User.query.get(session['user_id'])
    doctor = user.doctor_profile

    # Get review statistics
    ratings = doctor.ratings
    review_count = len(ratings)
    avg_rating = doctor.avg_rating

    # Response statistics
    response_count = DoctorResponse.query.filter_by(doctor_id=doctor.id).count()
    response_rate = (response_count / review_count * 100) if review_count > 0 else 0

    # Rating breakdown
    rating_breakdown = {
        5: len([r for r in ratings if r.rating == 5]),
        4: len([r for r in ratings if r.rating == 4]),
        3: len([r for r in ratings if r.rating == 3]),
        2: len([r for r in ratings if r.rating == 2]),
        1: len([r for r in ratings if r.rating == 1])
    }

    return render_template('doctor_analytics.html',
                         doctor=doctor,
                         review_count=review_count,
                         avg_rating=avg_rating,
                         response_count=response_count,
                         response_rate=response_rate,
                         rating_breakdown=rating_breakdown)


@app.route('/doctor/delete-account', methods=['GET'])
@doctor_required
def doctor_delete_account():
    """Show account deletion information page (directs to email support)"""
    user = User.query.get(session['user_id'])
    doctor = user.doctor_profile

    return render_template('doctor_delete_account.html', doctor=doctor, user=user)


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
