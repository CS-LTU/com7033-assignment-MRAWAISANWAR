from app import create_app, db
from app.models.user import User  # Import any additional models here

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully.")