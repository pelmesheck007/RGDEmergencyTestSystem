from datetime import datetime, timedelta
from sqlalchemy.orm import Session, sessionmaker

from api.database import engine
from api.models import *
from api.models.learning import MaterialCategory, LearningMaterial, MaterialProgress, MaterialRating
from api.models.user import StudyGroup, StudyGroupMember, UserProgress, UserGameData, User
from api.services.auth import get_password_hash

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_data(db: Session):
    try:
        # 1. Users
        admin = User(
            username="admin",
            email="admin@school.ru",
            hashed_password=get_password_hash("admin"),
            role="admin",
            full_name="Гл Администратор",
            fio="Гл Администратор",
        )

        teacher = User(
            username="teacher1",
            email="teacher@school.ru",
            hashed_password=get_password_hash("teacher1"),
            role="teacher",
            full_name="Мария Преподавателева",
            fio="Мария Преподавателева",
        )
        student = User(
            username="student1",
            email="student1@school.ru",
            hashed_password=get_password_hash("student1"),
            role="student",
            full_name="Иван Студентов",
            fio="Иван Студентов",
        )

        db.add_all([admin, teacher, student])
        db.flush()

        # 2. Groups
        math_group = StudyGroup(name="Математика", description="Группа для математики")
        db.add(math_group)
        db.flush()

        # 3. Group Membership
        db.add_all([
            StudyGroupMember(user_id=teacher.id, group_id=math_group.id),
            StudyGroupMember(user_id=student.id, group_id=math_group.id),
        ])

        # 4. Progress & Game Data
        db.add(UserProgress(user_id=student.id, completed_courses=1, last_active=datetime.utcnow()))
        db.add(UserGameData(user_id=student.id, level=2, experience=300))

        # 5. Category & Material
        category = MaterialCategory(name="Алгебра")
        db.add(category)
        db.flush()

        material = LearningMaterial(
            title="Квадратные уравнения",
            content_type=1,
            text_content="ax^2 + bx + c = 0",
            author_id=teacher.id,
            category_id=category.id,
            is_published=True,
            is_approved=True,
            approver_id=admin.id,
            approval_date=datetime.utcnow()
        )
        db.add(material)
        db.flush()

        db.add(MaterialProgress(user_id=student.id, material_id=material.id, progress=1.0, is_completed=True))
        db.add(MaterialRating(user_id=student.id, material_id=material.id, rating=5, review="Очень полезно!"))

        # 6. Task and Variable Answers
        task = Task(
            question="Сколько решений имеет уравнение x^2 + 1 = 0?",
            interaction_type=1,
            creator_id=teacher.id
        )
        db.add(task)
        db.flush()

        var1 = VariableAnswer(task_id=task.id, string_answer="0", truthful=True)
        var2 = VariableAnswer(task_id=task.id, string_answer="2", truthful=False)
        db.add_all([var1, var2])

        # 7. Test and Answers
        test = Test(
            test_name="Тест по алгебре",
            creator_id=teacher.id,
            student_id=student.id,
            test_type="training",
            is_active=True
        )
        db.add(test)
        db.flush()

        db.add(TestTask(test_id=test.id, task_id=task.id, order_number=1, score_weight=1.0))

        test_answer = TestAnswer(
            student_id=student.id,
            test_id=test.id,
            score=1.0,
            max_possible_score=1.0,
            is_passed=True
        )
        db.add(test_answer)
        db.flush()

        task_answer = TaskAnswer(
            student_id=student.id,
            task_id=task.id,
            test_answer_id=test_answer.id,
            string_answer="0",
            score=1.0,
            is_correct=True
        )
        db.add(task_answer)
        db.flush()

        db.add(TaskAnswerVariableAnswer(task_answer_id=task_answer.id, variable_answer_id=var1.id))

        db.commit()
        print("✅ Данные успешно заполнены.")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        raise


