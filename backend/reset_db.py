import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, SQLModel
import psycopg2

# We will connect directly using psycopg2 to drop tables and recreate them
db_url = "postgresql://postgres:localpassword@localhost:5432/ctfdb"
engine = create_engine(db_url)

def reset():
    from backend.models import Gate, User, UserProgress, Submission
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("Database reset successfully.")
    
    from backend.database import init_db
    # Override settings for local run
    from backend.core.config import settings
    settings.DATABASE_URL = db_url
    init_db()
    print("Database initialized.")

if __name__ == "__main__":
    reset()
