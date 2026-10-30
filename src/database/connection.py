from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseConnection:
    _engine = None
    _SessionLocal = None

    @classmethod
    def init_db(cls):
        try:
            cls._engine = create_engine(
                config.DATABASE_URL,
                echo=config.DEBUG,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
            cls._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls._engine
            )
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    @classmethod
    def get_session(cls) -> Session:
        if cls._SessionLocal is None:
            cls.init_db()
        return cls._SessionLocal()

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            cls.init_db()
        return cls._engine

    @classmethod
    def close_all(cls):
        if cls._engine:
            cls._engine.dispose()
            logger.info("Database connections closed")

def get_db() -> Session:
    db = DatabaseConnection.get_session()
    try:
        yield db
    finally:
        db.close()
