from extensions import db


class JobApplication(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    company_name = db.Column(db.String(100), nullable=False)

    job_role = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(100))

    application_date = db.Column(db.Date)

    status = db.Column(db.String(50), default='Applied')

    job_url = db.Column(db.String(300))

    notes = db.Column(db.Text)

    interviews = db.relationship(
    'Interview',
    backref='application',
    cascade='all, delete-orphan'
    )

class Interview(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey('job_application.id'),
        nullable=False
    )

    interview_date = db.Column(db.Date, nullable=False)

    interview_time = db.Column(db.Time)

    status = db.Column(
        db.String(50),
        default='Scheduled'
    )

    notes = db.Column(db.Text)