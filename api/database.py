from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from api.models.base import Base

DB_PATH = "./railway_training.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑️ Старый файл базы данных удален.")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Включить лог запросов
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """Генератор сессий для зависимостей FastAPI"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Создание всех таблиц в базе данных"""
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы в SQLite")