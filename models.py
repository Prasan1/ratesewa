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


# ============================================================
# NEPAL ADMINISTRATIVE DIVISIONS (Official 753 Local Levels)
# ============================================================

class Province(db.Model):
    """Nepal's 7 Provinces"""
    __tablename__ = 'provinces'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    nepali_name = db.Column(db.String(100))

    districts = db.relationship('District', backref='province', lazy=True)

    def __repr__(self):
        return f'<Province {self.name}>'


class District(db.Model):
    """Nepal's 77 Districts"""
    __tablename__ = 'districts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nepali_name = db.Column(db.String(100))
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), nullable=False)

    local_levels = db.relationship('LocalLevel', backref='district', lazy=True)

    def __repr__(self):
        return f'<District {self.name}>'


class LocalLevel(db.Model):
    """Nepal's 753 Local Levels (Palika) - Metropolitan, Sub-Metropolitan, Municipality, Rural Municipality"""
    __tablename__ = 'local_levels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    nepali_name = db.Column(db.String(150))
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)
    level_type = db.Column(db.String(50))  # Metropolitan, Sub-Metropolitan, Municipality, Rural Municipality

    # Link to old city for migration
    old_city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)

    def __repr__(self):
        return f'<LocalLevel {self.name} ({self.level_type})>'


class LocationAlias(db.Model):
    """Aliases for location names (K.M.C -> Kathmandu, etc.)"""
    __tablename__ = 'location_aliases'

    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(200), nullable=False, index=True)
    local_level_id = db.Column(db.Integer, db.ForeignKey('local_levels.id'), nullable=False)
    alias_type = db.Column(db.String(50))  # 'abbreviation', 'full_name', 'nepali', 'district_name', 'common_variant'

    local_level = db.relationship('LocalLevel', backref='aliases')

    def __repr__(self):
        return f'<LocationAlias {self.alias} -> {self.local_level_id}>'


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
    """Medical clinic/hospital that can have multiple doctors"""
    __tablename__ = 'clinics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)  # For legacy compatibility
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)  # City name for new portal clinics
    phone_number = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=True)  # Alias for phone_number
    email = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)

    # Clinic type and status
    clinic_type = db.Column(db.String(50), default='clinic')  # hospital, clinic, nursing_home, private_practice, polyclinic
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)  # Admin verified

    # Management (for clinic portal)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doctors = db.relationship('Doctor', backref='clinic', lazy=True)
    created_by = db.relationship('User', foreign_keys=[created_by_user_id], backref=db.backref('created_clinics', lazy=True))

    def __repr__(self):
        return f'<Clinic {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'address': self.address,
            'city': self.city,
            'phone': self.phone or self.phone_number,
            'email': self.email,
            'clinic_type': self.clinic_type,
            'description': self.description,
            'logo_url': self.logo_url,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_active_doctors(self):
        """Get all approved and active doctors at this clinic"""
        return ClinicDoctor.query.filter_by(
            clinic_id=self.id,
            status='approved',
            is_active=True
        ).all()


class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    local_level_id = db.Column(db.Integer, db.ForeignKey('local_levels.id'), nullable=True)
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
    specialty_verified = db.Column(db.Boolean, default=False)  # True if specialty confirmed by admin
    ranksewa_network_enabled = db.Column(db.Boolean, default=False)  # Allow patients to add to their network

    # Verification and contact info
    nmc_number = db.Column(db.String(50), unique=True, nullable=True)  # Nepal Medical Council registration
    nmc_expiry_date = db.Column(db.Date, nullable=True)  # NULL = permanent license, otherwise expiry date
    phone_number = db.Column(db.String(20), nullable=True)
    practice_address = db.Column(db.Text, nullable=True)
    external_clinic_url = db.Column(db.Text, nullable=True)  # External clinic profile URL (e.g., ClinicOne)
    working_hours = db.Column(db.Text, nullable=True)  # JSON string: {"monday": "9:00-17:00", "tuesday": "9:00-17:00", ...}
    accepted_insurance = db.Column(db.Text, nullable=True)  # Comma-separated list of accepted insurance providers

    # Analytics
    profile_views = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

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

    # Location relationship (new proper Nepal location system)
    local_level = db.relationship('LocalLevel', backref='doctors', lazy='select', foreign_keys=[local_level_id])

    # Normalized data relationships
    # Using lazy='select' for backward compatibility - tables may not exist yet in production
    contact = db.relationship('DoctorContact', backref='doctor', uselist=False, lazy='select')
    subscription = db.relationship('DoctorSubscription', backref='doctor', uselist=False, lazy='select')
    credentials = db.relationship('DoctorCredentials', backref='doctor', uselist=False, lazy='select')
    settings = db.relationship('DoctorSettings', backref='doctor', uselist=False, lazy='select')
    medical_tools = db.relationship('DoctorMedicalTools', backref='doctor', uselist=False, lazy='select')

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
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # User role and doctor linkage
    role = db.Column(db.String(20), default='patient')  # 'patient', 'doctor', 'admin'
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    is_doctor_intent = db.Column(db.Boolean, default=False)  # True if user checked "I am a doctor" during registration

    # Gamification
    points = db.Column(db.Integer, default=0)

    # Activity tracking
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_verification_sent_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    ratings = db.relationship('Rating', backref='user', lazy=True)
    appointments = db.relationship('Appointment', foreign_keys='Appointment.user_id', backref='user', lazy=True)
    contact_messages = db.relationship('ContactMessage', backref='user', lazy=True)
    doctor_profile = db.relationship('Doctor', foreign_keys=[doctor_id], backref=db.backref('user_account', uselist=False), uselist=False)
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


class BlockedIdentity(db.Model):
    __tablename__ = 'blocked_identities'

    id = db.Column(db.Integer, primary_key=True)
    block_type = db.Column(db.String(20), nullable=False)  # 'email', 'domain', 'ip'
    value = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<BlockedIdentity {self.block_type}:{self.value}>'


class SecurityEvent(db.Model):
    __tablename__ = 'security_events'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    ip = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    path = db.Column(db.String(255), nullable=True)
    method = db.Column(db.String(10), nullable=True)
    meta = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f'<SecurityEvent {self.event_type} {self.created_at}>'

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
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    suspicion_score = db.Column(db.Integer, default=0)
    is_suspected = db.Column(db.Boolean, default=False)
    credibility_score = db.Column(db.Integer, default=0)  # Community-based credibility (0-100+)

    # Visit experience details (new fields for better patient insights)
    visit_time = db.Column(db.String(20), nullable=True)  # Morning/Afternoon/Evening
    had_appointment = db.Column(db.Boolean, default=False)  # Did they have an appointment?
    wait_time_minutes = db.Column(db.Integer, nullable=True)  # How long they waited
    doctor_on_time = db.Column(db.Boolean, nullable=True)  # Was doctor on time? (for appointments)
    visit_type = db.Column(db.String(20), nullable=True)  # first/follow_up/emergency
    visit_reason = db.Column(db.String(255), nullable=True)
    recommendation = db.Column(db.String(5), nullable=True)  # yes/no
    value_rating = db.Column(db.Integer, nullable=True)
    bedside_rating = db.Column(db.Integer, nullable=True)
    cleanliness_rating = db.Column(db.Integer, nullable=True)

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
    """Patient appointment booking - supports both direct and clinic-based bookings"""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)

    # Legacy fields (for direct doctor bookings)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    message = db.Column(db.Text)  # Legacy message field

    # Clinic booking fields
    clinic_doctor_id = db.Column(db.Integer, db.ForeignKey('clinic_doctors.id'), nullable=True)

    # Appointment timing
    appointment_date = db.Column(db.Date, nullable=True)
    appointment_time = db.Column(db.Time, nullable=True)

    # Patient info (can be guest or registered user)
    patient_name = db.Column(db.String(200), nullable=True)
    patient_phone = db.Column(db.String(20), nullable=True)
    patient_email = db.Column(db.String(120))
    patient_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # If registered user

    # Booking details
    reason = db.Column(db.Text)  # Chief complaint / reason for visit
    booking_code = db.Column(db.String(10), unique=True, nullable=True)  # For patient to check status

    # Status tracking
    status = db.Column(db.String(50), default='pending')  # pending, booked, confirmed, checked_in, in_progress, completed, no_show, cancelled
    queue_position = db.Column(db.Integer)  # Position in queue for the day

    # Staff notes
    notes = db.Column(db.Text)  # Internal notes by clinic staff

    # Confirmation tracking
    confirmation_sent_at = db.Column(db.DateTime)
    confirmed_at = db.Column(db.DateTime)
    checked_in_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.String(500))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rating = db.relationship('Rating', backref='appointment', uselist=False, lazy=True)
    clinic_doctor = db.relationship('ClinicDoctor', backref=db.backref('appointments', lazy=True))
    patient_user = db.relationship('User', foreign_keys=[patient_user_id], backref=db.backref('patient_appointments', lazy=True))

    # Index for common queries
    __table_args__ = (
        db.Index('idx_appointment_date_doctor', 'clinic_doctor_id', 'appointment_date'),
        db.Index('idx_appointment_booking_code', 'booking_code'),
        db.Index('idx_appointment_patient_phone', 'patient_phone'),
    )

    @property
    def is_ratable(self):
        """Check if this appointment can be rated"""
        return self.status in ['confirmed', 'completed'] and self.rating is None

    @property
    def is_rated(self):
        """Check if this appointment has been rated"""
        return self.rating is not None

    def __repr__(self):
        return f'<Appointment {self.booking_code or self.id} {self.status}>'

    def to_dict(self, include_patient_details=False):
        result = {
            'id': self.id,
            'booking_code': self.booking_code,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'status': self.status,
            'queue_position': self.queue_position,
            'clinic_name': self.clinic_doctor.clinic.name if self.clinic_doctor else None,
            'doctor_name': self.clinic_doctor.doctor.name if self.clinic_doctor else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_patient_details:
            result.update({
                'patient_name': self.patient_name,
                'patient_phone': self.patient_phone,
                'patient_email': self.patient_email,
                'reason': self.reason,
                'notes': self.notes
            })

        return result

    @staticmethod
    def generate_booking_code():
        """Generate unique 8-character booking code"""
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            # Exclude confusing characters
            code = code.replace('O', 'X').replace('0', 'Y').replace('I', 'Z').replace('1', 'W')
            if not Appointment.query.filter_by(booking_code=code).first():
                return code

    def get_status_display(self):
        """Human-readable status"""
        status_map = {
            'pending': 'Pending',
            'booked': 'Booked',
            'confirmed': 'Confirmed',
            'checked_in': 'Checked In',
            'in_progress': 'With Doctor',
            'completed': 'Completed',
            'no_show': 'No Show',
            'cancelled': 'Cancelled'
        }
        return status_map.get(self.status, self.status)

    def can_cancel(self):
        """Check if appointment can still be cancelled"""
        if self.status in ['completed', 'no_show', 'cancelled']:
            return False

        if not self.clinic_doctor:
            return True  # Legacy appointments can always be cancelled

        from datetime import datetime, timedelta
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        notice_hours = self.clinic_doctor.cancellation_notice_hours or 24

        return datetime.now() < appointment_datetime - timedelta(hours=notice_hours)


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
    quick_answer = db.Column(db.Text)  # Quick answer box (reduces bounce rate)

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


# ============================================================================
# NORMALIZED DOCTOR TABLES
# ============================================================================

class DoctorContact(db.Model):
    """Contact and location information for doctors"""
    __tablename__ = 'doctor_contact'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, unique=True)
    phone_number = db.Column(db.String(20))
    practice_address = db.Column(db.Text)
    workplace = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DoctorContact doctor_id={self.doctor_id}>'


class DoctorWorkplace(db.Model):
    """Structured workplace/practice locations for doctors"""
    __tablename__ = 'doctor_workplaces'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, index=True)

    # Workplace details
    name = db.Column(db.String(200), nullable=False)  # Clinic/Hospital name
    address = db.Column(db.String(300), nullable=True)  # Street address
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)  # Link to cities table
    city_name = db.Column(db.String(100), nullable=True)  # Fallback if city not in list
    phone = db.Column(db.String(20), nullable=True)

    # Display order (1 = primary workplace)
    display_order = db.Column(db.Integer, default=1)
    is_primary = db.Column(db.Boolean, default=False)

    # Optional link to registered clinic
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doctor = db.relationship('Doctor', backref=db.backref('workplaces', lazy='select', order_by='DoctorWorkplace.display_order'))
    city = db.relationship('City', backref=db.backref('doctor_workplaces', lazy=True))
    clinic = db.relationship('Clinic', backref=db.backref('workplace_listings', lazy=True))

    def __repr__(self):
        return f'<DoctorWorkplace {self.name} for doctor_id={self.doctor_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city.name if self.city else self.city_name,
            'city_id': self.city_id,
            'phone': self.phone,
            'display_order': self.display_order,
            'is_primary': self.is_primary
        }

    @property
    def full_address(self):
        """Get full formatted address"""
        parts = [self.name]
        if self.address:
            parts.append(self.address)
        city = self.city.name if self.city else self.city_name
        if city:
            parts.append(city)
        return ', '.join(parts)


class DoctorSubscription(db.Model):
    """Subscription and billing information for doctors"""
    __tablename__ = 'doctor_subscription'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, unique=True)
    subscription_tier = db.Column(db.String(20), default='free')
    subscription_expires_at = db.Column(db.DateTime)
    trial_ends_at = db.Column(db.DateTime)
    stripe_customer_id = db.Column(db.String(255))
    profile_views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DoctorSubscription doctor_id={self.doctor_id} tier={self.subscription_tier}>'


class DoctorCredentials(db.Model):
    """Professional credentials for doctors"""
    __tablename__ = 'doctor_credentials'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, unique=True)
    nmc_number = db.Column(db.String(50))
    external_clinic_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DoctorCredentials doctor_id={self.doctor_id}>'


class DoctorSettings(db.Model):
    """Settings and preferences for doctors"""
    __tablename__ = 'doctor_settings'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, unique=True)
    photo_url = db.Column(db.Text)
    working_hours = db.Column(db.Text)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DoctorSettings doctor_id={self.doctor_id}>'


class DoctorMedicalTools(db.Model):
    """Medical tools configuration (certificates, prescriptions)"""
    __tablename__ = 'doctor_medical_tools'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, unique=True)

    # Signature & Branding
    signature_image = db.Column(db.Text)
    clinic_letterhead = db.Column(db.Text)

    # Default Values
    default_clinic_name = db.Column(db.String(255))
    default_clinic_address = db.Column(db.Text)
    default_consultation_fee = db.Column(db.Integer)

    # Preferences (JSON)
    certificate_settings = db.Column(db.Text)
    prescription_settings = db.Column(db.Text)

    # Access Control
    tools_enabled = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DoctorMedicalTools doctor_id={self.doctor_id}>'


class DoctorTemplateUsage(db.Model):
    """Analytics for medical template usage"""
    __tablename__ = 'doctor_template_usage'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    template_type = db.Column(db.String(50))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient_name = db.Column(db.String(100))

    def __repr__(self):
        return f'<DoctorTemplateUsage doctor_id={self.doctor_id} type={self.template_type}>'


# =============================================================================
# PATIENT HEALTH TRACKING MODELS
# =============================================================================

class BPRecord(db.Model):
    """Blood pressure readings for patient health tracking"""
    __tablename__ = 'bp_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    systolic = db.Column(db.Integer, nullable=False)  # Top number (mmHg)
    diastolic = db.Column(db.Integer, nullable=False)  # Bottom number (mmHg)
    pulse = db.Column(db.Integer, nullable=True)  # Heart rate (bpm)
    notes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('bp_records', lazy=True))

    def __repr__(self):
        return f'<BPRecord {self.systolic}/{self.diastolic} for user {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'systolic': self.systolic,
            'diastolic': self.diastolic,
            'pulse': self.pulse,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SugarRecord(db.Model):
    """Blood sugar readings for patient health tracking"""
    __tablename__ = 'sugar_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # mg/dL
    notes = db.Column(db.Text, nullable=True)  # Fasting, After meal, etc.
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('sugar_records', lazy=True))

    def __repr__(self):
        return f'<SugarRecord {self.value} mg/dL for user {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Medication(db.Model):
    """Medications tracked by patients"""
    __tablename__ = 'medications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)  # e.g., "500mg"
    frequency = db.Column(db.String(100), nullable=False)  # e.g., "Twice daily"
    instructions = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('medications', lazy=True))

    def __repr__(self):
        return f'<Medication {self.name} for user {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'instructions': self.instructions,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class HealthConsent(db.Model):
    """Tracks user consent for health tracking feature"""
    __tablename__ = 'health_consents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    terms_version = db.Column(db.String(20), nullable=False)  # e.g., "1.0"
    accepted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=True)

    user = db.relationship('User', backref=db.backref('health_consent', uselist=False))

    def __repr__(self):
        return f'<HealthConsent user={self.user_id} v{self.terms_version}>'


class PatientDoctor(db.Model):
    """Links patients to their doctors for health data sharing"""
    __tablename__ = 'patient_doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)  # e.g., "Primary care", "Cardiologist"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('my_doctors', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('patients', lazy=True))

    # Ensure unique patient-doctor pairs
    __table_args__ = (
        db.UniqueConstraint('user_id', 'doctor_id', name='unique_patient_doctor'),
    )

    def __repr__(self):
        return f'<PatientDoctor user={self.user_id} doctor={self.doctor_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'doctor_specialty': self.doctor.specialty.name if self.doctor and self.doctor.specialty else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =============================================================================
# CLINIC & APPOINTMENT SYSTEM
# =============================================================================

class ClinicStaff(db.Model):
    """Staff members who can manage a clinic (admin, receptionist, etc.)"""
    __tablename__ = 'clinic_staff'

    id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    role = db.Column(db.String(50), default='staff')  # admin, staff, receptionist
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    clinic = db.relationship('Clinic', backref=db.backref('staff', lazy=True))
    user = db.relationship('User', backref=db.backref('clinic_roles', lazy=True))

    # Ensure unique user per clinic
    __table_args__ = (
        db.UniqueConstraint('clinic_id', 'user_id', name='unique_clinic_staff'),
    )

    def __repr__(self):
        return f'<ClinicStaff clinic={self.clinic_id} user={self.user_id} role={self.role}>'


class ClinicDoctor(db.Model):
    """Links verified doctors to clinics - requires doctor approval"""
    __tablename__ = 'clinic_doctors'

    id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)

    # Role at clinic
    role = db.Column(db.String(50), default='consultant')  # owner, consultant, visiting, resident

    # Clinic-specific details (may differ from main profile)
    consultation_fee = db.Column(db.Integer)  # Fee at THIS clinic (NPR)

    # Approval workflow
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    invited_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responded_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.String(500))

    # Appointment settings for this doctor at this clinic
    slot_duration_minutes = db.Column(db.Integer, default=15)
    max_patients_per_slot = db.Column(db.Integer, default=1)
    accepts_online_booking = db.Column(db.Boolean, default=True)
    booking_notice_hours = db.Column(db.Integer, default=2)  # Min hours before appointment
    cancellation_notice_hours = db.Column(db.Integer, default=24)  # Min hours to cancel

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    clinic = db.relationship('Clinic', backref=db.backref('clinic_doctors', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('clinic_affiliations', lazy=True))
    invited_by = db.relationship('User', backref=db.backref('doctor_invitations', lazy=True))

    # Ensure unique doctor per clinic
    __table_args__ = (
        db.UniqueConstraint('clinic_id', 'doctor_id', name='unique_clinic_doctor'),
    )

    def __repr__(self):
        return f'<ClinicDoctor clinic={self.clinic_id} doctor={self.doctor_id} status={self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'clinic_id': self.clinic_id,
            'clinic_name': self.clinic.name if self.clinic else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'role': self.role,
            'consultation_fee': self.consultation_fee,
            'status': self.status,
            'slot_duration_minutes': self.slot_duration_minutes,
            'accepts_online_booking': self.accepts_online_booking,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_schedules(self):
        """Get all active schedules for this doctor at this clinic"""
        return ClinicSchedule.query.filter_by(
            clinic_doctor_id=self.id,
            is_active=True
        ).order_by(ClinicSchedule.day_of_week).all()


class ClinicSchedule(db.Model):
    """Weekly schedule for a doctor at a specific clinic"""
    __tablename__ = 'clinic_schedules'

    id = db.Column(db.Integer, primary_key=True)
    clinic_doctor_id = db.Column(db.Integer, db.ForeignKey('clinic_doctors.id'), nullable=False)

    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Sunday, 1=Monday, ..., 6=Saturday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Capacity
    max_appointments = db.Column(db.Integer, default=20)

    # Overrides
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    clinic_doctor = db.relationship('ClinicDoctor', backref=db.backref('schedules', lazy=True))

    def __repr__(self):
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        return f'<ClinicSchedule {days[self.day_of_week]} {self.start_time}-{self.end_time}>'

    def to_dict(self):
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        return {
            'id': self.id,
            'clinic_doctor_id': self.clinic_doctor_id,
            'day_of_week': self.day_of_week,
            'day_name': days[self.day_of_week],
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'max_appointments': self.max_appointments,
            'is_active': self.is_active
        }

    def get_time_slots(self, slot_duration_minutes=15):
        """Generate available time slots for this schedule"""
        from datetime import datetime, timedelta
        slots = []
        current = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)

        while current < end:
            slots.append(current.time())
            current += timedelta(minutes=slot_duration_minutes)

        return slots


class ScheduleException(db.Model):
    """Exceptions to regular schedule (holidays, special hours, blocked days)"""
    __tablename__ = 'schedule_exceptions'

    id = db.Column(db.Integer, primary_key=True)
    clinic_doctor_id = db.Column(db.Integer, db.ForeignKey('clinic_doctors.id'), nullable=False)

    exception_date = db.Column(db.Date, nullable=False)
    exception_type = db.Column(db.String(20), nullable=False)  # closed, modified, special

    # For modified hours (if not fully closed)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    reason = db.Column(db.String(200))  # "Holiday", "Conference", "Personal leave"

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    clinic_doctor = db.relationship('ClinicDoctor', backref=db.backref('schedule_exceptions', lazy=True))

    def __repr__(self):
        return f'<ScheduleException {self.exception_date} {self.exception_type}>'


class AppointmentReminder(db.Model):
    """Track reminders sent for appointments"""
    __tablename__ = 'appointment_reminders'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)

    reminder_type = db.Column(db.String(20), nullable=False)  # email, sms, whatsapp
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='sent')  # sent, delivered, failed

    # For tracking responses (SMS confirmation)
    response_received = db.Column(db.Boolean, default=False)
    response_text = db.Column(db.String(200))
    response_at = db.Column(db.DateTime)

    # Relationships
    appointment = db.relationship('Appointment', backref=db.backref('reminders', lazy=True))

    def __repr__(self):
        return f'<AppointmentReminder {self.appointment_id} {self.reminder_type} {self.status}>'


class PatientNoShowRecord(db.Model):
    """Track patient no-show history for reliability scoring"""
    __tablename__ = 'patient_no_show_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_phone = db.Column(db.String(20), nullable=False, index=True)
    patient_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    no_show_date = db.Column(db.Date, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointment = db.relationship('Appointment', backref=db.backref('no_show_record', uselist=False))
    patient_user = db.relationship('User', backref=db.backref('no_show_records', lazy=True))

    def __repr__(self):
        return f'<PatientNoShowRecord {self.patient_phone} {self.no_show_date}>'

    @staticmethod
    def get_no_show_count(patient_phone, months=6):
        """Get number of no-shows in the past N months"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now().date() - timedelta(days=months * 30)
        return PatientNoShowRecord.query.filter(
            PatientNoShowRecord.patient_phone == patient_phone,
            PatientNoShowRecord.no_show_date >= cutoff_date
        ).count()
