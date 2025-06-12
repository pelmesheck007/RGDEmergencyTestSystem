from api.models.user import StudyGroup, StudyGroupMember, User
from api.services.auth import get_password_hash


def create_users(db):
    admin = User(
        username="admin",
        email="admin@mail.ru",
        hashed_password=get_password_hash("admin"),
        role="admin",
        full_name="Гл Администратор"
    )
    teacher = User(
        username="teacher1",
        email="instructor@mail.ru",
        hashed_password=get_password_hash("teacher1"),
        role="teacher",
        position='Прорводник',
        full_name="Инструктор Петрова"
    )
    student = User(
        username="student1",
        email="operator@mail.ru",
        hashed_password=get_password_hash("student1"),
        role="student",
        position='Проводник',
        full_name="Оператор Сидоров"
    )

    db.add_all([admin, teacher, student])
    db.flush()
    return admin, teacher, student


def create_study_group(db, admin, student):
    group = StudyGroup(
        name="Аварийная подготовка",
        description="Обучение действиям при ЧС на транспорте"
    )
    db.add(group)
    db.flush()

    db.add_all([
        StudyGroupMember(user_id=admin.id, group_id=group.id),
        StudyGroupMember(user_id=student.id, group_id=group.id),
    ])
    return group

