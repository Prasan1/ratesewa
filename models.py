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


class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False)
    experience = db.Column(db.Integer)
    education = db.Column(db.Text)
    college = db.Column(db.Text)
    description = db.Column(db.Text)
    photo_url = db.Column(db.Text)  # URL to doctor's photo
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    # Relationships (backrefs created in City, Specialty models)
    ratings = db.relationship('Rating', backref='doctor', lazy=True)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    contact_messages = db.relationship('ContactMessage', backref='doctor', lazy=True)

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

    # Relationships
    ratings = db.relationship('Rating', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    contact_messages = db.relationship('ContactMessage', backref='user', lazy=True)

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def user_name(self):
        """Get user name for the rating"""
        return self.user.name if self.user else 'Anonymous'

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
