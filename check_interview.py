from app import app, db
from models import JobApplication, Interview

with app.app_context():

    tables = db.inspect(db.engine).get_table_names()

    print("Database Tables:", tables)

    print("Job Applications:", JobApplication.query.count())

    print("Interview Records:", Interview.query.count())