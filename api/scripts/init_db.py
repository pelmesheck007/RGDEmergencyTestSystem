from datetime import datetime, timedelta

from api.database import engine
from api.models.user import *
from sqlalchemy.orm import sessionmaker, Session

from api.services.auth import get_password_hash

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 3. Функция заполнения данными
from datetime import datetime, timedelta
from sqlalchemy.orm import Session


def create_test_data(db: Session):
    try:
        # 1. Создаем тестовых пользователей
        admin = User(
            username="admin",
            email="admin@school.ru",
            password_hash=get_password_hash("admin"),
            role="admin",
            full_name="Гл Администратор",
            is_active=True,
            registration_date=datetime.utcnow()
        )

        teacher = User(
            username="teacher1",
            email="teacher@school.ru",
            password_hash=get_password_hash("teacher1"),
            role="teacher",
            full_name="Мария Преподавателева",
            is_active=True,
            registration_date=datetime.utcnow()
        )

        student = User(
            username="student1",
            email="student1@school.ru",
            password_hash=get_password_hash("student1"),
            role="student",
            full_name="Иван Студентов",
            is_active=True,
            registration_date=datetime.utcnow()
        )

        db.add_all([admin, teacher, student])
        db.flush()

        # 2. Создаем учебные группы
        math_group = StudyGroup(
            name="Математика 10-А",
            description="Группа по алгебре и геометрии",
            created_at=datetime.utcnow()
        )

        physics_group = StudyGroup(
            name="Физика 10-Б",
            description="Экспериментальная группа",
            created_at=datetime.utcnow()
        )

        db.add_all([math_group, physics_group])
        db.flush()

        # 3. Назначаем пользователей в группы
        memberships = [
            StudyGroupMember(user_id=admin.id, group_id=math_group.id),
            StudyGroupMember(user_id=teacher.id, group_id=math_group.id),
            StudyGroupMember(user_id=teacher.id, group_id=physics_group.id),
            StudyGroupMember(user_id=student.id, group_id=math_group.id)
        ]
        db.add_all(memberships)

        # 4. Добавляем прогресс и игровые данные для студента
        db.add(UserProgress(
            user_id=student.id,
            last_active=datetime.utcnow(),
            completed_courses=2
        ))

        db.add(UserGameData(
            user_id=student.id,
            level=3,
            experience=450
        ))

        db.commit()
        print("✅ Тестовые данные успешно созданы!")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании тестовых данных: {e}")
        raise