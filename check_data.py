from app import app, db
from models import JobApplication

with app.app_context():

    duplicate = JobApplication.query.get(2)

    if duplicate:
        db.session.delete(duplicate)
        db.session.commit()
        print("Duplicate application deleted successfully!")
    else:
        print("Application not found!")

    print("Remaining applications:", JobApplication.query.count())