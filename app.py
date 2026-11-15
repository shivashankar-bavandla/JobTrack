from urllib.parse import urlparse
from sqlalchemy import or_, func
from flask import Flask, render_template, request, redirect, url_for, send_file
from io import BytesIO
from openpyxl import Workbook
from datetime import datetime
import os

from extensions import db

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))

database_folder = os.path.join(basedir, 'database')
os.makedirs(database_folder, exist_ok=True)

database_path = os.path.join(database_folder, 'jobtrack.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Import database models
from models import JobApplication, Interview


# Homepage / Dashboard
@app.route('/')
def home():

    applications = JobApplication.query.order_by(
        JobApplication.id.desc()
    ).all()

    total_applications = JobApplication.query.count()

    applied_count = JobApplication.query.filter_by(
        status='Applied'
    ).count()

    interview_count = JobApplication.query.filter_by(
        status='Interview'
    ).count()

    selected_count = JobApplication.query.filter_by(
        status='Selected'
    ).count()

    return render_template(
        'dashboard.html',
        applications=applications,
        total_applications=total_applications,
        applied_count=applied_count,
        interview_count=interview_count,
        selected_count=selected_count
    )


# Add application
@app.route('/add-application', methods=['GET', 'POST'])
def add_application():

    if request.method == 'POST':

        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        location = request.form.get('location', '').strip()
        application_date = request.form.get('application_date', '').strip()
        status = request.form.get('status', 'Applied').strip()
        job_url = request.form.get('job_url', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validate required fields
        if not company_name or not job_role or not application_date:
            return render_template(
                'add_application.html',
                error="Company name, job role and application date are required."
            )

        # Validate character limits
        if len(company_name) > 100 or len(job_role) > 100:
            return render_template(
                'add_application.html',
                error="Company name and job role must not exceed 100 characters."
            )

        # Validate application date
        try:
            application_date = datetime.strptime(
                application_date, '%Y-%m-%d'
            ).date()
        except ValueError:
            return render_template(
                'add_application.html',
                error="Please enter a valid application date."
            )

        # Validate application status
        if status not in ['Applied', 'Interview', 'Selected', 'Rejected']:
            return render_template(
                'add_application.html',
                error="Invalid application status."
            )

        # Validate job URL if provided
        if job_url:
            parsed_url = urlparse(job_url)

            if parsed_url.scheme not in ['http', 'https'] or not parsed_url.netloc:
                return render_template(
                    'add_application.html',
                    error="Please enter a valid job URL."
                )

        # Save application
        new_application = JobApplication(
            company_name=company_name,
            job_role=job_role,
            location=location,
            application_date=application_date,
            status=status,
            job_url=job_url,
            notes=notes
        )

        db.session.add(new_application)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add_application.html')

# View applications, search, filter and pagination
@app.route('/applications')
def applications():

    search = request.args.get('search', '').strip()
    selected_status = request.args.get('status', '').strip()

    page = request.args.get('page', 1, type=int)

    query = JobApplication.query

    # Search by company or job role
    if search:
        query = query.filter(
            or_(
                JobApplication.company_name.contains(search),
                JobApplication.job_role.contains(search)
            )
        )

    # Filter by status
    if selected_status:
        query = query.filter_by(status=selected_status)

    # Pagination: 5 records per page
    pagination = query.order_by(
        JobApplication.id.desc()
    ).paginate(
        page=page,
        per_page=5,
        error_out=False
    )

    return render_template(
        'applications.html',
        applications=pagination.items,
        pagination=pagination,
        search=search,
        selected_status=selected_status
    )

# Edit application
# Interview Tracker
# Interview Tracker - Search and Filter
@app.route('/interviews')
def interviews():
    from datetime import date

    search = request.args.get('search', '').strip()
    selected_status = request.args.get('status', '').strip()
    date_filter = request.args.get('date_filter', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Interview.query.join(JobApplication)

    # Search by company name or job role
    if search:
        query = query.filter(
            or_(
                JobApplication.company_name.ilike(f'%{search}%'),
                JobApplication.job_role.ilike(f'%{search}%')
            )
        )

    # Filter by interview status
    if selected_status:
        query = query.filter(Interview.status == selected_status)

    # Filter by upcoming or past interviews
    if date_filter == 'upcoming':
        query = query.filter(Interview.interview_date >= date.today())
    elif date_filter == 'past':
        query = query.filter(Interview.interview_date < date.today())

    # Pagination: display 5 interviews per page
    pagination = query.order_by(
        Interview.interview_date.asc()
    ).paginate(
        page=page,
        per_page=5,
        error_out=False
    )

    # Statistics
    total_interviews = Interview.query.count()

    upcoming_interviews = Interview.query.filter(
        Interview.interview_date >= date.today(),
        Interview.status == 'Scheduled'
    ).count()

    completed_interviews = Interview.query.filter_by(
        status='Completed'
    ).count()

    cancelled_interviews = Interview.query.filter_by(
        status='Cancelled'
    ).count()

    return render_template(
        'interviews.html',
        interviews=pagination.items,
        pagination=pagination,
        total_interviews=total_interviews,
        upcoming_interviews=upcoming_interviews,
        completed_interviews=completed_interviews,
        cancelled_interviews=cancelled_interviews,
        search=search,
        selected_status=selected_status,
        date_filter=date_filter
    )
# Add Interview
@app.route('/add-interview', methods=['GET', 'POST'])
def add_interview():

    applications = JobApplication.query.order_by(
        JobApplication.company_name.asc()
    ).all()

    if request.method == 'POST':

        application_id = request.form.get('application_id', '').strip()
        interview_date = request.form.get('interview_date', '').strip()
        interview_time = request.form.get('interview_time', '').strip()
        status = request.form.get('status', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validate company selection
        if not application_id:
            return render_template(
                'add_interview.html',
                applications=applications,
                error="Please select a company."
            )

        try:
            application_id = int(application_id)
        except ValueError:
            return render_template(
                'add_interview.html',
                applications=applications,
                error="Invalid company selection."
            )

        # Check whether the application exists
        selected_application = db.session.get(
            JobApplication, application_id
        )

        if selected_application is None:
            return render_template(
                'add_interview.html',
                applications=applications,
                error="Selected application does not exist."
            )

        # Validate interview date
        if not interview_date:
            return render_template(
                'add_interview.html',
                applications=applications,
                error="Interview date is required."
            )

        try:
            interview_date = datetime.strptime(
                interview_date, '%Y-%m-%d'
            ).date()
        except ValueError:
            return render_template(
                'add_interview.html',
                applications=applications,
                error="Please enter a valid interview date."
            )

        # Validate interview time
        if interview_time:
            try:
                interview_time = datetime.strptime(
                    interview_time, '%H:%M'
                ).time()
            except ValueError:
                return render_template(
                    'add_interview.html',
                    applications=applications,
                    error="Please enter a valid interview time."
                )
        else:
            interview_time = None

        # Validate interview status
        if status not in ['Scheduled', 'Completed', 'Cancelled']:
            return render_template(
                'add_interview.html',
                applications=applications,
                error="Invalid interview status."
            )

        # Save interview
        new_interview = Interview(
            application_id=application_id,
            interview_date=interview_date,
            interview_time=interview_time,
            status=status,
            notes=notes
        )

        db.session.add(new_interview)
        db.session.commit()

        return redirect(url_for('interviews'))

    return render_template(
        'add_interview.html',
        applications=applications
    )
# Edit Interview
@app.route('/edit-interview/<int:id>', methods=['GET', 'POST'])
def edit_interview(id):

    interview = db.get_or_404(Interview, id)

    if request.method == 'POST':

        interview_date = request.form.get('interview_date', '').strip()
        interview_time = request.form.get('interview_time', '').strip()
        status = request.form.get('status', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validate interview date
        if not interview_date:
            return render_template(
                'edit_interview.html',
                interview=interview,
                error="Interview date is required."
            )

        try:
            interview_date = datetime.strptime(
                interview_date, '%Y-%m-%d'
            ).date()
        except ValueError:
            return render_template(
                'edit_interview.html',
                interview=interview,
                error="Please enter a valid interview date."
            )

        # Validate interview time
        if interview_time:
            try:
                interview_time = datetime.strptime(
                    interview_time, '%H:%M'
                ).time()
            except ValueError:
                return render_template(
                    'edit_interview.html',
                    interview=interview,
                    error="Please enter a valid interview time."
                )
        else:
            interview_time = None

        # Validate status
        if status not in ['Scheduled', 'Completed', 'Cancelled']:
            return render_template(
                'edit_interview.html',
                interview=interview,
                error="Invalid interview status."
            )

        # Update interview
        interview.interview_date = interview_date
        interview.interview_time = interview_time
        interview.status = status
        interview.notes = notes

        db.session.commit()

        return redirect(url_for('interviews'))

    return render_template(
        'edit_interview.html',
        interview=interview
    )
# Delete Interview
@app.route('/delete-interview/<int:id>', methods=['POST'])
def delete_interview(id):

    interview = db.get_or_404(Interview, id)

    db.session.delete(interview)
    db.session.commit()

    return redirect(url_for('interviews'))
@app.route('/edit-application/<int:id>', methods=['GET', 'POST'])
def edit_application(id):

    application = db.get_or_404(JobApplication, id)

    if request.method == 'POST':

        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        location = request.form.get('location', '').strip()
        application_date = request.form.get('application_date', '').strip()
        status = request.form.get('status', 'Applied').strip()
        job_url = request.form.get('job_url', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validate required fields
        if not company_name or not job_role or not application_date:
            return render_template(
                'edit_application.html',
                application=application,
                error="Company name, job role and application date are required."
            )

        # Validate character limits
        if len(company_name) > 100 or len(job_role) > 100:
            return render_template(
                'edit_application.html',
                application=application,
                error="Company name and job role must not exceed 100 characters."
            )

        # Validate application date
        try:
            application_date = datetime.strptime(
                application_date, '%Y-%m-%d'
            ).date()
        except ValueError:
            return render_template(
                'edit_application.html',
                application=application,
                error="Please enter a valid application date."
            )

        # Validate status
        if status not in ['Applied', 'Interview', 'Selected', 'Rejected']:
            return render_template(
                'edit_application.html',
                application=application,
                error="Invalid application status."
            )

        # Validate job URL
        if job_url:
            parsed_url = urlparse(job_url)

            if parsed_url.scheme not in ['http', 'https'] or not parsed_url.netloc:
                return render_template(
                    'edit_application.html',
                    application=application,
                    error="Please enter a valid job URL."
                )

        # Update application
        application.company_name = company_name
        application.job_role = job_role
        application.location = location
        application.application_date = application_date
        application.status = status
        application.job_url = job_url
        application.notes = notes

        db.session.commit()

        return redirect(url_for('applications'))

    return render_template(
        'edit_application.html',
        application=application
    )

# Delete application
@app.route('/delete-application/<int:id>', methods=['POST'])
def delete_application(id):

    application = db.get_or_404(JobApplication, id)

    db.session.delete(application)
    db.session.commit()

    return redirect(url_for('applications'))



# Analytics Dashboard
@app.route('/analytics')
def analytics():

    # Application statistics
    total_applications = JobApplication.query.count()

    selected_count = JobApplication.query.filter_by(
        status='Selected'
    ).count()

    if total_applications > 0:
        success_rate = round(
            (selected_count / total_applications) * 100, 2
        )
    else:
        success_rate = 0

    # Total interviews
    total_interviews = Interview.query.count()

    # Application status chart
    application_status = db.session.query(
        JobApplication.status,
        func.count(JobApplication.id)
    ).group_by(JobApplication.status).all()

    status_labels = [row[0] for row in application_status]
    status_values = [row[1] for row in application_status]

    # Interview status chart
    interview_status = db.session.query(
        Interview.status,
        func.count(Interview.id)
    ).group_by(Interview.status).all()

    interview_labels = [row[0] for row in interview_status]
    interview_values = [row[1] for row in interview_status]

    # Monthly application trends
    monthly_data = db.session.query(
        func.strftime('%Y-%m', JobApplication.application_date),
        func.count(JobApplication.id)
    ).filter(
        JobApplication.application_date.isnot(None)
    ).group_by(
        func.strftime('%Y-%m', JobApplication.application_date)
    ).order_by(
        func.strftime('%Y-%m', JobApplication.application_date)
    ).all()

    month_labels = [row[0] for row in monthly_data]
    month_values = [row[1] for row in monthly_data]

    return render_template(
        'analytics.html',
        total_applications=total_applications,
        total_interviews=total_interviews,
        selected_count=selected_count,
        success_rate=success_rate,
        status_labels=status_labels,
        status_values=status_values,
        interview_labels=interview_labels,
        interview_values=interview_values,
        month_labels=month_labels,
        month_values=month_values
    )
# Export Applications to Excel
@app.route('/export-applications')
def export_applications():

    applications = JobApplication.query.order_by(
        JobApplication.id.asc()
    ).all()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Job Applications"

    headers = [
        "ID",
        "Company Name",
        "Job Role",
        "Location",
        "Application Date",
        "Status",
        "Job URL",
        "Notes"
    ]

    sheet.append(headers)

    for application in applications:
        sheet.append([
            application.id,
            application.company_name,
            application.job_role,
            application.location,
            application.application_date,
            application.status,
            application.job_url,
            application.notes
        ])

    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            if cell.value is not None:
                max_length = max(max_length, len(str(cell.value)))

        sheet.column_dimensions[column_letter].width = max_length + 4

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="JobTrack_Applications.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# Run application
if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)