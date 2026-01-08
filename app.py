from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, make_response, abort
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
import re
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from models import db, City, Specialty, Clinic, Doctor, User, Rating, Appointment, ContactMessage, Advertisement, VerificationRequest, DoctorResponse, ReviewFlag, BadgeDefinition, UserBadge, ReviewHelpful, Article, ArticleCategory, ClinicManagerDoctor, ClinicAccount
from config import Config
import ad_manager
import upload_utils
import r2_storage
import stripe
import subscription_config
import promo_config
import resend
from PIL import Image
import secrets

# Import text_utils with fallback
try:
    import text_utils
except ImportError:
    # Fallback if text_utils not available
    class text_utils:
        @staticmethod
        def normalize_name(name):
            """Fallback name normalization"""
            if not name:
                return name
            name = name.strip()
            if not name:
                return name

            # Handle Dr. prefix
            prefix = ""
            name_part = name

            if name.lower().startswith("dr. "):
                prefix = "Dr. "
                name_part = name[4:]
            elif name.lower().startswith("dr "):
                prefix = "Dr. "
                name_part = name[3:]

            # Convert to title case
            name_part = name_part.title()

            return prefix + name_part

# Load environment variables
load_dotenv()

# Configure Resend for email notifications
resend_key = os.getenv('RESEND_API_KEY')
if not resend_key:
    print("WARNING: RESEND_API_KEY not set. Email functionality will not work.")
    resend_key = None  # Will fail gracefully when trying to send emails
resend.api_key = resend_key

# --- App Configuration ---
app = Flask(__name__)
app.config.from_object(Config)

# SECRET_KEY is required - fail fast if not set in production
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('DATABASE_URL'):
        raise ValueError("SECRET_KEY environment variable must be set in production!")
    # Development fallback only
    secret_key = 'dev-secret-key-INSECURE-FOR-DEVELOPMENT-ONLY'
    print("WARNING: Using insecure development SECRET_KEY. DO NOT use in production!")
app.config['SECRET_KEY'] = secret_key
db_url = os.environ.get('DATABASE_URL') or 'sqlite:///doctors.db'
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security configurations
# SESSION_COOKIE_SECURE: True in production (HTTPS), False in development
is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('DATABASE_URL') is not None
app.config['SESSION_COOKIE_SECURE'] = is_production
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


def clinic_manager_required(f):
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
        if user.role != 'clinic_manager':
            flash('Clinic manager access required.', 'warning')
            # Fixed: Redirect to index instead of clinic_manager_dashboard to avoid infinite loop
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def is_safe_url(target):
    """
    Validate that a redirect URL is safe (prevents open redirects).
    Only allows relative URLs or URLs to the same host.
    """
    if not target:
        return False

    from urllib.parse import urlparse, urljoin
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    # Must be same scheme (http/https) and same netloc (domain)
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_safe_redirect(param_name='next', fallback='index'):
    """
    Get a safe redirect URL from request parameters.
    Returns the validated URL or a fallback route.
    """
    target = request.values.get(param_name)
    if target and is_safe_url(target):
        return target
    return url_for(fallback)


def build_doctor_analytics_context(doctor):
    """Build analytics context for doctor or clinic manager views."""
    tier_order = ['free', 'premium', 'featured']
    effective_tier = doctor.subscription_tier or 'free'
    promo_tier = promo_config.get_promotional_tier()
    if promo_tier in tier_order:
        promo_index = tier_order.index(promo_tier)
        current_index = tier_order.index(effective_tier) if effective_tier in tier_order else 0
        if promo_index > current_index:
            effective_tier = promo_tier
    has_enhanced_analytics = effective_tier == 'featured'

    ratings = doctor.ratings
    review_count = len(ratings)
    avg_rating = doctor.avg_rating
    now = datetime.utcnow()
    last_30_days = now - timedelta(days=30)
    last_90_days = now - timedelta(days=90)

    recent_reviews = sorted(
        [r for r in ratings if r.created_at],
        key=lambda r: r.created_at,
        reverse=True
    )
    reviews_last_30 = [r for r in recent_reviews if r.created_at >= last_30_days]
    reviews_prev_30 = [
        r for r in recent_reviews
        if r.created_at < last_30_days and r.created_at >= (last_30_days - timedelta(days=30))
    ]
    avg_rating_last_90 = 0.0
    if recent_reviews:
        ratings_last_90 = [r.rating for r in recent_reviews if r.created_at >= last_90_days]
        if ratings_last_90:
            avg_rating_last_90 = sum(ratings_last_90) / len(ratings_last_90)

    response_count = DoctorResponse.query.filter_by(doctor_id=doctor.id).count()
    response_rate = (response_count / review_count * 100) if review_count > 0 else 0
    responded_reviews = [r for r in recent_reviews if r.doctor_response]
    average_response_hours = None
    if responded_reviews:
        total_seconds = 0
        for r in responded_reviews:
            delta = r.doctor_response.created_at - r.created_at
            total_seconds += max(delta.total_seconds(), 0)
        average_response_hours = total_seconds / len(responded_reviews) / 3600
    unanswered_reviews = [r for r in recent_reviews if not r.doctor_response][:3]

    response_speed = None
    if has_enhanced_analytics and responded_reviews:
        within_24 = 0
        within_72 = 0
        over_72 = 0
        for r in responded_reviews:
            delta_hours = max((r.doctor_response.created_at - r.created_at).total_seconds() / 3600, 0)
            if delta_hours <= 24:
                within_24 += 1
            elif delta_hours <= 72:
                within_72 += 1
            else:
                over_72 += 1
        total_responded = len(responded_reviews)
        response_speed = {
            'within_24': within_24,
            'within_72': within_72,
            'over_72': over_72,
            'within_24_pct': (within_24 / total_responded * 100) if total_responded else 0,
            'within_72_pct': (within_72 / total_responded * 100) if total_responded else 0,
            'over_72_pct': (over_72 / total_responded * 100) if total_responded else 0
        }

    rating_trend_delta = None
    ratings_prev_90 = [r.rating for r in recent_reviews if r.created_at < last_90_days and r.created_at >= (last_90_days - timedelta(days=90))]
    if ratings_prev_90 and avg_rating_last_90:
        avg_prev_90 = sum(ratings_prev_90) / len(ratings_prev_90)
        rating_trend_delta = avg_rating_last_90 - avg_prev_90

    def month_start(dt, months_back):
        month = dt.month - months_back
        year = dt.year
        while month <= 0:
            month += 12
            year -= 1
        return datetime(year, month, 1)

    review_trend = []
    if has_enhanced_analytics:
        for i in range(5, -1, -1):
            start = month_start(now, i)
            end = month_start(now, i - 1) if i > 0 else datetime(now.year, now.month, 1) + timedelta(days=32)
            end = datetime(end.year, end.month, 1)
            month_reviews = [r for r in recent_reviews if r.created_at >= start and r.created_at < end]
            month_avg = sum(r.rating for r in month_reviews) / len(month_reviews) if month_reviews else 0
            review_trend.append({
                'label': start.strftime('%b %Y'),
                'count': len(month_reviews),
                'avg_rating': month_avg
            })

    profile_fields = [
        ('photo', bool(doctor.photo_url)),
        ('bio', bool(doctor.description)),
        ('education', bool(doctor.education)),
        ('workplace', bool(doctor.workplace)),
        ('address', bool(doctor.practice_address)),
        ('phone', bool(doctor.phone_number))
    ]
    profile_strength_pct = round(sum(1 for _, present in profile_fields if present) / len(profile_fields) * 100)
    missing_profile_fields = [name for name, present in profile_fields if not present]

    rating_breakdown = {
        5: len([r for r in ratings if r.rating == 5]),
        4: len([r for r in ratings if r.rating == 4]),
        3: len([r for r in ratings if r.rating == 3]),
        2: len([r for r in ratings if r.rating == 2]),
        1: len([r for r in ratings if r.rating == 1])
    }

    # Get daily analytics for last 30 days
    from models import DoctorAnalytics
    from datetime import date
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    daily_analytics = DoctorAnalytics.query.filter(
        DoctorAnalytics.doctor_id == doctor.id,
        DoctorAnalytics.date >= start_date,
        DoctorAnalytics.date <= end_date
    ).order_by(DoctorAnalytics.date.asc()).all()

    # Calculate totals from daily analytics
    total_views_30d = sum(a.profile_views for a in daily_analytics)
    total_search_appearances = sum(a.search_appearances for a in daily_analytics)
    total_phone_clicks = sum(a.phone_clicks for a in daily_analytics)
    avg_daily_views = total_views_30d / 30 if total_views_30d > 0 else 0

    # Traffic sources breakdown
    traffic_sources = {
        'search': sum(a.source_search for a in daily_analytics),
        'google': sum(a.source_google for a in daily_analytics),
        'homepage': sum(a.source_homepage for a in daily_analytics),
        'direct': sum(a.source_direct for a in daily_analytics)
    }

    # Prepare chart data for last 30 days
    chart_data = {
        'dates': [a.date.strftime('%b %d') for a in daily_analytics],
        'views': [a.profile_views for a in daily_analytics]
    }

    return {
        'review_count': review_count,
        'avg_rating': avg_rating,
        'response_count': response_count,
        'response_rate': response_rate,
        'rating_breakdown': rating_breakdown,
        'reviews_last_30': reviews_last_30,
        'reviews_prev_30': reviews_prev_30,
        'avg_rating_last_90': avg_rating_last_90,
        'rating_trend_delta': rating_trend_delta,
        'average_response_hours': average_response_hours,
        'response_speed': response_speed,
        'unanswered_reviews': unanswered_reviews,
        'recent_reviews': recent_reviews[:5],
        'profile_strength_pct': profile_strength_pct,
        'missing_profile_fields': missing_profile_fields,
        'review_trend': review_trend,
        'has_enhanced_analytics': has_enhanced_analytics,
        'effective_tier': effective_tier,
        # New analytics data
        'total_views_30d': total_views_30d,
        'avg_daily_views': avg_daily_views,
        'total_search_appearances': total_search_appearances,
        'total_phone_clicks': total_phone_clicks,
        'traffic_sources': traffic_sources,
        'chart_data': chart_data
    }

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

def send_verification_approved_email(to_email, doctor_name):
    """
    Send email notification when doctor verification is approved

    Args:
        to_email: Doctor's email address
        doctor_name: Full name of the doctor (e.g., "Dr. Bilakshan Mishra")

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Extract last name for personalization
        last_name = doctor_name.split()[-1].replace('Dr.', '').strip()

        subject = "Your RankSewa Profile Has Been Verified"

        html_body = f"""
        <div style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #111;">
            <p>Dear Dr. {last_name},</p>

            <p>
                Greetings from <strong>RankSewa</strong>.
            </p>

            <p>
                We are pleased to inform you that your doctor profile on
                <strong>RankSewa</strong> has been <strong>successfully verified</strong>
                after reviewing the documents you submitted.
            </p>

            <p>
                Thank you for taking the time to complete the verification process.
                As we build RankSewa to help patients in Nepal find trusted healthcare
                professionals, verified doctors like you play a vital role in
                maintaining transparency and trust.
            </p>

            <p>
                We would also like to sincerely thank you for your contribution to
                the healthcare community. Medical professionals like you are essential
                to the well-being of our society, and your work makes a meaningful
                difference every day.
            </p>

            <p>
                RankSewa is still in its early stages, and your decision to verify your
                profile means a great deal to us. We truly appreciate your trust
                and support.
            </p>

            <p>
                If you ever wish to update your profile or share feedback on how we can
                improve the platform for doctors and patients, please contact us at
                <a href="mailto:support@ranksewa.com">support@ranksewa.com</a>.
            </p>

            <p style="margin-top: 32px;">
                With sincere appreciation,<br>
                <strong>Paul Paudyal</strong><br>
                Founder, RankSewa<br>
                <a href="https://ranksewa.com">https://ranksewa.com</a><br>
                <span style="color: #6b7280; font-size: 14px;">Support: <a href="mailto:support@ranksewa.com">support@ranksewa.com</a></span>
            </p>
        </div>
        """

        params = {
            "from": "RankSewa Onboarding <onboarding@ranksewa.com>",
            "to": [to_email],
            "subject": subject,
            "html": html_body
        }

        email_response = resend.Emails.send(params)
        print(f"✅ Verification approved email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send verification email to {to_email}: {e}")
        return False

def send_verification_rejected_email(to_email, doctor_name, admin_notes=None):
    """
    Send email notification when doctor verification is rejected

    Args:
        to_email: Doctor's email address
        doctor_name: Full name of the doctor
        admin_notes: Optional notes from admin about rejection

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        last_name = doctor_name.split()[-1].replace('Dr.', '').strip()

        subject = "Update on Your RankSewa Verification Request"

        rejection_reason = ""
        if admin_notes:
            rejection_reason = f"""
            <p>
                <strong>Admin Notes:</strong><br>
                {admin_notes}
            </p>
            """

        html_body = f"""
        <div style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #111;">
            <p>Dear Dr. {last_name},</p>

            <p>
                Thank you for submitting your verification request on <strong>RankSewa</strong>.
            </p>

            <p>
                After reviewing your submission, we were unable to approve your verification
                request at this time.
            </p>

            {rejection_reason}

            <p>
                You are welcome to submit a new verification request with updated information
                or documentation. Please ensure:
            </p>
            <ul>
                <li>Your NMC registration number is valid and matches NMC records</li>
                <li>All uploaded documents are clear and readable</li>
                <li>Your information matches your official NMC registration</li>
            </ul>

            <p>
                If you have any questions or need clarification, please contact us at
                <a href="mailto:support@ranksewa.com">support@ranksewa.com</a> and we'll be happy to help.
            </p>

            <p style="margin-top: 32px;">
                Best regards,<br>
                <strong>RankSewa Team</strong><br>
                <a href="https://ranksewa.com">https://ranksewa.com</a><br>
                <span style="color: #6b7280; font-size: 14px;">Support: <a href="mailto:support@ranksewa.com">support@ranksewa.com</a></span>
            </p>
        </div>
        """

        params = {
            "from": "RankSewa Onboarding <onboarding@ranksewa.com>",
            "to": [to_email],
            "subject": subject,
            "html": html_body
        }

        email_response = resend.Emails.send(params)
        print(f"✅ Verification rejected email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send rejection email to {to_email}: {e}")
        return False

def send_admin_verification_notification(verification_request, doctor_name, user_email):
    """
    Send email notification to admin when new verification request is submitted

    Args:
        verification_request: VerificationRequest object
        doctor_name: Name of the doctor/profile being verified
        user_email: Email of the user submitting request

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Get admin email from environment variable
        admin_email = os.getenv('ADMIN_EMAIL', 'paul.paudyal@gmail.com')

        request_type = "New Doctor Registration" if verification_request.is_new_doctor else "Profile Claim"

        subject = f"New Verification Request: {doctor_name}"

        html_body = f"""
        <div style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #111;">
            <h2 style="color: #2563eb;">🔔 New Verification Request</h2>

            <p><strong>Type:</strong> {request_type}</p>
            <p><strong>Doctor Name:</strong> {doctor_name}</p>
            <p><strong>User Email:</strong> {user_email}</p>
            <p><strong>NMC Number:</strong> {verification_request.nmc_number or 'Not provided'}</p>
            <p><strong>Submitted:</strong> {verification_request.created_at.strftime('%B %d, %Y at %I:%M %p') if verification_request.created_at else 'Just now'}</p>

            <div style="margin: 30px 0; padding: 20px; background-color: #f3f4f6; border-left: 4px solid #2563eb;">
                <p style="margin: 0;"><strong>Action Required:</strong></p>
                <p style="margin: 10px 0 0 0;">Review and approve/reject this verification request in your admin panel.</p>
            </div>

            <p>
                <a href="https://ranksewa.com/admin/verification-requests/{verification_request.id}"
                   style="display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Review Request →
                </a>
            </p>

            <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">

            <p style="color: #6b7280; font-size: 14px;">
                This is an automated notification from RankSewa.<br>
                <a href="https://ranksewa.com/admin/verification-requests" style="color: #2563eb;">View all pending requests</a>
            </p>
        </div>
        """

        params = {
            "from": "RankSewa Admin <onboarding@ranksewa.com>",
            "to": [admin_email],
            "subject": subject,
            "html": html_body,
            "reply_to": user_email
        }

        email_response = resend.Emails.send(params)
        print(f"✅ Admin notification sent to {admin_email} for {doctor_name}")
        return True

    except Exception as e:
        print(f"❌ Failed to send admin notification: {e}")
        return False

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


def generate_unique_clinic_slug(name, clinic_id=None):
    base_slug = generate_slug(name)
    slug = base_slug
    counter = 2
    while True:
        existing = Clinic.query.filter_by(slug=slug).first()
        if not existing or (clinic_id and existing.id == clinic_id):
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


def get_doctor_avatar_url(doctor_name, doctor_id):
    """
    Generate professional avatar URL for doctors without photos.
    Uses DiceBear Avatars API to create unique, professional initials-based avatars.

    Args:
        doctor_name: Full name of the doctor (e.g., "Dr. Ramesh Sharma")
        doctor_id: Unique doctor ID for color consistency

    Returns:
        URL to professional avatar image
    """
    from urllib.parse import quote

    # Color palette - professional medical colors
    colors = [
        '0D8ABC',  # Medical blue
        '2a9d8f',  # Teal
        'e76f51',  # Coral
        'f4a261',  # Sandy brown
        '264653',  # Dark blue-green
        '9b59b6',  # Purple
        '3498db',  # Sky blue
        '16a085',  # Green sea
    ]

    # Select color based on doctor ID for consistency
    color = colors[doctor_id % len(colors)]

    # Normalize to avoid "Dr" being used as the first initial
    cleaned_name = doctor_name or ''
    title_pattern = r'^\s*(dr|mr|mrs|ms|prof|professor|asst|assistant|assoc|associate)\.?\s+'
    while re.match(title_pattern, cleaned_name, flags=re.IGNORECASE):
        cleaned_name = re.sub(title_pattern, '', cleaned_name, flags=re.IGNORECASE)
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
    seed_name = cleaned_name or doctor_name

    # URL encode the doctor name for seed
    seed = quote(seed_name)

    # Generate DiceBear initials avatar URL
    return f"https://api.dicebear.com/7.x/initials/svg?seed={seed}&backgroundColor={color}"


# Register as Jinja template filter
@app.template_filter('doctor_avatar')
def doctor_avatar_filter(doctor):
    """
    Jinja template filter to get doctor avatar URL.
    Usage in templates: {{ doctor|doctor_avatar }}
    """
    if doctor.photo_url:
        return doctor.photo_url
    return get_doctor_avatar_url(doctor.name, doctor.id)


@app.template_filter('from_json')
def from_json_filter(json_string):
    """
    Jinja template filter to parse JSON string.
    Usage in templates: {{ doctor.working_hours|from_json }}
    """
    if not json_string:
        return {}
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return {}


@app.template_filter('doctor_title')
def doctor_title_filter(name):
    """
    Jinja template filter to add 'Dr.' prefix if not already present.
    Handles edge cases like professors (Prof. Dr. ...).
    Usage in templates: {{ doctor.name|doctor_title }}
    """
    if not name:
        return ''

    name = name.strip()

    # If name already starts with Dr. or Prof., don't add anything
    if name.startswith('Dr.') or name.startswith('Prof.'):
        return name

    # Otherwise, add Dr. prefix
    return f'Dr. {name}'


def optimize_and_save_article_image(image_file):
    """
    Optimize uploaded article image and save to static/img/articles/

    - Resizes to optimal social sharing size (1200x630px for OG tags)
    - Compresses for web (reduces file size 60-80%)
    - Converts to JPEG for consistency
    - Generates unique filename

    Returns: relative path like 'img/articles/abc123.jpg' or None if error
    """
    try:
        # Generate unique filename
        random_hex = secrets.token_hex(8)
        filename = f"{random_hex}.jpg"
        filepath = os.path.join('static', 'img', 'articles', filename)

        # Open and optimize image
        img = Image.open(image_file)

        # Convert to RGB if necessary (handles PNG with transparency, etc.)
        if img.mode != 'RGB':
            # Create white background for images with transparency
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA' or 'transparency' in img.info:
                # Paste with alpha channel as mask
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            else:
                rgb_img.paste(img)
            img = rgb_img

        # Resize to optimal social sharing size (1200x630px for OG tags)
        # This is the perfect size for Facebook/Twitter/LinkedIn sharing
        target_width = 1200
        target_height = 630

        # Calculate aspect ratio
        aspect = img.width / img.height
        target_aspect = target_width / target_height

        if aspect > target_aspect:
            # Image is wider - crop width
            new_width = int(img.height * target_aspect)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            # Image is taller - crop height
            new_height = int(img.width / target_aspect)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))

        # Resize to target dimensions
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Save with high quality JPEG compression (85 = good balance of quality/size)
        img.save(filepath, 'JPEG', quality=85, optimize=True)

        # Return relative path for database (without 'static/' prefix)
        return f"img/articles/{filename}"

    except Exception as e:
        print(f"Error optimizing image: {e}")
        return None


# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        is_doctor = request.form.get('is_doctor') == '1'
        is_clinic_manager = request.form.get('is_clinic_manager') == '1'

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        if is_doctor and is_clinic_manager:
            flash('Please select either doctor or clinic manager, not both.', 'danger')
            return redirect(url_for('register'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists.', 'danger')
            return redirect(url_for('register'))

        # Create new user
        user = User(name=name, email=email)
        user.set_password(password)
        if is_clinic_manager:
            user.role = 'clinic_manager'
        if is_doctor or is_clinic_manager:
            user.is_active = False

        try:
            db.session.add(user)
            db.session.commit()

            # If user indicated they're a doctor, auto-login and redirect to claim profile
            if is_doctor:
                flash('Registration received. Please wait for admin approval before logging in.', 'info')
                return redirect(url_for('login'))
            if is_clinic_manager:
                flash('Registration received. Please wait for admin approval before logging in.', 'info')
                return redirect(url_for('login'))
            else:
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
                flash('Your account is not active yet. Please wait for admin approval.', 'warning')
                return redirect(url_for('login'))
            if is_admin_email(user.email) and not user.is_admin:
                user.is_admin = True
                db.session.commit()
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            session['role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')

            # Fixed: Use safe redirect to prevent open redirect vulnerability
            return redirect(get_safe_redirect('next', 'index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/login/facebook')
def facebook_login():
    if not facebook.client_id or not facebook.client_secret:
        flash('Facebook login is not configured. Please contact the site admin.', 'warning')
        return redirect(url_for('login'))
    # Fixed: Validate redirect URL before storing in session
    next_page = request.args.get('next')
    if next_page and is_safe_url(next_page):
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

    # Fixed: Validate stored redirect URL before using it
    next_page = session.pop('oauth_next', None)
    if next_page and is_safe_url(next_page):
        return redirect(next_page)
    return redirect(url_for('index'))

@app.route('/login/google')
def google_login():
    if not google.client_id or not google.client_secret:
        flash('Google login is not configured. Please contact the site admin.', 'warning')
        return redirect(url_for('login'))
    # Fixed: Validate redirect URL before storing in session
    next_page = request.args.get('next')
    if next_page and is_safe_url(next_page):
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

    # Fixed: Validate stored redirect URL before using it
    next_page = session.pop('oauth_next', None)
    if next_page and is_safe_url(next_page):
        return redirect(next_page)
    return redirect(url_for('index'))

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

@app.route('/pricing')
def pricing():
    """Pricing page for doctors - shows promotional offer"""
    return render_template('pricing.html')

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap for Google Search Console"""
    from sitemap import generate_sitemap
    sitemap_xml = generate_sitemap(app, db)

    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/robots.txt')
def robots():
    """Robots.txt for search engines"""
    robots_txt = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /doctor/dashboard
Disallow: /doctor/analytics

Sitemap: https://ranksewa.com/sitemap.xml
"""
    response = make_response(robots_txt)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/health-digest')
def health_digest():
    """Health digest article listing page"""
    # Get filter parameters
    category_slug = request.args.get('category')
    search_query = request.args.get('q', '').strip()

    # Base query - only published articles
    query = Article.query.filter_by(is_published=True)

    # Filter by category if specified
    if category_slug:
        category = ArticleCategory.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)
    else:
        category = None

    # Search if query provided
    if search_query:
        search_pattern = f'%{search_query}%'
        query = query.filter(
            db.or_(
                Article.title.ilike(search_pattern),
                Article.summary.ilike(search_pattern),
                Article.content.ilike(search_pattern)
            )
        )

    # Order by featured first, then by published date
    articles = query.order_by(
        Article.is_featured.desc(),
        Article.published_at.desc()
    ).all()

    # Get all categories for filter menu
    categories = ArticleCategory.query.order_by(ArticleCategory.display_order).all()

    # Get featured articles for sidebar
    featured_articles = Article.query.filter_by(
        is_published=True,
        is_featured=True
    ).order_by(Article.published_at.desc()).limit(3).all()

    return render_template('health_digest.html',
                         articles=articles,
                         categories=categories,
                         current_category=category,
                         featured_articles=featured_articles,
                         search_query=search_query)


@app.route('/health-digest/<slug>')
def article_detail(slug):
    """Individual article detail page"""
    # Get article and increment view count
    article = Article.query.filter_by(slug=slug, is_published=True).first_or_404()
    article.view_count += 1
    db.session.commit()

    # Get related articles (same category, exclude current)
    related_articles = Article.query.filter_by(
        category_id=article.category_id,
        is_published=True
    ).filter(Article.id != article.id)\
     .order_by(Article.published_at.desc())\
     .limit(3).all()

    # Get related doctors if article has a related specialty
    related_doctors = []
    if article.related_specialty_id:
        # Try to get verified doctors first
        related_doctors = Doctor.query.filter_by(
            specialty_id=article.related_specialty_id,
            is_active=True,
            is_verified=True
        ).order_by(Doctor.is_featured.desc())\
         .limit(4).all()

        # If no verified doctors found, fall back to all active doctors
        if not related_doctors:
            related_doctors = Doctor.query.filter_by(
                specialty_id=article.related_specialty_id,
                is_active=True
            ).order_by(Doctor.is_featured.desc(), Doctor.is_verified.desc())\
             .limit(4).all()

    return render_template('article_detail.html',
                         article=article,
                         related_articles=related_articles,
                         related_doctors=related_doctors)


@app.route('/leaderboard')
def leaderboard():
    """Show top reviewers leaderboard"""
    from sqlalchemy import func, desc

    # Get top reviewers by points
    top_by_points = User.query.filter(User.points > 0)\
        .order_by(desc(User.points))\
        .limit(50).all()

    # Get top reviewers by review count
    top_by_reviews = db.session.query(User)\
        .join(Rating)\
        .group_by(User.id)\
        .order_by(desc(func.count(Rating.id)))\
        .limit(50).all()

    # Get top reviewers by helpful votes (most helpful)
    # This is more complex - need to count helpful votes across all their reviews
    from sqlalchemy import select
    helpful_subquery = db.session.query(
        Rating.user_id,
        func.count(ReviewHelpful.id).label('helpful_count')
    ).join(ReviewHelpful, Rating.id == ReviewHelpful.rating_id)\
     .group_by(Rating.user_id)\
     .subquery()

    top_by_helpful = db.session.query(User)\
        .join(helpful_subquery, User.id == helpful_subquery.c.user_id)\
        .order_by(desc(helpful_subquery.c.helpful_count))\
        .limit(50).all()

    # Get all badge definitions for display
    badges = BadgeDefinition.query.filter_by(is_active=True)\
        .order_by(BadgeDefinition.display_order).all()

    return render_template('leaderboard.html',
                         top_by_points=top_by_points,
                         top_by_reviews=top_by_reviews,
                         top_by_helpful=top_by_helpful,
                         badges=badges)

# --- Doctor Verification Routes ---
@app.route('/claim-profile', methods=['GET'])
def claim_profile():
    """Search for unclaimed doctor profiles"""
    # If user is already a verified doctor, redirect to dashboard
    if session.get('role') == 'doctor':
        flash('You already have a verified doctor profile.', 'info')
        return redirect(url_for('doctor_dashboard'))

    # Check if user has any verification request
    user_id = session.get('user_id')
    if user_id:
        existing_request = VerificationRequest.query.filter_by(
            user_id=user_id
        ).order_by(VerificationRequest.created_at.desc()).first()

        if existing_request:
            if existing_request.status == 'pending':
                flash('You already have a pending verification request. Please wait for admin review.', 'info')
                return redirect(url_for('verification_submitted'))
            elif existing_request.status == 'approved':
                flash('Your doctor profile is already verified.', 'success')
                return redirect(url_for('doctor_dashboard'))
            elif existing_request.status == 'rejected':
                # Allow searching/claiming but show warning
                flash(f'Your previous request was rejected: {existing_request.admin_notes}. You can submit a new request below.', 'warning')

    search_query = request.args.get('search', '').strip()
    unclaimed_doctors = []

    if search_query:
        # Find doctors without a linked user account
        # Search by both name AND NMC number for better accuracy
        unclaimed_doctors = Doctor.query.outerjoin(User, User.doctor_id == Doctor.id)\
            .filter(
                db.or_(
                    Doctor.name.ilike(f'%{search_query}%'),
                    Doctor.nmc_number.ilike(f'%{search_query}%')
                )
            )\
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

    # Check if user already has ANY pending or approved verification request
    user_id = session['user_id']
    existing_request = VerificationRequest.query.filter_by(
        user_id=user_id
    ).order_by(VerificationRequest.created_at.desc()).first()

    if existing_request:
        if existing_request.status == 'pending':
            flash('You already have a pending verification request. Please wait for admin review.', 'info')
            return redirect(url_for('verification_submitted'))
        elif existing_request.status == 'approved':
            flash('Your doctor profile is already verified.', 'success')
            return redirect(url_for('doctor_dashboard'))
        # If rejected, allow them to claim a different profile

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

    # Check if user already has a pending or approved verification request
    user_id = session['user_id']
    existing_request = VerificationRequest.query.filter_by(
        user_id=user_id
    ).order_by(VerificationRequest.created_at.desc()).first()

    if existing_request and existing_request.status in ['pending', 'approved']:
        flash('You already have a verification request. Cannot submit another.', 'danger')
        return redirect(url_for('user_profile'))

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

        # Validate required file upload (only govt_id is required)
        if not govt_id or not govt_id.filename:
            flash('Government ID is required for verification.', 'danger')
            return redirect(url_for('claim_profile_form', doctor_id=doctor_id))

        # Save files to R2 (with local fallback)
        upload_folder = app.config['UPLOAD_FOLDER']
        govt_id_path = None

        # Try R2 first
        try:
            govt_id_path = r2_storage.save_verification_document(
                govt_id, doctor_id, 'govt_id'
            )
        except Exception as e:
            print(f"R2 upload failed, falling back to local storage: {e}")
            govt_id_path = None

        # Fallback to local storage if R2 fails
        if not govt_id_path:
            try:
                govt_id.seek(0)  # Reset file pointer
            except Exception:
                pass  # File might be closed, try upload anyway

            govt_id_path = upload_utils.save_verification_document(
                govt_id, upload_folder, doctor_id, 'govt_id'
            )
            if not govt_id_path:
                flash('Error uploading government ID. Please try again.', 'danger')
                return redirect(url_for('claim_profile_form', doctor_id=doctor_id))

        # Optional medical degree
        medical_degree_path = None
        if medical_degree and medical_degree.filename:
            try:
                medical_degree_path = r2_storage.save_verification_document(
                    medical_degree, doctor_id, 'medical_degree'
                )
            except Exception as e:
                print(f"R2 upload failed for medical_degree, falling back: {e}")
                medical_degree_path = None

            # Fallback to local if R2 fails
            if not medical_degree_path:
                try:
                    medical_degree.seek(0)
                except Exception:
                    pass
                medical_degree_path = upload_utils.save_verification_document(
                    medical_degree, upload_folder, doctor_id, 'medical_degree'
                )

        # Optional practice license
        practice_license_path = None
        if practice_license and practice_license.filename:
            try:
                practice_license_path = r2_storage.save_verification_document(
                    practice_license, doctor_id, 'practice_license'
                )
            except Exception as e:
                print(f"R2 upload failed for practice_license, falling back: {e}")
                practice_license_path = None

            # Fallback to local if R2 fails
            if not practice_license_path:
                try:
                    practice_license.seek(0)
                except Exception:
                    pass
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

        # Send admin notification
        user = User.query.get(session['user_id'])
        send_admin_verification_notification(verification_request, doctor.name, user.email)

        return redirect(url_for('verification_submitted'))

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
    # If user is already a verified doctor, redirect to dashboard
    if session.get('role') == 'doctor':
        flash('You already have a verified doctor profile.', 'info')
        return redirect(url_for('doctor_dashboard'))

    # Check if user has any verification request
    user_id = session.get('user_id')
    if user_id:
        existing_request = VerificationRequest.query.filter_by(
            user_id=user_id
        ).order_by(VerificationRequest.created_at.desc()).first()

        if existing_request:
            if existing_request.status == 'pending':
                flash('You already have a pending verification request. Please wait for admin review.', 'info')
                return redirect(url_for('verification_submitted'))
            elif existing_request.status == 'approved':
                # User is approved but session might not be updated
                flash('Your doctor profile is already verified.', 'success')
                return redirect(url_for('doctor_dashboard'))
            elif existing_request.status == 'rejected':
                # Allow resubmission but show message
                flash(f'Your previous request was rejected: {existing_request.admin_notes}. You can submit a new request below.', 'warning')

    cities = City.query.order_by(City.name).all()
    specialties = Specialty.query.order_by(Specialty.name).all()
    return render_template('doctor_self_register.html', cities=cities, specialties=specialties)


@app.route('/doctor/self-register/submit', methods=['POST'])
@login_required
def doctor_self_register_submit():
    """Process doctor self-registration submission"""
    # Check if user already has a pending or approved verification request
    user_id = session['user_id']
    existing_request = VerificationRequest.query.filter_by(
        user_id=user_id
    ).order_by(VerificationRequest.created_at.desc()).first()

    if existing_request and existing_request.status in ['pending', 'approved']:
        flash('You already have a verification request. Cannot submit another.', 'danger')
        return redirect(url_for('user_profile'))

    try:
        # Get form data - all fields are mandatory
        name = text_utils.normalize_name(request.form.get('name', '').strip())
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

        # Check if THIS USER already has a pending verification request
        existing_request = VerificationRequest.query.filter_by(
            user_id=session['user_id'],
            status='pending'
        ).first()
        if existing_request:
            flash('You already have a pending verification request. Please wait for admin review.', 'info')
            return redirect(url_for('verification_submitted'))

        # Note: We intentionally allow multiple users to submit with the same NMC number
        # Admin will review all requests and approve the legitimate one
        # This prevents real doctors from being locked out by fraudulent submissions
        # Admin sees red "Duplicate" warnings and can compare documents side-by-side

        # Handle file uploads - only govt_id is mandatory
        medical_degree = request.files.get('medical_degree')
        govt_id = request.files.get('govt_id')
        practice_license = request.files.get('practice_license')

        if not govt_id or not govt_id.filename:
            flash('Government ID is required for verification.', 'danger')
            return redirect(url_for('doctor_self_register'))

        # Create a temporary doctor ID for file storage (use user_id as placeholder)
        temp_doctor_id = f"new_{session['user_id']}"

        # Save files to R2 (with local fallback)
        upload_folder = app.config['UPLOAD_FOLDER']
        govt_id_path = None

        # Try R2 first
        try:
            govt_id_path = r2_storage.save_verification_document(
                govt_id, temp_doctor_id, 'govt_id'
            )
        except Exception as e:
            print(f"R2 upload failed, falling back to local storage: {e}")
            govt_id_path = None

        # Fallback to local storage if R2 fails
        if not govt_id_path:
            try:
                govt_id.seek(0)  # Reset file pointer
            except Exception:
                pass  # File might be closed, try upload anyway

            govt_id_path = upload_utils.save_verification_document(
                govt_id, upload_folder, temp_doctor_id, 'govt_id'
            )
            if not govt_id_path:
                flash('Error uploading government ID. Please try again.', 'danger')
                return redirect(url_for('doctor_self_register'))

        # Optional medical degree
        medical_degree_path = None
        if medical_degree and medical_degree.filename:
            try:
                medical_degree_path = r2_storage.save_verification_document(
                    medical_degree, temp_doctor_id, 'medical_degree'
                )
            except Exception as e:
                print(f"R2 upload failed for medical_degree, falling back: {e}")
                medical_degree_path = None

            # Fallback to local if R2 fails
            if not medical_degree_path:
                try:
                    medical_degree.seek(0)
                except Exception:
                    pass
                medical_degree_path = upload_utils.save_verification_document(
                    medical_degree, upload_folder, temp_doctor_id, 'medical_degree'
                )

        # Optional practice license
        practice_license_path = None
        if practice_license and practice_license.filename:
            try:
                practice_license_path = r2_storage.save_verification_document(
                    practice_license, temp_doctor_id, 'practice_license'
                )
            except Exception as e:
                print(f"R2 upload failed for practice_license, falling back: {e}")
                practice_license_path = None

            # Fallback to local if R2 fails
            if not practice_license_path:
                try:
                    practice_license.seek(0)
                except Exception:
                    pass
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

        # Send admin notification
        user = User.query.get(user_id)
        send_admin_verification_notification(verification_request, name, user.email)

        return redirect(url_for('verification_submitted'))

    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('doctor_self_register'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while processing your registration: {str(e)}', 'danger')
        return redirect(url_for('doctor_self_register'))


@app.route('/verification/submitted')
@login_required
def verification_submitted():
    """Show verification submitted confirmation page"""
    user = User.query.get(session['user_id'])
    return render_template('verification_submitted.html', user=user)


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

    # Get stats for social proof section
    total_doctors = Doctor.query.filter_by(is_active=True).count()  # All doctors (NMC city = practice location)
    total_cities = City.query.count()
    total_reviews = Rating.query.count()
    verified_doctors = Doctor.query.filter_by(is_verified=True, is_active=True).count()
    featured_clinics = Clinic.query.filter_by(is_active=True)\
        .order_by(Clinic.is_featured.desc(), Clinic.name.asc())\
        .limit(6).all()

    return render_template('index.html',
                         cities=cities,
                         specialties=specialties,
                         total_doctors=total_doctors,
                         total_cities=total_cities,
                         total_reviews=total_reviews,
                         verified_doctors=verified_doctors,
                         featured_clinics=featured_clinics)

@app.route('/test-homepage')
def test_homepage():
    """Test route for improved homepage design"""
    cities = City.query.all()
    specialties = Specialty.query.all()

    # Get stats for social proof section
    total_doctors = Doctor.query.filter_by(is_active=True).count()
    total_cities = City.query.count()
    total_reviews = Rating.query.count()
    verified_doctors = Doctor.query.filter_by(is_verified=True, is_active=True).count()
    featured_clinics = Clinic.query.filter_by(is_active=True)\
        .order_by(Clinic.is_featured.desc(), Clinic.name.asc())\
        .limit(6).all()

    return render_template('index_improved.html',
                         cities=cities,
                         specialties=specialties,
                         total_doctors=total_doctors,
                         total_cities=total_cities,
                         total_reviews=total_reviews,
                         verified_doctors=verified_doctors,
                         featured_clinics=featured_clinics)

@app.route('/clinics')
def clinics():
    clinics = Clinic.query.filter_by(is_active=True).order_by(Clinic.is_featured.desc(), Clinic.name.asc()).all()
    return render_template('clinics.html', clinics=clinics)


@app.route('/clinic/<slug>')
def clinic_profile(slug):
    clinic = Clinic.query.filter_by(slug=slug, is_active=True).first_or_404()
    doctors = Doctor.query.filter_by(clinic_id=clinic.id, is_active=True).order_by(Doctor.name.asc()).all()
    return render_template('clinic_profile.html', clinic=clinic, doctors=doctors)

@app.route('/doctors')
def get_doctors():
    city_id = request.args.get('city_id', '')
    specialty_id = request.args.get('specialty_id', '')
    name_search = request.args.get('name', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Limit results per page

    # Build query with rating aggregates and eager loading to prevent N+1 queries
    from sqlalchemy import func, case, and_
    from sqlalchemy.orm import selectinload

    avg_rating = func.coalesce(func.avg(Rating.rating), 0).label('avg_rating')
    rating_count = func.count(Rating.id).label('rating_count')
    sort_rank = case(
        (and_(Doctor.is_featured.is_(True), Doctor.is_verified.is_(True)), 0),
        (Doctor.is_verified.is_(True), 1),
        (rating_count > 0, 2),
        else_=3
    ).label('sort_rank')

    rating_stats = db.session.query(
        Doctor.id.label('doctor_id'),
        avg_rating,
        rating_count,
        sort_rank
    ).outerjoin(Rating).group_by(Doctor.id).subquery()

    query = db.session.query(
        Doctor,
        rating_stats.c.avg_rating,
        rating_stats.c.rating_count,
        rating_stats.c.sort_rank
    ).join(rating_stats, Doctor.id == rating_stats.c.doctor_id).options(
        selectinload(Doctor.city),
        selectinload(Doctor.specialty),
        selectinload(Doctor.clinic)
    ).filter(Doctor.is_active.is_(True))  # Show all active doctors (NMC city = practice location)

    if city_id:
        query = query.filter(Doctor.city_id == int(city_id))

    if specialty_id:
        query = query.filter(Doctor.specialty_id == int(specialty_id))

    if name_search:
        # Search by doctor or clinic name (case-insensitive partial match)
        query = query.outerjoin(Clinic).filter(
            or_(
                Doctor.name.ilike(f'%{name_search}%'),
                Clinic.name.ilike(f'%{name_search}%')
            )
        )

    # Get total count BEFORE pagination for pagination UI
    total_doctors = query.count()
    total_pages = (total_doctors + per_page - 1) // per_page  # Ceiling division

    # Order by priority:
    # 1) Featured + verified, 2) Verified, 3) Highest rated, 4) Others
    query = query.order_by(
        rating_stats.c.sort_rank.asc(),
        rating_stats.c.avg_rating.desc(),
        Doctor.name.asc()
    )

    # Paginate results using offset and limit
    offset = (page - 1) * per_page
    doctors = query.offset(offset).limit(per_page).all()

    # Serialize to JSON
    doctors_list = []
    for d, avg_rating_value, rating_count_value, _sort_rank in doctors:
        # Generate proper photo URL
        photo_url = None
        if d.photo_url:
            # Extract filename/path for serve_photo route
            if d.photo_url.count('/') > 1:
                # R2 format: photos/{doctor_id}/{filename}
                # Remove 'photos/' prefix for the route
                photo_path = d.photo_url.replace('photos/', '')
            else:
                # Local format: photos/{filename}
                photo_path = d.photo_url.split('/')[-1]

            photo_url = url_for('serve_photo', filename=photo_path, _external=False)

        doctors_list.append({
            'id': d.id,
            'name': d.name,
            'slug': d.slug,
            'city_id': d.city_id,
            'city_name': d.city.name,
            'clinic_name': d.clinic.name if d.clinic else None,
            'clinic_slug': d.clinic.slug if d.clinic else None,
            'specialty_id': d.specialty_id,
            'specialty_name': d.specialty.name,
            'nmc_number': d.nmc_number,
            'workplace': d.workplace,
            'experience': d.experience,
            'education': d.education,
            'college': d.college,
            'description': d.description,
            'photo_url': photo_url,
            'is_featured': d.is_featured,
            'is_verified': d.is_verified,
            'avg_rating': float(avg_rating_value or 0),
            'rating_count': int(rating_count_value or 0)
        })

    return jsonify({
        'doctors': doctors_list,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_doctors': total_doctors,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    })

@app.route('/admin/doctors')
@admin_required
def admin_doctors():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Show 50 doctors per page

    query = Doctor.query.options(joinedload(Doctor.city), joinedload(Doctor.specialty), joinedload(Doctor.clinic))
    search = request.args.get('q', '').strip()
    if search:
        query = query.filter(Doctor.name.ilike(f"%{search}%"))

    # Paginate instead of loading all at once
    pagination = query.order_by(Doctor.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template('admin_doctors.html',
                         doctors=pagination.items,
                         pagination=pagination,
                         search=search)

@app.route('/admin/doctors/new', methods=['GET', 'POST'])
@admin_required
def admin_doctor_new():
    cities = City.query.order_by(City.name.asc()).all()
    specialties = Specialty.query.order_by(Specialty.name.asc()).all()
    clinics = Clinic.query.order_by(Clinic.name.asc()).all()
    if request.method == 'POST':
        name = text_utils.normalize_name(request.form.get('name', '').strip())
        nmc_number = request.form.get('nmc_number', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        workplace = request.form.get('workplace', '').strip()
        practice_address = request.form.get('practice_address', '').strip()
        external_clinic_url = request.form.get('external_clinic_url', '').strip()
        city_id = request.form.get('city_id')
        specialty_id = request.form.get('specialty_id')
        clinic_id = request.form.get('clinic_id') or None
        experience_raw = request.form.get('experience', '').strip()
        education = request.form.get('education', '').strip()
        college = request.form.get('college', '').strip()
        description = request.form.get('description', '').strip()
        is_featured = bool(request.form.get('is_featured'))
        is_active = bool(request.form.get('is_active'))
        is_verified = bool(request.form.get('is_verified'))

        # Collect working hours from form
        working_hours_dict = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            hours = request.form.get(day, '').strip()
            if hours:  # Only include days with hours specified
                working_hours_dict[day] = hours

        # Convert to JSON string (or None if no hours specified)
        working_hours_json = json.dumps(working_hours_dict) if working_hours_dict else None

        # Convert string "None" to empty string (form may submit "None" as text)
        if nmc_number.lower() == 'none':
            nmc_number = ''
        if phone_number.lower() == 'none':
            phone_number = ''
        if workplace.lower() == 'none':
            workplace = ''
        if practice_address.lower() == 'none':
            practice_address = ''
        if external_clinic_url.lower() == 'none':
            external_clinic_url = ''
        if education.lower() == 'none':
            education = ''
        if college.lower() == 'none':
            college = ''
        if description.lower() == 'none':
            description = ''

        if not name or not city_id or not specialty_id:
            flash('Name, city, and specialty are required.', 'danger')
            return render_template('admin_doctor_form.html', doctor=None, cities=cities, specialties=specialties, clinics=clinics)

        # Validate field lengths (prevent database errors)
        validation_errors = []
        if len(name) > 200:
            validation_errors.append('Doctor name must be less than 200 characters')
        if nmc_number and len(nmc_number) > 50:
            validation_errors.append('NMC number must be less than 50 characters')
        if phone_number and len(phone_number) > 20:
            validation_errors.append('Phone number must be less than 20 characters (use only one number)')
        if workplace and len(workplace) > 200:
            validation_errors.append('Workplace must be less than 200 characters')
        if practice_address and len(practice_address) > 500:
            validation_errors.append('Practice address must be less than 500 characters')
        if external_clinic_url and len(external_clinic_url) > 500:
            validation_errors.append('External clinic URL must be less than 500 characters')
        if education and len(education) > 200:
            validation_errors.append('Education must be less than 200 characters')
        if college and len(college) > 200:
            validation_errors.append('College must be less than 200 characters')

        if validation_errors:
            for error in validation_errors:
                flash(error, 'danger')
            return render_template('admin_doctor_form.html', doctor=None, cities=cities, specialties=specialties, clinics=clinics)

        # Check if NMC number already exists
        # Skip validation if NMC number is empty or "None" string
        if nmc_number and nmc_number.lower() != 'none':
            existing = Doctor.query.filter_by(nmc_number=nmc_number).first()
            if existing:
                flash(f'NMC number {nmc_number} is already registered to {existing.name}.', 'danger')
                return render_template('admin_doctor_form.html', doctor=None, cities=cities, specialties=specialties, clinics=clinics)

        experience = int(experience_raw) if experience_raw.isdigit() else None
        slug = generate_unique_slug(name)

        doctor = Doctor(
            name=name,
            slug=slug,
            nmc_number=nmc_number or None,
            phone_number=phone_number or None,
            workplace=workplace or None,
            practice_address=practice_address or None,
            external_clinic_url=external_clinic_url or None,
            city_id=int(city_id),
            specialty_id=int(specialty_id),
            clinic_id=int(clinic_id) if clinic_id else None,
            experience=experience,
            education=education or None,
            college=college or None,
            description=description or None,
            photo_url=None,  # Will be set after photo upload
            working_hours=working_hours_json,
            is_featured=is_featured,
            is_active=is_active,
            is_verified=is_verified
        )
        try:
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

        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            if 'too long' in error_msg.lower() or 'value too long' in error_msg.lower():
                flash('One or more fields are too long. Please shorten your input.', 'danger')
            elif 'duplicate' in error_msg.lower() or 'unique' in error_msg.lower():
                flash('This doctor may already exist in the database.', 'danger')
            else:
                flash(f'Error adding doctor: {error_msg}', 'danger')
            return render_template('admin_doctor_form.html', doctor=None, cities=cities, specialties=specialties, clinics=clinics)

    return render_template('admin_doctor_form.html', doctor=None, cities=cities, specialties=specialties, clinics=clinics)

@app.route('/admin/doctors/<int:doctor_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_doctor_edit(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    cities = City.query.order_by(City.name.asc()).all()
    specialties = Specialty.query.order_by(Specialty.name.asc()).all()
    clinics = Clinic.query.order_by(Clinic.name.asc()).all()

    if request.method == 'POST':
        name = text_utils.normalize_name(request.form.get('name', '').strip())
        nmc_number = request.form.get('nmc_number', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        workplace = request.form.get('workplace', '').strip()
        practice_address = request.form.get('practice_address', '').strip()
        external_clinic_url = request.form.get('external_clinic_url', '').strip()
        city_id = request.form.get('city_id')
        specialty_id = request.form.get('specialty_id')
        clinic_id = request.form.get('clinic_id') or None
        experience_raw = request.form.get('experience', '').strip()
        education = request.form.get('education', '').strip()
        college = request.form.get('college', '').strip()
        description = request.form.get('description', '').strip()
        is_featured = bool(request.form.get('is_featured'))
        is_active = bool(request.form.get('is_active'))
        is_verified = bool(request.form.get('is_verified'))

        # Collect working hours from form
        working_hours_dict = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            hours = request.form.get(day, '').strip()
            if hours:  # Only include days with hours specified
                working_hours_dict[day] = hours

        # Convert to JSON string (or None if no hours specified)
        working_hours_json = json.dumps(working_hours_dict) if working_hours_dict else None

        # Convert string "None" to empty string (form may submit "None" as text)
        if nmc_number.lower() == 'none':
            nmc_number = ''
        if phone_number.lower() == 'none':
            phone_number = ''
        if workplace.lower() == 'none':
            workplace = ''
        if practice_address.lower() == 'none':
            practice_address = ''
        if external_clinic_url.lower() == 'none':
            external_clinic_url = ''
        if education.lower() == 'none':
            education = ''
        if college.lower() == 'none':
            college = ''
        if description.lower() == 'none':
            description = ''

        if not name or not city_id or not specialty_id:
            flash('Name, city, and specialty are required.', 'danger')
            return render_template('admin_doctor_form.html', doctor=doctor, cities=cities, specialties=specialties, clinics=clinics)

        # Validate field lengths (prevent database errors)
        validation_errors = []
        if len(name) > 200:
            validation_errors.append('Doctor name must be less than 200 characters')
        if nmc_number and len(nmc_number) > 50:
            validation_errors.append('NMC number must be less than 50 characters')
        if phone_number and len(phone_number) > 20:
            validation_errors.append('Phone number must be less than 20 characters (use only one number)')
        if workplace and len(workplace) > 200:
            validation_errors.append('Workplace must be less than 200 characters')
        if practice_address and len(practice_address) > 500:
            validation_errors.append('Practice address must be less than 500 characters')
        if external_clinic_url and len(external_clinic_url) > 500:
            validation_errors.append('External clinic URL must be less than 500 characters')
        if education and len(education) > 200:
            validation_errors.append('Education must be less than 200 characters')
        if college and len(college) > 200:
            validation_errors.append('College must be less than 200 characters')

        if validation_errors:
            for error in validation_errors:
                flash(error, 'danger')
            return render_template('admin_doctor_form.html', doctor=doctor, cities=cities, specialties=specialties, clinics=clinics)

        # Check if NMC number already exists (if changing it)
        # Skip validation if NMC number is empty or "None" string
        if nmc_number and nmc_number.lower() != 'none' and nmc_number != doctor.nmc_number:
            existing = Doctor.query.filter_by(nmc_number=nmc_number).first()
            if existing and existing.id != doctor.id:
                flash(f'NMC number {nmc_number} is already registered to {existing.name}.', 'danger')
                return render_template('admin_doctor_form.html', doctor=doctor, cities=cities, specialties=specialties, clinics=clinics)

        if name != doctor.name:
            doctor.slug = generate_unique_slug(name, doctor_id=doctor.id)

        doctor.name = name
        doctor.nmc_number = nmc_number or None
        doctor.phone_number = phone_number or None
        doctor.workplace = workplace or None
        doctor.practice_address = practice_address or None
        doctor.external_clinic_url = external_clinic_url or None
        doctor.city_id = int(city_id)
        doctor.specialty_id = int(specialty_id)
        doctor.clinic_id = int(clinic_id) if clinic_id else None
        doctor.experience = int(experience_raw) if experience_raw.isdigit() else None
        doctor.education = education or None
        doctor.college = college or None
        doctor.description = description or None
        doctor.working_hours = working_hours_json
        doctor.is_featured = is_featured
        doctor.is_active = is_active
        doctor.is_verified = is_verified

        try:
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

        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            if 'too long' in error_msg.lower() or 'value too long' in error_msg.lower():
                flash('One or more fields are too long. Please shorten your input.', 'danger')
            elif 'duplicate' in error_msg.lower() or 'unique' in error_msg.lower():
                flash('This doctor may already exist in the database.', 'danger')
            else:
                flash(f'Error updating doctor: {error_msg}', 'danger')
            return render_template('admin_doctor_form.html', doctor=doctor, cities=cities, specialties=specialties, clinics=clinics)

    return render_template('admin_doctor_form.html', doctor=doctor, cities=cities, specialties=specialties, clinics=clinics)

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
    # Pagination to handle 1000+ cities
    page = request.args.get('page', 1, type=int)
    per_page = 50

    pagination = City.query.order_by(City.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template('admin_cities.html',
                         cities=pagination.items,
                         pagination=pagination)


@app.route('/admin/clinics')
@admin_required
def admin_clinics():
    # Pagination for better performance
    page = request.args.get('page', 1, type=int)
    per_page = 50

    pagination = Clinic.query.options(joinedload(Clinic.city)).order_by(Clinic.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template('admin_clinics.html',
                         clinics=pagination.items,
                         pagination=pagination)


@app.route('/admin/clinics/new', methods=['GET', 'POST'])
@admin_required
def admin_clinic_new():
    cities = City.query.order_by(City.name.asc()).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city_id = request.form.get('city_id')
        address = request.form.get('address', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        description = request.form.get('description', '').strip()
        is_featured = bool(request.form.get('is_featured'))
        is_active = bool(request.form.get('is_active'))

        if not name or not city_id:
            flash('Clinic name and city are required.', 'danger')
            return render_template('admin_clinic_form.html', clinic=None, cities=cities)

        slug = generate_unique_clinic_slug(name)
        clinic = Clinic(
            name=name,
            slug=slug,
            city_id=int(city_id),
            address=address or None,
            phone_number=phone_number or None,
            description=description or None,
            is_featured=is_featured,
            is_active=is_active
        )
        db.session.add(clinic)
        db.session.commit()
        flash('Clinic added successfully.', 'success')
        return redirect(url_for('admin_clinics'))

    return render_template('admin_clinic_form.html', clinic=None, cities=cities)


@app.route('/admin/clinics/<int:clinic_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_clinic_edit(clinic_id):
    clinic = Clinic.query.get_or_404(clinic_id)
    cities = City.query.order_by(City.name.asc()).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city_id = request.form.get('city_id')
        address = request.form.get('address', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        description = request.form.get('description', '').strip()
        is_featured = bool(request.form.get('is_featured'))
        is_active = bool(request.form.get('is_active'))

        if not name or not city_id:
            flash('Clinic name and city are required.', 'danger')
            return render_template('admin_clinic_form.html', clinic=clinic, cities=cities)

        if name != clinic.name:
            clinic.slug = generate_unique_clinic_slug(name, clinic_id=clinic.id)

        clinic.name = name
        clinic.city_id = int(city_id)
        clinic.address = address or None
        clinic.phone_number = phone_number or None
        clinic.description = description or None
        clinic.is_featured = is_featured
        clinic.is_active = is_active

        db.session.commit()
        flash('Clinic updated successfully.', 'success')
        return redirect(url_for('admin_clinics'))

    return render_template('admin_clinic_form.html', clinic=clinic, cities=cities)


@app.route('/admin/clinics/<int:clinic_id>/delete', methods=['POST'])
@admin_required
def admin_clinic_delete(clinic_id):
    clinic = Clinic.query.get_or_404(clinic_id)
    if Doctor.query.filter_by(clinic_id=clinic.id).count() > 0:
        flash('Clinic cannot be deleted while doctors are assigned.', 'warning')
        return redirect(url_for('admin_clinics'))

    db.session.delete(clinic)
    db.session.commit()
    flash('Clinic deleted successfully.', 'success')
    return redirect(url_for('admin_clinics'))

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
    # Pagination for better performance and consistency
    page = request.args.get('page', 1, type=int)
    per_page = 50

    pagination = Specialty.query.order_by(Specialty.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template('admin_specialties.html',
                         specialties=pagination.items,
                         pagination=pagination)

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

# --- Admin Article Routes ---
@app.route('/admin/articles')
@admin_required
def admin_articles():
    """List all articles (published and drafts)"""
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin_articles.html', articles=articles)

@app.route('/admin/articles/new', methods=['GET', 'POST'])
@admin_required
def admin_article_new():
    """Create new article"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id')
        summary = request.form.get('summary', '').strip()
        content = request.form.get('content', '').strip()
        meta_description = request.form.get('meta_description', '').strip()
        meta_keywords = request.form.get('meta_keywords', '').strip()
        related_specialty_id = request.form.get('related_specialty_id') or None
        is_published = request.form.get('is_published') == 'on'
        is_featured = request.form.get('is_featured') == 'on'

        if not title or not content or not category_id:
            flash('Title, category, and content are required.', 'danger')
            categories = ArticleCategory.query.order_by(ArticleCategory.display_order).all()
            specialties = Specialty.query.order_by(Specialty.name).all()
            return render_template('admin_article_form.html', article=None, categories=categories, specialties=specialties)

        # Handle image upload
        featured_image = None
        if 'featured_image' in request.files:
            image_file = request.files['featured_image']
            if image_file and image_file.filename:
                # Optimize and save image
                featured_image = optimize_and_save_article_image(image_file)
                if not featured_image:
                    flash('Error processing image. Please try again or use a different image.', 'warning')

        # Generate slug from title
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        # Make sure slug is unique
        base_slug = slug
        counter = 1
        while Article.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        article = Article(
            title=title,
            slug=slug,
            category_id=category_id,
            summary=summary or None,
            content=content,
            featured_image=featured_image,
            meta_description=meta_description or None,
            meta_keywords=meta_keywords or None,
            related_specialty_id=related_specialty_id,
            is_published=is_published,
            is_featured=is_featured,
            published_at=datetime.utcnow() if is_published else None
        )
        db.session.add(article)
        db.session.commit()
        flash('Article created successfully!', 'success')
        return redirect(url_for('admin_articles'))

    categories = ArticleCategory.query.order_by(ArticleCategory.display_order).all()
    specialties = Specialty.query.order_by(Specialty.name).all()
    return render_template('admin_article_form.html', article=None, categories=categories, specialties=specialties)

@app.route('/admin/articles/<int:article_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_article_edit(article_id):
    """Edit existing article"""
    article = Article.query.get_or_404(article_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id')
        summary = request.form.get('summary', '').strip()
        content = request.form.get('content', '').strip()
        meta_description = request.form.get('meta_description', '').strip()
        meta_keywords = request.form.get('meta_keywords', '').strip()
        related_specialty_id = request.form.get('related_specialty_id') or None
        was_published = article.is_published
        is_published = request.form.get('is_published') == 'on'
        is_featured = request.form.get('is_featured') == 'on'

        if not title or not content or not category_id:
            flash('Title, category, and content are required.', 'danger')
            categories = ArticleCategory.query.order_by(ArticleCategory.display_order).all()
            specialties = Specialty.query.order_by(Specialty.name).all()
            return render_template('admin_article_form.html', article=article, categories=categories, specialties=specialties)

        # Handle image upload (keep existing image if no new one uploaded)
        if 'featured_image' in request.files:
            image_file = request.files['featured_image']
            if image_file and image_file.filename:
                # Optimize and save new image
                new_image_path = optimize_and_save_article_image(image_file)
                if new_image_path:
                    # Delete old image file if it exists
                    if article.featured_image:
                        old_image_path = os.path.join('static', article.featured_image)
                        if os.path.exists(old_image_path):
                            try:
                                os.remove(old_image_path)
                            except:
                                pass  # Ignore errors if file doesn't exist
                    article.featured_image = new_image_path
                else:
                    flash('Error processing new image. Keeping existing image.', 'warning')

        article.title = title
        article.category_id = category_id
        article.summary = summary or None
        article.content = content
        article.meta_description = meta_description or None
        article.meta_keywords = meta_keywords or None
        article.related_specialty_id = related_specialty_id
        article.is_published = is_published
        article.is_featured = is_featured

        # Set published_at if publishing for the first time
        if is_published and not was_published:
            article.published_at = datetime.utcnow()

        db.session.commit()
        flash('Article updated successfully!', 'success')
        return redirect(url_for('admin_articles'))

    categories = ArticleCategory.query.order_by(ArticleCategory.display_order).all()
    specialties = Specialty.query.order_by(Specialty.name).all()
    return render_template('admin_article_form.html', article=article, categories=categories, specialties=specialties)

@app.route('/admin/articles/<int:article_id>/clean-debug', methods=['GET'])
@admin_required
def admin_article_clean_debug(article_id):
    """Remove debug text from article content (one-time cleanup)"""
    import re
    article = Article.query.get_or_404(article_id)

    original_content = article.content
    updated_content = original_content

    # Remove debug text patterns
    debug_patterns = [
        r'Related Specialty:.*?production database\)',
        r'Related Specialty:.*?Dentist',
        r'Category: Oral Health',
        r'Recommended doctor specialty:.*?\)',
        r'based on your production database',
        r'\(ID \d+ based on your production database\)'
    ]

    for pattern in debug_patterns:
        updated_content = re.sub(pattern, '', updated_content, flags=re.DOTALL | re.IGNORECASE)

    # Clean up extra whitespace
    updated_content = re.sub(r'\n\n\n+', '\n\n', updated_content)
    updated_content = updated_content.strip()

    if original_content != updated_content:
        article.content = updated_content
        db.session.commit()
        chars_removed = len(original_content) - len(updated_content)
        flash(f'✅ Debug text removed successfully! ({chars_removed} characters cleaned)', 'success')
    else:
        flash('ℹ️ No debug text found to remove', 'info')

    return redirect(url_for('admin_article_edit', article_id=article_id))

@app.route('/admin/articles/<int:article_id>/delete', methods=['POST'])
@admin_required
def admin_article_delete(article_id):
    """Delete article"""
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted successfully.', 'success')
    return redirect(url_for('admin_articles'))

@app.route('/admin/email-composer')
@admin_required
def admin_email_composer():
    """Email composer for sending emails to doctors"""
    # Get all verified doctors (user_account backref will load user if exists)
    verified_doctors = Doctor.query.filter_by(is_verified=True)\
        .order_by(Doctor.name).all()

    return render_template('admin_email_composer.html',
                         verified_doctors=verified_doctors)

@app.route('/admin/send-email', methods=['POST'])
@admin_required
def admin_send_email():
    """Send email to doctor(s)"""
    doctor_id = request.form.get('doctor_id')
    recipient_email = request.form.get('recipient_email', '').strip()
    subject = request.form.get('subject', '').strip()
    body = request.form.get('body', '').strip()

    # Validate inputs
    if not subject or not body:
        flash('Subject and body are required', 'danger')
        return redirect(url_for('admin_email_composer'))

    # Determine recipient
    to_email = None
    doctor_name = None

    if doctor_id:
        # Selected from dropdown
        doctor = Doctor.query.get(doctor_id)
        if doctor and doctor.user_account:
            to_email = doctor.user_account.email
            doctor_name = doctor.name
        else:
            flash('Selected doctor does not have an email address', 'danger')
            return redirect(url_for('admin_email_composer'))
    elif recipient_email:
        # Manual email entry
        to_email = recipient_email
        doctor_name = recipient_email.split('@')[0]  # Use email prefix as fallback
    else:
        flash('Please select a doctor or enter an email address', 'danger')
        return redirect(url_for('admin_email_composer'))

    # Send email using Resend
    try:
        # Wrap body in professional HTML template
        html_body = f"""
        <div style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #111;">
            {body}
        </div>
        """

        params = {
            "from": "RankSewa Support <support@ranksewa.com>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
            "reply_to": "support@ranksewa.com"
        }

        response = resend.Emails.send(params)

        flash(f'✅ Email sent successfully to {to_email}!', 'success')
        print(f"[EMAIL] Sent to {to_email}: {subject}")

    except Exception as e:
        flash(f'❌ Failed to send email: {str(e)}', 'danger')
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")
        return redirect(url_for('admin_email_composer'))

    return redirect(url_for('admin_email_composer'))

@app.route('/admin/users')
@admin_required
def admin_users():
    # Pagination for scalability
    page = request.args.get('page', 1, type=int)
    per_page = 50

    pagination = User.query.order_by(User.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template('admin_users.html',
                         users=pagination.items,
                         pagination=pagination)

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

@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def admin_user_toggle_admin(user_id):
    """Toggle admin status for a user"""
    if session.get('user_id') == user_id:
        flash('You cannot change your own admin status.', 'warning')
        return redirect(url_for('admin_users'))

    user = User.query.get_or_404(user_id)

    # Toggle admin status
    user.is_admin = not user.is_admin
    if user.is_admin:
        user.role = 'admin'
    elif user.role == 'admin':
        user.role = 'patient'  # Revert to patient if they're not a doctor

    db.session.commit()

    if user.is_admin:
        flash(f'{user.name} ({user.email}) is now an admin!', 'success')
    else:
        flash(f'{user.name} ({user.email}) is no longer an admin.', 'info')

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

# --- Admin Route: Import Doctors from Embedded Data ---
@app.route('/admin/import-doctors')
@admin_required
def import_doctors_page():
    """Show import doctors page with button to trigger import"""
    from models import Doctor, City, Specialty
    current_doctor_count = Doctor.query.count()

    # Debug info
    cities = City.query.all()
    specialties = Specialty.query.all()

    # Check if specific doctors exist
    test_doctors = [
        "Prof. Dr. Anil Kumar Jha",
        "Dr. Mahesh Shah",
        "Prof. Dr. Prakash Kafle"
    ]
    found_doctors = []
    for name in test_doctors:
        doctor = Doctor.query.filter(Doctor.name.ilike(name)).first()
        if doctor:
            found_doctors.append(f"{name} (found)")
        else:
            found_doctors.append(f"{name} (NOT FOUND)")

    return render_template('admin_import_doctors.html',
                         current_doctor_count=current_doctor_count,
                         cities=cities,
                         specialties=specialties,
                         found_doctors=found_doctors)

@app.route('/admin/import-doctors/run', methods=['POST'])
@admin_required
def run_import_doctors():
    """Execute the doctor import from embedded data"""
    try:
        # Import the function from the embedded script
        from import_doctors_embedded import import_doctors, DOCTORS_DATA

        # Capture output
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        # Run the import (use_app_context=False since we're already in a Flask route)
        import_doctors(use_app_context=False)

        # Get the output
        output = buffer.getvalue()
        sys.stdout = old_stdout

        flash('Doctor import completed! Check the results below.', 'success')
        return render_template('admin_import_result.html', output=output)

    except Exception as e:
        flash(f'Error during import: {str(e)}', 'danger')
        return redirect(url_for('import_doctors_page'))

@app.route('/admin/activate-all-doctors', methods=['POST'])
@admin_required
def activate_all_doctors():
    """Activate all inactive doctors (one-time fix)"""
    try:
        inactive_doctors = Doctor.query.filter_by(is_active=False).all()
        count = len(inactive_doctors)

        for doctor in inactive_doctors:
            doctor.is_active = True

        db.session.commit()

        flash(f'Successfully activated {count} doctors! They should now appear on the homepage.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error activating doctors: {str(e)}', 'danger')

    return redirect(url_for('import_doctors_page'))

@app.route('/admin/import-bnc-doctors/run', methods=['POST'])
@admin_required
def run_import_bnc_doctors():
    """Import doctors from B&C Medical College"""
    try:
        # Import the function from the B&C import script
        from import_bnc_doctors import import_bnc_doctors

        # Capture output
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        # Run the import
        import_bnc_doctors()

        # Get the output
        output = buffer.getvalue()
        sys.stdout = old_stdout

        flash('B&C Medical College doctors import completed!', 'success')
        return render_template('admin_import_result.html', output=output)

    except Exception as e:
        flash(f'Error during B&C import: {str(e)}', 'danger')
        return redirect(url_for('import_doctors_page'))

@app.route('/admin/add-workplace-field', methods=['POST'])
@admin_required
def add_workplace_field():
    """Migration: Add workplace field to doctors table"""
    try:
        from add_workplace_field import add_workplace_column

        # Capture output
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        add_workplace_column()

        output = buffer.getvalue()
        sys.stdout = old_stdout

        flash('Workplace field migration completed!', 'success')
        return render_template('admin_import_result.html', output=output)

    except Exception as e:
        flash(f'Error during migration: {str(e)}', 'danger')
        return redirect(url_for('import_doctors_page'))

@app.route('/admin/debug-doctor/<int:doctor_id>')
@admin_required
def debug_doctor(doctor_id):
    """Debug a specific doctor's data"""
    doctor = Doctor.query.get_or_404(doctor_id)

    debug_info = {
        'id': doctor.id,
        'name': doctor.name,
        'slug': doctor.slug,
        'is_active': doctor.is_active,
        'is_verified': doctor.is_verified,
        'is_featured': doctor.is_featured,
        'specialty_id': doctor.specialty_id,
        'specialty_name': doctor.specialty.name if doctor.specialty else 'None',
        'city_id': doctor.city_id,
        'city_name': doctor.city.name if doctor.city else 'None',
        'experience': doctor.experience,
        'avg_rating': doctor.avg_rating,
        'review_count': len(doctor.ratings)
    }

    # Check if this doctor would show up in a search
    test_query = Doctor.query.filter_by(
        is_active=True,
        specialty_id=doctor.specialty_id,
        city_id=doctor.city_id
    ).all()

    flash(f"Debug Info for {doctor.name}: {debug_info}", 'info')
    flash(f"Doctors matching this specialty+city: {len(test_query)} total", 'info')

    return redirect(url_for('admin_doctors'))

@app.route('/admin/merge-duplicate-specialties', methods=['POST'])
@admin_required
def merge_duplicate_specialties():
    """Merge duplicate specialties (e.g., Dermatology -> Dermatologist)"""
    try:
        from fix_duplicate_specialties import SPECIALTY_MAPPINGS

        total_merged = 0
        messages = []

        for target_name, source_names in SPECIALTY_MAPPINGS.items():
            # Find or create target specialty
            target = Specialty.query.filter(Specialty.name.ilike(target_name)).first()

            if not target:
                # Check if any of the source names exist
                for source_name in source_names:
                    source = Specialty.query.filter(Specialty.name.ilike(source_name)).first()
                    if source:
                        # Rename the first found source to target
                        source.name = target_name
                        target = source
                        messages.append(f"Renamed '{source_name}' to '{target_name}'")
                        break

                if not target:
                    continue

            # Now merge all source specialties into target
            for source_name in source_names:
                sources = Specialty.query.filter(Specialty.name.ilike(source_name)).all()

                for source in sources:
                    if source.id == target.id:
                        continue  # Skip self

                    # Move all doctors from source to target
                    doctors = Doctor.query.filter_by(specialty_id=source.id).all()

                    if doctors:
                        for doctor in doctors:
                            doctor.specialty_id = target.id

                        total_merged += len(doctors)
                        messages.append(f"Merged {len(doctors)} doctors from '{source.name}' to '{target.name}'")

                        # Delete the old specialty
                        db.session.delete(source)

        db.session.commit()

        flash(f'Successfully merged duplicate specialties! Moved {total_merged} doctors.', 'success')
        for msg in messages:
            flash(msg, 'info')

    except Exception as e:
        db.session.rollback()
        flash(f'Error merging specialties: {str(e)}', 'danger')

    return redirect(url_for('admin_specialties'))

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
        # Increment total profile views
        doctor.profile_views = (doctor.profile_views or 0) + 1

        # Track daily analytics
        from datetime import date
        from models import DoctorAnalytics
        today = date.today()
        analytics = DoctorAnalytics.query.filter_by(
            doctor_id=doctor.id,
            date=today
        ).first()

        if not analytics:
            analytics = DoctorAnalytics(
                doctor_id=doctor.id,
                date=today,
                profile_views=1,
                search_appearances=0,
                search_clicks=0,
                phone_clicks=0,
                website_clicks=0,
                review_button_clicks=0,
                source_search=0,
                source_homepage=0,
                source_google=0,
                source_direct=0
            )
            db.session.add(analytics)
        else:
            analytics.profile_views += 1

        # Track source
        referrer = request.referrer or ''
        if 'doctors?city' in referrer or 'doctors?specialty' in referrer or 'doctors?' in referrer:
            analytics.source_search = (analytics.source_search or 0) + 1
        elif 'google' in referrer.lower():
            analytics.source_google = (analytics.source_google or 0) + 1
        elif referrer == '' or 'ranksewa.com' not in referrer:
            analytics.source_direct = (analytics.source_direct or 0) + 1
        elif referrer and 'ranksewa.com' in referrer:
            if 'index' in referrer or referrer.endswith('/'):
                analytics.source_homepage = (analytics.source_homepage or 0) + 1
            else:
                analytics.source_direct = (analytics.source_direct or 0) + 1

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

    # Get tier features for access control
    import subscription_config
    tier_features = subscription_config.TIER_FEATURES.get(doctor.subscription_tier, subscription_config.TIER_FEATURES['free'])

    return render_template('doctor_profile.html',
                          doctor=doctor,
                          ratings=ratings,
                          avg_rating=avg_rating,
                          banner_ad=banner_ad,
                          inline_ad=inline_ad,
                          tier_features=tier_features)

@app.route('/rate_doctor', methods=['POST'])
@login_required
def rate_doctor():
    doctor_id = request.form.get('doctor_id')
    rating_value = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session['user_id']

    # New visit experience fields
    visit_time = request.form.get('visit_time')  # Morning/Afternoon/Evening
    had_appointment = request.form.get('had_appointment') == 'yes'  # yes/no -> boolean
    wait_time_minutes = request.form.get('wait_time_minutes')  # integer
    doctor_on_time = request.form.get('doctor_on_time')  # yes/no/null

    if not doctor_id or not rating_value:
        flash('Please provide a rating.', 'danger')
        return redirect(url_for('index'))

    # CRITICAL FIX: Prevent doctors from rating themselves
    user = User.query.get(user_id)
    if user.doctor_id and int(user.doctor_id) == int(doctor_id):
        flash('You cannot rate yourself. Reviews must be from patients.', 'warning')
        doctor = Doctor.query.get(doctor_id)
        return redirect(url_for('doctor_profile', slug=doctor.slug))

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

    # Content moderation check (only if comment provided)
    if comment and comment.strip():
        from content_moderation import moderate_review
        moderation = moderate_review('', comment)
        if not moderation['approved']:
            flash(moderation['message'], 'warning')
            doctor = Doctor.query.get(doctor_id)
            return redirect(url_for('doctor_profile', slug=doctor.slug))

    # Check if this is the first review for this doctor
    is_first_review = Rating.query.filter_by(doctor_id=doctor_id).count() == 0

    # Create new rating with visit experience details
    new_rating = Rating(
        doctor_id=doctor_id,
        user_id=user_id,
        rating=rating_value,
        comment=comment,
        visit_time=visit_time,
        had_appointment=had_appointment,
        wait_time_minutes=int(wait_time_minutes) if wait_time_minutes else None,
        doctor_on_time=True if doctor_on_time == 'yes' else (False if doctor_on_time == 'no' else None)
    )
    db.session.add(new_rating)
    db.session.flush()  # Flush to get the rating ID

    # Award points and badges using gamification system
    from gamification import process_new_review
    user = User.query.get(user_id)
    result = process_new_review(user, new_rating, is_first_for_doctor=is_first_review)

    # Show success message with points earned
    points_msg = f"Your review has been submitted! You earned {result['points']} points"
    if result['badges']:
        badge_names = ', '.join([b.badge_definition.name for b in result['badges']])
        points_msg += f" and unlocked: {badge_names}"
    flash(points_msg, 'success')

    # Get the doctor's slug to redirect correctly
    doctor = Doctor.query.get(doctor_id)
    return redirect(url_for('doctor_profile', slug=doctor.slug))


@app.route('/flag_review', methods=['POST'])
def flag_review():
    """Flag a review as inappropriate (content moderation, NOT for negative reviews)"""
    rating_id = request.form.get('rating_id')
    reason = request.form.get('reason')
    additional_details = request.form.get('additional_details', '').strip()
    doctor_slug = request.form.get('doctor_slug')

    if not rating_id or not reason:
        flash('Please provide a reason for flagging.', 'danger')
        return redirect(url_for('doctor_profile', slug=doctor_slug))

    # Validate reason
    valid_reasons = ['offensive', 'discriminatory', 'false', 'privacy', 'spam']
    if reason not in valid_reasons:
        flash('Invalid flag reason.', 'danger')
        return redirect(url_for('doctor_profile', slug=doctor_slug))

    # Get reporter user ID (null if not logged in - allow anonymous flags)
    reporter_user_id = session.get('user_id', None)

    # Check if this user already flagged this review
    if reporter_user_id:
        existing_flag = ReviewFlag.query.filter_by(
            rating_id=rating_id,
            reporter_user_id=reporter_user_id
        ).first()

        if existing_flag:
            flash('You have already flagged this review. Our team will review it soon.', 'info')
            return redirect(url_for('doctor_profile', slug=doctor_slug))

    try:
        # Create flag
        flag = ReviewFlag(
            rating_id=int(rating_id),
            reporter_user_id=reporter_user_id,
            reason=reason,
            additional_details=additional_details or None
        )

        db.session.add(flag)
        db.session.commit()

        flash('Thank you for reporting. Our team will review this content within 24-48 hours.', 'success')

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error flagging review: {str(e)}")
        flash('Error submitting flag. Please try again.', 'danger')

    return redirect(url_for('doctor_profile', slug=doctor_slug))


@app.route('/mark_helpful', methods=['POST'])
@login_required
def mark_helpful():
    """Mark a review as helpful"""
    rating_id = request.form.get('rating_id')
    doctor_slug = request.form.get('doctor_slug')
    user_id = session['user_id']

    if not rating_id:
        flash('Invalid review.', 'danger')
        return redirect(url_for('doctor_profile', slug=doctor_slug))

    rating = Rating.query.get_or_404(rating_id)

    # Don't allow users to mark their own reviews as helpful
    if rating.user_id == user_id:
        flash('You cannot mark your own review as helpful.', 'warning')
        return redirect(url_for('doctor_profile', slug=doctor_slug))

    # Check if already marked helpful by this user
    existing_vote = ReviewHelpful.query.filter_by(
        rating_id=rating_id,
        user_id=user_id
    ).first()

    if existing_vote:
        # Remove the helpful vote (toggle off)
        db.session.delete(existing_vote)
        db.session.commit()
        flash('Helpful vote removed.', 'info')
    else:
        # Add helpful vote
        helpful_vote = ReviewHelpful(
            rating_id=rating_id,
            user_id=user_id
        )
        db.session.add(helpful_vote)
        db.session.flush()

        # Award points to the review author
        from gamification import process_helpful_vote
        review_author = rating.user
        result = process_helpful_vote(review_author, rating)

        flash('Marked as helpful!', 'success')

    return redirect(url_for('doctor_profile', slug=doctor_slug))


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

                    # Send verification approved email
                    send_verification_approved_email(user.email, new_doctor.name)

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

                    # Send verification approved email
                    send_verification_approved_email(user.email, doctor.name)

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

                    # Send verification rejected email
                    user = verification_request.user
                    doctor_name = verification_request.proposed_name if verification_request.is_new_doctor else verification_request.doctor.name
                    send_verification_rejected_email(user.email, doctor_name, admin_notes)

                    flash(f'Verification request rejected.', 'info')
                    return redirect(url_for('admin_verification_requests'))

                except Exception as e:
                    db.session.rollback()
                    flash(f'Error rejecting verification: {str(e)}', 'danger')

    # Get all pending requests for duplicate NMC checking
    all_requests = VerificationRequest.query.filter_by(status='pending').all()

    return render_template('admin_verification_detail.html',
                         request=verification_request,
                         all_requests=all_requests)


@app.route('/verification/document/<int:request_id>/<doc_type>')
@admin_required
def serve_verification_document(request_id, doc_type):
    """Serve verification documents from R2 (admin only)"""
    from flask import send_file
    import io

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

    # Get file from R2
    file_content = r2_storage.get_verification_document(doc_path)

    if not file_content:
        flash('Document file not found in storage.', 'warning')
        return redirect(url_for('admin_verification_detail', request_id=request_id))

    # Determine content type based on file extension
    file_ext = doc_path.split('.')[-1].lower()
    content_type_map = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    content_type = content_type_map.get(file_ext, 'application/octet-stream')

    # Create a BytesIO object and send file
    return send_file(
        io.BytesIO(file_content),
        mimetype=content_type,
        as_attachment=False,
        download_name=doc_path.split('/')[-1]
    )


@app.route('/uploads/photos/<path:filename>')
def serve_photo(filename):
    """Serve profile photos from R2 or local storage (publicly accessible)"""
    from flask import send_from_directory, send_file, make_response
    import os
    from io import BytesIO

    # Security: Prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        abort(404)

    # If filename contains doctor ID (R2 format: {doctor_id}/{filename}), try R2 first
    if '/' in filename:
        # Try to fetch from R2
        try:
            from r2_storage import get_verification_document
            # For photos, use photos/{doctor_id}/{filename} format
            r2_path = f"photos/{filename}"
            photo_data = get_verification_document(r2_path)
            if photo_data:
                response = make_response(send_file(
                    BytesIO(photo_data),
                    mimetype='image/jpeg',
                    as_attachment=False
                ))
                # Add cache headers - cache for 7 days (photos rarely change)
                response.headers['Cache-Control'] = 'public, max-age=604800, immutable'
                response.headers['Expires'] = '7 days'
                return response
        except Exception as e:
            print(f"[R2] Error fetching photo from R2: {e}")

        # Extract just the filename for local fallback
        filename = filename.split('/')[-1]

    # Fallback: Try local storage
    photos_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'photos')
    local_path = os.path.join(photos_folder, filename)

    if os.path.exists(local_path):
        response = make_response(send_from_directory(photos_folder, filename))
        # Add cache headers - cache for 7 days
        response.headers['Cache-Control'] = 'public, max-age=604800, immutable'
        response.headers['Expires'] = '7 days'
        return response

    # Photo not found anywhere
    abort(404)


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

    # Get tier features for access control
    import subscription_config
    tier_features = subscription_config.TIER_FEATURES.get(doctor.subscription_tier, subscription_config.TIER_FEATURES['free'])

    return render_template('doctor_dashboard.html',
                         doctor=doctor,
                         user=user,
                         review_count=review_count,
                         avg_rating=avg_rating,
                         response_count=response_count,
                         response_rate=response_rate,
                         verification_request=verification_request,
                         tier_features=tier_features)


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
            doctor.workplace = request.form.get('workplace', '').strip()
            doctor.phone_number = request.form.get('phone_number', '').strip()

            # Experience (convert to int)
            experience_str = request.form.get('experience', '0').strip()
            try:
                doctor.experience = int(experience_str) if experience_str else 0
            except ValueError:
                doctor.experience = 0

            # NMC number (can only be set once)
            if not doctor.nmc_number:
                nmc_input = request.form.get('nmc_number', '').strip()
                if nmc_input:
                    # Check if NMC number already exists for another doctor
                    existing = Doctor.query.filter_by(nmc_number=nmc_input).first()
                    if existing and existing.id != doctor.id:
                        flash('This NMC number is already registered to another doctor.', 'danger')
                    else:
                        doctor.nmc_number = nmc_input
                        flash('NMC number added successfully!', 'success')

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


@app.route('/doctor/working-hours/update', methods=['POST'])
@doctor_required
def doctor_update_working_hours():
    """Update doctor's working hours (Premium/Featured only)"""
    user = User.query.get(session['user_id'])
    doctor = user.doctor_profile

    # Check if doctor has access to working hours feature
    tier = doctor.subscription_tier or 'free'
    tier_features = subscription_config.TIER_FEATURES.get(tier, subscription_config.TIER_FEATURES['free'])

    if not tier_features['can_show_hours']:
        flash('Working hours feature is available with Premium subscription.', 'warning')
        return redirect(url_for('subscription_pricing'))

    try:
        # Collect working hours from form
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        working_hours = {}

        for day in days:
            hours = request.form.get(day, '').strip()
            if hours:  # Only save non-empty values
                working_hours[day] = hours

        # Save as JSON string
        if working_hours:
            doctor.working_hours = json.dumps(working_hours)
            flash('Working hours updated successfully!', 'success')
        else:
            # If all fields are empty, clear working hours
            doctor.working_hours = None
            flash('Working hours cleared.', 'info')

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating working hours: {str(e)}', 'danger')

    return redirect(url_for('doctor_dashboard'))


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
            db.session.flush()

            # Award points to the review author for getting a response
            from gamification import process_doctor_response
            review_author = rating.user
            process_doctor_response(review_author)

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

    # Check if doctor has access to analytics (Premium+)
    import subscription_config
    if not subscription_config.can_access_feature(doctor.subscription_tier, 'can_view_analytics'):
        flash('Analytics dashboard is available with Premium subscription. Upgrade to unlock detailed insights!', 'info')
        return redirect(url_for('subscription_pricing'))

    analytics_context = build_doctor_analytics_context(doctor)

    return render_template('doctor_analytics.html',
                         doctor=doctor,
                         viewer_role='doctor',
                         **analytics_context)


@app.route('/clinic/manager')
@login_required
def clinic_manager_dashboard():
    """Clinic manager dashboard for managing doctor profiles"""
    user = User.query.get(session['user_id'])
    if user.role != 'clinic_manager':
        return render_template('clinic_manager_start.html', user=user)

    clinic_account = ClinicAccount.query.filter_by(manager_user_id=user.id).first()
    if not clinic_account:
        tier_info = subscription_config.get_clinic_tier_info('clinic_starter')
        clinic_account = ClinicAccount(
            manager_user_id=user.id,
            subscription_tier='clinic_starter',
            max_doctors=tier_info['max_doctors']
        )
        db.session.add(clinic_account)
        db.session.commit()

    search_query = request.args.get('search', '').strip()
    search_results = []
    if search_query:
        search_results = Doctor.query.filter(
            Doctor.name.ilike(f'%{search_query}%'),
            Doctor.is_active == True
        ).all()

    managed_links = ClinicManagerDoctor.query.filter_by(manager_user_id=user.id).all()

    return render_template('clinic_manager_dashboard.html',
                         user=user,
                         clinic_account=clinic_account,
                         managed_links=managed_links,
                         search_query=search_query,
                         search_results=search_results)


@app.route('/clinic/manager/activate', methods=['POST'])
@login_required
def clinic_manager_activate():
    user = User.query.get(session['user_id'])
    if user.role == 'doctor':
        flash('Your account is already a doctor profile. Please use the doctor dashboard.', 'warning')
        return redirect(url_for('doctor_dashboard'))
    if user.role != 'clinic_manager':
        user.role = 'clinic_manager'
        user.is_active = False
        db.session.commit()
        session.clear()
        flash('Clinic manager request submitted. Please wait for admin approval.', 'info')
        return redirect(url_for('login'))
    return redirect(url_for('clinic_manager_dashboard'))


@app.route('/clinic/manager/add/<int:doctor_id>', methods=['POST'])
@clinic_manager_required
def clinic_manager_add_doctor(doctor_id):
    user = User.query.get(session['user_id'])
    doctor = Doctor.query.get_or_404(doctor_id)
    clinic_account = ClinicAccount.query.filter_by(manager_user_id=user.id).first()
    if clinic_account:
        current_count = ClinicManagerDoctor.query.filter_by(manager_user_id=user.id).count()
        if current_count >= clinic_account.max_doctors:
            flash('Clinic plan limit reached. Please upgrade to add more doctors.', 'warning')
            return redirect(url_for('clinic_manager_dashboard'))
    existing = ClinicManagerDoctor.query.filter_by(manager_user_id=user.id, doctor_id=doctor.id).first()
    if existing:
        flash('This doctor is already managed by your account.', 'info')
        return redirect(url_for('clinic_manager_dashboard'))
    link = ClinicManagerDoctor(manager_user_id=user.id, doctor_id=doctor.id)
    db.session.add(link)
    db.session.commit()
    flash(f'You are now managing {doctor.name}.', 'success')
    return redirect(url_for('clinic_manager_dashboard'))


@app.route('/clinic/manager/remove/<int:link_id>', methods=['POST'])
@clinic_manager_required
def clinic_manager_remove_doctor(link_id):
    user = User.query.get(session['user_id'])
    link = ClinicManagerDoctor.query.filter_by(id=link_id, manager_user_id=user.id).first_or_404()
    doctor_name = link.doctor.name if link.doctor else 'this doctor'
    db.session.delete(link)
    db.session.commit()
    flash(f'Stopped managing {doctor_name}.', 'info')
    return redirect(url_for('clinic_manager_dashboard'))


@app.route('/clinic/manager/analytics/<int:doctor_id>')
@clinic_manager_required
def clinic_manager_analytics(doctor_id):
    user = User.query.get(session['user_id'])
    link = ClinicManagerDoctor.query.filter_by(manager_user_id=user.id, doctor_id=doctor_id).first()
    if not link:
        flash('You do not have access to this doctor profile.', 'danger')
        return redirect(url_for('clinic_manager_dashboard'))
    doctor = Doctor.query.get_or_404(doctor_id)
    analytics_context = build_doctor_analytics_context(doctor)
    return render_template('doctor_analytics.html',
                         doctor=doctor,
                         viewer_role='clinic_manager',
                         **analytics_context)


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

    # If user is an approved doctor, redirect to doctor dashboard
    if user.role == 'doctor':
        return redirect(url_for('doctor_dashboard'))

    # Check if user has pending verification request
    pending_verification = VerificationRequest.query.filter_by(
        user_id=user_id,
        status='pending'
    ).first()

    # If user has pending verification, show verification confirmation page
    if pending_verification:
        return redirect(url_for('verification_submitted'))

    # Get user's appointments
    appointments = Appointment.query.filter_by(user_id=user_id).order_by(Appointment.created_at.desc()).all()

    # Get user's ratings
    ratings = Rating.query.filter_by(user_id=user_id).order_by(Rating.created_at.desc()).all()

    # Latest verification request for status display (for approved/rejected doctors)
    verification_request = VerificationRequest.query.filter_by(
        user_id=user_id
    ).order_by(VerificationRequest.created_at.desc()).first()

    # Get user's badges
    user_badges = UserBadge.query.filter_by(user_id=user_id)\
        .join(BadgeDefinition)\
        .order_by(BadgeDefinition.display_order).all()

    # Calculate gamification stats
    total_helpful_received = user.helpful_count
    total_points = user.points
    tier = user.tier
    tier_name = user.tier_name

    return render_template('user_profile.html',
                         user=user,
                         appointments=appointments,
                         ratings=ratings,
                         verification_request=verification_request,
                         user_badges=user_badges,
                         total_helpful_received=total_helpful_received,
                         total_points=total_points,
                         tier=tier,
                         tier_name=tier_name)

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


@app.route('/admin/debug/r2-config')
@login_required
@admin_required
def debug_r2_config():
    """Debug route to check R2 configuration (admin only)"""
    import os

    def mask_value(value, show_chars=4):
        """Mask sensitive values but show length and special chars"""
        if not value:
            return "[NOT SET]"

        # Show repr to see special characters like \n
        repr_str = repr(value)

        # Check for special characters
        has_newline = '\\n' in repr_str
        has_space = ' ' in value
        has_tab = '\\t' in repr_str

        # Mask middle characters
        if len(value) > show_chars * 2:
            masked = value[:show_chars] + '...' + value[-show_chars:]
        else:
            masked = value[:show_chars] + '...'

        warnings = []
        if has_newline:
            warnings.append("⚠️ NEWLINE")
        if has_space:
            warnings.append("⚠️ SPACE")
        if has_tab:
            warnings.append("⚠️ TAB")

        warning_str = ' '.join(warnings) if warnings else "✓"

        return f"{masked} [len={len(value)}] {warning_str}"

    # Read R2 config
    r2_config = {
        'R2_ACCESS_KEY_ID': os.getenv('R2_ACCESS_KEY_ID', ''),
        'R2_SECRET_ACCESS_KEY': os.getenv('R2_SECRET_ACCESS_KEY', ''),
        'R2_ENDPOINT_URL': os.getenv('R2_ENDPOINT_URL', ''),
        'R2_BUCKET_NAME': os.getenv('R2_BUCKET_NAME', 'ranksewa-documents')
    }

    # After stripping
    r2_config_stripped = {
        'R2_ACCESS_KEY_ID': r2_config['R2_ACCESS_KEY_ID'].strip(),
        'R2_SECRET_ACCESS_KEY': r2_config['R2_SECRET_ACCESS_KEY'].strip(),
        'R2_ENDPOINT_URL': r2_config['R2_ENDPOINT_URL'].strip(),
        'R2_BUCKET_NAME': r2_config['R2_BUCKET_NAME'].strip()
    }

    # Build debug info
    debug_info = []
    debug_info.append("=== R2 Configuration Debug ===\n")

    for key in ['R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_ENDPOINT_URL', 'R2_BUCKET_NAME']:
        raw = r2_config[key]
        stripped = r2_config_stripped[key]

        debug_info.append(f"\n{key}:")
        debug_info.append(f"  Raw: {mask_value(raw)}")
        if raw != stripped:
            debug_info.append(f"  ⚠️ After strip: {mask_value(stripped)}")
        else:
            debug_info.append(f"  ✓ No whitespace issues")

    # Test R2 connection
    debug_info.append("\n\n=== R2 Connection Test ===")
    try:
        from r2_storage import R2Storage
        if all([r2_config_stripped['R2_ACCESS_KEY_ID'],
                r2_config_stripped['R2_SECRET_ACCESS_KEY'],
                r2_config_stripped['R2_ENDPOINT_URL']]):
            r2 = R2Storage(
                r2_config_stripped['R2_ACCESS_KEY_ID'],
                r2_config_stripped['R2_SECRET_ACCESS_KEY'],
                r2_config_stripped['R2_ENDPOINT_URL'],
                r2_config_stripped['R2_BUCKET_NAME']
            )
            debug_info.append("✓ R2Storage initialized successfully")
        else:
            debug_info.append("❌ Missing required credentials")
    except Exception as e:
        debug_info.append(f"❌ Error: {str(e)}")

    return '<pre>' + '\n'.join(debug_info) + '</pre>'


@app.route('/doctor/debug/my-photo')
@login_required
@doctor_required
def debug_my_photo():
    """Debug route to check doctor's photo status"""
    user = User.query.get(session['user_id'])
    doctor = user.doctor_profile

    debug_info = []
    debug_info.append("=== Doctor Photo Debug ===\n")
    debug_info.append(f"Doctor ID: {doctor.id}")
    debug_info.append(f"Doctor Name: {doctor.name}\n")

    # Check photo_url in database
    debug_info.append(f"Photo URL in DB: {doctor.photo_url or '[NOT SET]'}\n")

    if doctor.photo_url:
        # Check if it's an R2 path or local path
        if '/' in doctor.photo_url and doctor.photo_url.count('/') > 1:
            debug_info.append("Photo Type: R2 Storage")
            debug_info.append(f"R2 Path: {doctor.photo_url}")

            # Try to fetch from R2
            try:
                from r2_storage import get_verification_document
                photo_data = get_verification_document(doctor.photo_url)
                if photo_data:
                    debug_info.append(f"✓ Photo exists in R2 ({len(photo_data)} bytes)")
                else:
                    debug_info.append("✗ Photo NOT found in R2")
            except Exception as e:
                debug_info.append(f"✗ Error fetching from R2: {e}")
        else:
            debug_info.append("Photo Type: Local Storage")
            debug_info.append(f"Local Path: {doctor.photo_url}")

            # Check if file exists locally
            import os
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], doctor.photo_url)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                debug_info.append(f"✓ Photo exists locally ({size} bytes)")
            else:
                debug_info.append(f"✗ Photo NOT found locally at: {full_path}")

        # Show the URL that will be used
        filename = doctor.photo_url.split('/')[-1]
        url = url_for('serve_photo', filename=doctor.photo_url.split('/')[-1] if doctor.photo_url.count('/') == 1 else doctor.photo_url.replace('photos/', ''), _external=True)
        debug_info.append(f"\nPhoto URL: {url}")
        debug_info.append("\nTo test, try accessing the photo URL above in your browser.")
    else:
        debug_info.append("No photo uploaded yet.")
        debug_info.append("\nTo upload a photo:")
        debug_info.append("1. Go to Doctor Dashboard")
        debug_info.append("2. Click 'Edit Profile'")
        debug_info.append("3. Upload a photo")

    return '<pre>' + '\n'.join(debug_info) + '</pre>'


@app.route('/admin/debug/test-r2-upload')
@login_required
@admin_required
def test_r2_upload():
    """Test R2 upload with a small test file (admin only)"""
    import io
    from r2_storage import R2Storage

    results = []
    results.append("=== R2 Upload Test ===\n")

    # Get credentials
    access_key_id = os.getenv('R2_ACCESS_KEY_ID', '').strip()
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY', '').strip()
    endpoint_url = os.getenv('R2_ENDPOINT_URL', '').strip()
    bucket_name = os.getenv('R2_BUCKET_NAME', 'ranksewa-documents').strip()

    # Check credentials
    if not all([access_key_id, secret_access_key, endpoint_url]):
        results.append("❌ Missing R2 credentials")
        return '<pre>' + '\n'.join(results) + '</pre>'

    results.append(f"Bucket: {bucket_name}")
    results.append(f"Endpoint: {endpoint_url}")
    results.append(f"Access Key ID: {access_key_id[:8]}...{access_key_id[-4:]}\n")

    try:
        # Initialize R2
        results.append("Step 1: Initializing R2Storage...")
        r2 = R2Storage(access_key_id, secret_access_key, endpoint_url, bucket_name)
        results.append("✓ R2Storage initialized\n")

        # Create test file
        results.append("Step 2: Creating test file...")
        test_content = f"R2 Test Upload - {datetime.now().isoformat()}"
        test_file = io.BytesIO(test_content.encode('utf-8'))
        test_object_name = f"test/upload-test-{datetime.now().timestamp()}.txt"
        results.append("✓ Test file created\n")

        # Try upload
        results.append(f"Step 3: Uploading to '{test_object_name}'...")
        result = r2.upload_file(test_file, test_object_name, 'text/plain')

        if result:
            results.append(f"✓✓✓ UPLOAD SUCCESSFUL! ✓✓✓")
            results.append(f"Object name: {result}")
            results.append("\n🎉 R2 is working correctly!")

            # Try to verify file exists
            results.append("\nStep 4: Verifying file exists...")
            if r2.file_exists(result):
                results.append("✓ File verified in R2\n")

                # Try to read it back
                results.append("Step 5: Reading file back...")
                content = r2.get_file_object(result)
                if content:
                    results.append(f"✓ File content: {content.decode('utf-8')}\n")

                # Clean up test file
                results.append("Step 6: Cleaning up test file...")
                if r2.delete_file(result):
                    results.append("✓ Test file deleted")
            else:
                results.append("⚠️ Could not verify file (might still be uploading)")
        else:
            results.append("❌ UPLOAD FAILED")
            results.append("Check application logs for detailed error")

    except Exception as e:
        results.append(f"\n❌ ERROR: {type(e).__name__}")
        results.append(f"Message: {str(e)}")

        # Try to get more details
        if hasattr(e, 'response'):
            results.append(f"Response: {e.response}")

    return '<pre>' + '\n'.join(results) + '</pre>'


if __name__ == '__main__':
    # Fixed: Only enable debug mode if explicitly set, never in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    if is_production and debug_mode:
        print("ERROR: Debug mode cannot be enabled in production!")
        debug_mode = False
    app.run(debug=debug_mode)
