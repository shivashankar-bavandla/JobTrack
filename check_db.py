from app import app, db
from models import JobApplication

with app.app_context():

    db.create_all()

    tables = db.inspect(db.engine).get_table_names()

    print("Database Tables:", tables)