# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from api.models.base import Base

# Для SQLite используем относительный путь к файлу БД
SQLALCHEMY_DATABASE_URL = "sqlite:///./railway_training1.db"

# Создаем синхронный движок для SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Нужно для SQLite
    echo=True  # Логирование SQL-запросов
)



# Настройка сессии
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