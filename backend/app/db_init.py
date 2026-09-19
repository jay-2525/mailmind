"""
Database initialization script to create all tables.
"""
from app.core.database import engine, Base
import app.models  # Ensure all models are registered

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
