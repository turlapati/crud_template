from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

def get_database_config():
    """Get database configuration based on DATABASE_URL."""
    db_url = settings.DATABASE_URL
    connect_args = {}
    engine_kwargs = {}
    
    if db_url.startswith("sqlite"):
        # SQLite-specific configuration
        connect_args = {"check_same_thread": False}
        engine_kwargs = {"pool_pre_ping": True}
        
    elif db_url.startswith("postgresql"):
        # PostgreSQL-specific configuration
        engine_kwargs = {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 300,  # Recycle connections every 5 minutes
        }
        
    elif db_url.startswith("mysql"):
        # MySQL-specific configuration
        connect_args = {
            "charset": "utf8mb4",
            "use_unicode": True,
        }
        engine_kwargs = {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # Recycle connections every hour (MySQL timeout)
        }
        
    elif db_url.startswith("oracle"):
        # Oracle-specific configuration
        engine_kwargs = {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 1800,  # Recycle connections every 30 minutes
            "echo": False,  # Set to True for SQL debugging
        }
    else:
        raise ValueError(f"Unsupported database type in DATABASE_URL: {db_url}")
    
    return {
        "url": db_url,
        "connect_args": connect_args,
        "engine_kwargs": engine_kwargs
    }

# Get database configuration
config = get_database_config()

# Create the SQLAlchemy engine
engine = create_engine(
    config["url"],
    **config["engine_kwargs"],
    connect_args=config["connect_args"]
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """FastAPI dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()