from app.db.base import Base, engine
from sqlalchemy.exc import OperationalError

def init():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created (if not using Alembic).")
    except OperationalError as e:
        print("❌ Database initialization failed:", e)

if __name__ == "__main__":
    init()
