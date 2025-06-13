from sqlalchemy.orm import Session, sessionmaker
from api.database import engine
from api.scripts.create_scenario_tests import create_scenario_tests
from api.scripts.create_tests_themes import create_themes, create_test_with_tasks_and_answers
from api.scripts.create_user_and_groups import create_users, create_study_group

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_data(db: Session):
    try:
        admin, teacher, student = create_users(db)
        group = create_study_group(db, admin, student)
        theme1, theme2, theme3 = create_themes(db)
        create_test_with_tasks_and_answers(db, teacher, student, group, [theme1, theme2, theme3])
        create_scenario_tests(db, student, [theme1, theme2, theme3])

        db.commit()
        print("✅ Данные успешно добавлены.")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при заполнении тестовых данных: {e}")
        raise
