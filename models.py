from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    doctors = db.relationship('Doctor', backref='city', lazy=True)

    def __repr__(self):
        return f'<City {self.name}>'


class Specialty(db.Model):
    __tablename__ = 'specialties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    doctors = db.relationship('Doctor', backref='specialty', lazy=True)

    def __repr__(self):
        return f'<Specialty {self.name}>'


class Clinic(db.Model):
    __tablename__ = 'clinics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    address = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    doctors = db.relationship('Doctor', backref='clinic', lazy=True)

    def __repr__(self):
        return f'<Clinic {self.name}>'


class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=True)
    experience = db.Column(db.Integer)
    education = db.Column(db.Text)  # Educational qualifications (e.g., "MBBS, MD")
    college = db.Column(db.Text)  # Where they studied (e.g., "Tribhuvan University")
    workplace = db.Column(db.Text)  # Where they work (e.g., "B&C Medical College")
    description = db.Column(db.Text)
    photo_url = db.Column(db.Text)  # URL to doctor's photo
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    # Verification and contact info
    nmc_number = db.Column(db.String(50), unique=True, nullable=True)  # Nepal Medical Council registration
    phone_number = db.Column(db.String(20), nullable=True)
    practice_address = db.Column(db.Text, nullable=True)
    external_clinic_url = db.Column(db.Text, nullable=True)  # External clinic profile URL (e.g., ClinicOne)

    # Analytics
    profile_views = db.Column(db.Integer, default=0)

    # Subscription and monetization
    subscription_tier = db.Column(db.String(20), default='free')  # 'free', 'premium', 'featured'
    subscription_expires_at = db.Column(db.DateTime, nullable=True)  # When paid subscription ends
    trial_ends_at = db.Column(db.DateTime, nullable=True)  # When free trial ends (for future premium trial)
    stripe_customer_id = db.Column(db.String(255), nullable=True)  # Stripe customer ID for subscription management

    # Relationships (backrefs created in City, Specialty models)
    ratings = db.relationship('Rating', backref='doctor', lazy=True)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    contact_messages = db.relationship('ContactMessage', backref='doctor', lazy=True)
    verification_requests = db.relationship('VerificationRequest', backref='doctor', lazy=True)
    review_responses = db.relationship('DoctorResponse', backref='doctor', lazy=True)
    clinic_managers = db.relationship('ClinicManagerDoctor', backref='doctor', lazy=True)

    @property
    def avg_rating(self):
        """Calculate average rating for the doctor"""
        if self.ratings:
            return sum(r.rating for r in self.ratings) / len(self.ratings)
        return 0.0

    @property
    def rating_count(self):
        """Get total number of ratings"""
        return len(self.ratings)

    def __repr__(self):
        return f'<Doctor {self.name}>'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # User role and doctor linkage
    role = db.Column(db.String(20), default='patient')  # 'patient', 'doctor', 'admin'
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)

    # Gamification
    points = db.Column(db.Integer, default=0)

    # Relationships
    ratings = db.relationship('Rating', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    contact_messages = db.relationship('ContactMessage', backref='user', lazy=True)
    doctor_profile = db.relationship('Doctor', foreign_keys=[doctor_id], backref='user_account', uselist=False)
    verification_requests = db.relationship('VerificationRequest', foreign_keys='VerificationRequest.user_id', backref='user', lazy=True)
    badges = db.relationship('UserBadge', backref='user', lazy=True)
    helpful_votes = db.relationship('ReviewHelpful', backref='user', lazy=True)
    managed_doctors = db.relationship('ClinicManagerDoctor', backref='manager', lazy=True, foreign_keys='ClinicManagerDoctor.manager_user_id')
    clinic_accounts = db.relationship('ClinicAccount', backref='manager', lazy=True, foreign_keys='ClinicAccount.manager_user_id')

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password, password)

    @property
    def tier(self):
        """Get user tier based on points"""
        if self.points >= 300:
            return 'platinum'
        elif self.points >= 151:
            return 'gold'
        elif self.points >= 51:
            return 'silver'
        else:
            return 'bronze'

    @property
    def tier_name(self):
        """Get display name for user tier"""
        tier_names = {
            'bronze': 'Basic Contributor',
            'silver': 'Trusted Reviewer',
            'gold': 'Expert Reviewer',
            'platinum': 'Community Leader'
        }
        return tier_names.get(self.tier, 'Basic Contributor')

    @property
    def review_count(self):
        """Get total number of reviews written"""
        return len(self.ratings)

    @property
    def helpful_count(self):
        """Get total number of helpful votes received on reviews"""
        count = 0
        for rating in self.ratings:
            count += len(rating.helpful_votes)
        return count

    def __repr__(self):
        return f'<User {self.email}>'


class ClinicManagerDoctor(db.Model):
    __tablename__ = 'clinic_manager_doctors'

    id = db.Column(db.Integer, primary_key=True)
    manager_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ClinicManagerDoctor manager={self.manager_user_id} doctor={self.doctor_id}>'


class ClinicAccount(db.Model):
    __tablename__ = 'clinic_accounts'

    id = db.Column(db.Integer, primary_key=True)
    manager_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    subscription_tier = db.Column(db.String(50), default='clinic_starter')
    max_doctors = db.Column(db.Integer, default=3)
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ClinicAccount manager={self.manager_user_id} tier={self.subscription_tier}>'


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    doctor_response = db.relationship('DoctorResponse', backref='rating', uselist=False, lazy=True)
    helpful_votes = db.relationship('ReviewHelpful', backref='rating', lazy=True)

    @property
    def user_name(self):
        """Get user name for the rating"""
        return self.user.name if self.user else 'Anonymous'

    @property
    def helpful_count(self):
        """Get number of helpful votes for this review"""
        return len(self.helpful_votes)

    def __repr__(self):
        return f'<Rating {self.rating} for Doctor ID {self.doctor_id}>'


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_date = db.Column(db.Date)
    appointment_time = db.Column(db.Time)
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    rating = db.relationship('Rating', backref='appointment', uselist=False, lazy=True)

    @property
    def is_ratable(self):
        """Check if this appointment can be rated"""
        return self.status == 'confirmed' and self.rating is None

    @property
    def is_rated(self):
        """Check if this appointment has been rated"""
        return self.rating is not None

    def __repr__(self):
        return f'<Appointment {self.id} - {self.status}>'


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactMessage {self.id} from {self.email}>'


class VerificationRequest(db.Model):
    __tablename__ = 'verification_requests'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)  # Nullable for new registrations
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Registration type
    is_new_doctor = db.Column(db.Boolean, default=False)  # True if self-registration, False if claiming existing

    # New doctor profile data (only for is_new_doctor=True)
    proposed_name = db.Column(db.String(200), nullable=True)
    proposed_specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=True)
    proposed_city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    proposed_education = db.Column(db.Text, nullable=True)
    proposed_college = db.Column(db.Text, nullable=True)
    proposed_experience = db.Column(db.Integer, nullable=True)

    # Contact verification
    nmc_number = db.Column(db.String(50))  # Nepal Medical Council registration
    phone_number = db.Column(db.String(20))
    phone_verified = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(200))
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255), nullable=True)

    # Document paths (stored in /instance/uploads/verification/{doctor_id}/)
    medical_degree_path = db.Column(db.String(500), nullable=True)
    govt_id_path = db.Column(db.String(500), nullable=True)
    practice_license_path = db.Column(db.String(500), nullable=True)

    # Practice information
    practice_address = db.Column(db.Text)
    practice_city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)

    # Admin review
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    admin_notes = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    practice_city = db.relationship('City', foreign_keys=[practice_city_id])
    proposed_specialty = db.relationship('Specialty', foreign_keys=[proposed_specialty_id])
    proposed_city = db.relationship('City', foreign_keys=[proposed_city_id])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

    def __repr__(self):
        return f'<VerificationRequest {self.id} - {self.status}>'


class DoctorResponse(db.Model):
    __tablename__ = 'doctor_responses'

    id = db.Column(db.Integer, primary_key=True)
    rating_id = db.Column(db.Integer, db.ForeignKey('ratings.id'), nullable=False, unique=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Doctor's user account
    response_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (backrefs created in Rating, Doctor, User models)
    response_user = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f'<DoctorResponse {self.id} for Rating {self.rating_id}>'


class Advertisement(db.Model):
    __tablename__ = 'advertisements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    ad_type = db.Column(db.String(50), nullable=False)  # 'banner', 'native', 'text', 'adsense'
    position = db.Column(db.String(100), nullable=False)  # 'homepage_sidebar', 'profile_top', etc.
    format = db.Column(db.String(50))  # '300x250', '728x90', etc.

    # Ad Content
    image_url = db.Column(db.String(500))
    link_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    html_content = db.Column(db.Text)

    # Targeting
    target_page = db.Column(db.String(100), default='all')  # 'all', 'homepage', 'profile', etc.
    target_specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=True)
    target_city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)

    # Scheduling
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Priority & Rotation
    priority = db.Column(db.Integer, default=0)  # Higher = more frequent display
    weight = db.Column(db.Integer, default=1)  # For weighted random selection

    # Performance Tracking
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)

    # Metadata
    advertiser_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships for targeting
    target_specialty = db.relationship('Specialty', foreign_keys=[target_specialty_id])
    target_city = db.relationship('City', foreign_keys=[target_city_id])

    @property
    def ctr(self):
        """Calculate Click-Through Rate"""
        if self.impressions > 0:
            return (self.clicks / self.impressions) * 100
        return 0.0

    def __repr__(self):
        return f'<Advertisement {self.name} - {self.position}>'


class ReviewFlag(db.Model):
    """
    Model for flagging inappropriate reviews
    NOT for removing negative reviews - only for content moderation
    """
    __tablename__ = 'review_flags'

    id = db.Column(db.Integer, primary_key=True)
    rating_id = db.Column(db.Integer, db.ForeignKey('ratings.id'), nullable=False)
    reporter_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null if anonymous

    # Flag details
    reason = db.Column(db.String(50), nullable=False)  # 'offensive', 'discriminatory', 'false', 'privacy', 'spam'
    additional_details = db.Column(db.Text, nullable=True)

    # Review status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'reviewed', 'approved', 'dismissed'
    admin_notes = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    rating = db.relationship('Rating', foreign_keys=[rating_id], backref='flags')
    reporter = db.relationship('User', foreign_keys=[reporter_user_id])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

    def __repr__(self):
        return f'<ReviewFlag {self.id} - Rating {self.rating_id} - {self.reason}>'


class BadgeDefinition(db.Model):
    """
    Defines available badges that users can earn
    """
    __tablename__ = 'badge_definitions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "First Review"
    slug = db.Column(db.String(100), unique=True, nullable=False)  # e.g., "first_review"
    description = db.Column(db.Text, nullable=False)  # How to earn the badge
    icon = db.Column(db.String(50))  # Emoji or icon class (e.g., "🌟", "fa-star")
    tier = db.Column(db.String(20), default='bronze')  # 'bronze', 'silver', 'gold', 'platinum'
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)  # For sorting badges
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user_badges = db.relationship('UserBadge', backref='badge_definition', lazy=True)

    def __repr__(self):
        return f'<BadgeDefinition {self.name}>'


class UserBadge(db.Model):
    """
    Tracks badges earned by users
    """
    __tablename__ = 'user_badges'
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge_definitions.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserBadge User {self.user_id} - Badge {self.badge_id}>'


class ReviewHelpful(db.Model):
    """
    Tracks which users found which reviews helpful
    Users can mark reviews as helpful (like upvoting)
    """
    __tablename__ = 'review_helpful'
    __table_args__ = (db.UniqueConstraint('rating_id', 'user_id', name='unique_helpful_vote'),)

    id = db.Column(db.Integer, primary_key=True)
    rating_id = db.Column(db.Integer, db.ForeignKey('ratings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ReviewHelpful Rating {self.rating_id} by User {self.user_id}>'


class ArticleCategory(db.Model):
    """
    Categories for health digest articles
    """
    __tablename__ = 'article_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Font Awesome icon class
    display_order = db.Column(db.Integer, default=0)

    # Relationship
    articles = db.relationship('Article', backref='category', lazy=True)

    def __repr__(self):
        return f'<ArticleCategory {self.name}>'


class Article(db.Model):
    """
    Health digest articles
    """
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('article_categories.id'), nullable=False)

    # Content
    summary = db.Column(db.Text)  # Short excerpt for listing page
    content = db.Column(db.Text, nullable=False)  # Full article content (HTML)
    featured_image = db.Column(db.String(500))  # URL to featured image

    # Author (can be admin or doctor in future)
    author_type = db.Column(db.String(20), default='admin')  # 'admin' or 'doctor'
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # If doctor
    author_name = db.Column(db.String(200), default='RankSewa Team')  # Display name

    # SEO
    meta_description = db.Column(db.String(160))  # For Google search results
    meta_keywords = db.Column(db.String(255))  # SEO keywords

    # Related specialty (to show related doctors)
    related_specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=True)

    # Status and analytics
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)  # Show on homepage
    view_count = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = db.relationship('User', foreign_keys=[author_id], backref='articles')
    related_specialty = db.relationship('Specialty', foreign_keys=[related_specialty_id])

    @property
    def read_time(self):
        """Calculate estimated read time in minutes"""
        if not self.content:
            return 1
        # Average reading speed: 200 words per minute
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes

    def __repr__(self):
        return f'<Article {self.title}>'


class DoctorAnalytics(db.Model):
    """Track detailed analytics for doctors"""
    __tablename__ = 'doctor_analytics'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    # Views
    profile_views = db.Column(db.Integer, default=0)
    search_appearances = db.Column(db.Integer, default=0)  # How many times shown in search
    search_clicks = db.Column(db.Integer, default=0)  # How many times clicked from search

    # Engagement
    phone_clicks = db.Column(db.Integer, default=0)  # "Call Now" button clicks
    website_clicks = db.Column(db.Integer, default=0)
    review_button_clicks = db.Column(db.Integer, default=0)

    # Sources
    source_search = db.Column(db.Integer, default=0)  # From search page
    source_homepage = db.Column(db.Integer, default=0)  # From homepage featured
    source_google = db.Column(db.Integer, default=0)  # From Google search
    source_direct = db.Column(db.Integer, default=0)  # Direct link

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    doctor = db.relationship('Doctor', backref='analytics')

    # Unique constraint: one row per doctor per day
    __table_args__ = (db.UniqueConstraint('doctor_id', 'date', name='_doctor_date_uc'),)

    def __repr__(self):
        return f'<DoctorAnalytics doctor_id={self.doctor_id} date={self.date}>'
