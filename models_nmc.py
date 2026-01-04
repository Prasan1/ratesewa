"""
NMC Verification Database Models

This is separate from the main Doctor model.
NMC data is used ONLY for verification, not public display.
"""

from models import db


class NMCDoctor(db.Model):
    """
    NMC registered doctors database.

    Used for:
    - Verifying doctor credentials during profile claim
    - Preventing fake doctor registrations
    - Auto-filling verified information

    NOT used for:
    - Public doctor listings
    - Search results
    - Patient-facing features
    """
    __tablename__ = 'nmc_doctors'

    nmc_number = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)  # Free text, not normalized
    gender = db.Column(db.String(10))
    degree = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<NMCDoctor {self.nmc_number}: {self.full_name}>'

    @property
    def is_claimed(self):
        """Check if this NMC number has been claimed by a verified doctor"""
        from models import Doctor
        return Doctor.query.filter_by(nmc_number=str(self.nmc_number), is_verified=True).first() is not None
