# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from api.models.base import Base

# Путь к SQLite-файлу
DB_PATH = "./railway_training.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Удаление файла, если он существует
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑️ Старый файл базы данных удален.")

# Создание нового движка
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Включить лог запросов
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