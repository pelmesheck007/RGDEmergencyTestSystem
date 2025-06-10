from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker

from api.database import engine
from api.models import *
from api.models.scenario_tests import ScenarioTest, ScenarioStep, ScenarioChoice, ScenarioLog
from api.models.test import TestType
from api.models.user import StudyGroup, StudyGroupMember, User
from api.services.auth import get_password_hash

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_data(db: Session):
    try:
        # 1. Users
        admin = User(
            username="admin",
            email="admin@trainingsys.local",
            hashed_password=get_password_hash("admin"),
            role="admin",
            full_name="Гл Администратор"
        )
        teacher = User(
            username="teacher1",
            email="instructor@trainingsys.local",
            hashed_password=get_password_hash("teacher1"),
            role="teacher",
            position='Прорводник',
            full_name="Инструктор Петрова"
        )
        student = User(
            username="student1",
            email="operator@trainingsys.local",
            hashed_password=get_password_hash("student1"),
            role="student",
            position='Проводник',
            full_name="Оператор Сидоров"
        )

        db.add_all([admin, teacher, student])
        db.flush()

        # 2. Group
        group = StudyGroup(
            name="Аварийная подготовка",
            description="Обучение действиям при ЧС на транспорте"
        )
        db.add(group)
        db.flush()

        db.add_all([
            StudyGroupMember(user_id=teacher.id, group_id=group.id),
            StudyGroupMember(user_id=student.id, group_id=group.id),
        ])

        # 3. Прогресс и игровые данные

        # 4. Тест
        test = Test(
            test_name="Аттестация по ЧС",
            description="Тест по действиям в условиях нештатных ситуаций",
            creator_id=teacher.id,
            test_type=TestType.TRAINING,
            passing_score=1.0,
            time_limit=20
        )
        db.add(test)
        db.flush()

        # Привязка теста к группе
        db.add(GroupAssignedTest(group_id=group.id, test_id=test.id))

        # 5. Задание
        task = Task(
            test_id=test.id,
            question="Что делать при отказе напольной сигнализации?",
            question_details="Сигнальное оборудование перестало работать на перегоне.",
            interaction_type=1,
            difficulty_level=2
        )
        db.add(task)
        db.flush()

        # Варианты ответов
        var1 = VariableAnswer(task_id=task.id, string_answer="Сообщить дежурному", truthful=True)
        var2 = VariableAnswer(task_id=task.id, string_answer="Продолжить движение", truthful=False)
        db.add_all([var1, var2])

        # 6. Ответы на тест
        test_answer = TestAnswer(
            student_id=student.id,
            test_id=test.id,
            score=1.0,
            is_passed=True,
            start_datetime=datetime.utcnow()
        )
        db.add(test_answer)
        db.flush()

        task_answer = TaskAnswer(
            student_id=student.id,
            task_id=task.id,
            test_answer_id=test_answer.id,
            string_answer="Сообщить дежурному",
            score=1.0,
            is_correct=True,
            answer_date=datetime.utcnow()
        )
        db.add(task_answer)
        db.flush()

        db.add(TaskAnswerVariableAnswer(
            task_answer_id=task_answer.id,
            variable_answer_id=var1.id
        ))

        # 7. Сценарный тест
        scenario = ScenarioTest(
            title="Отказ светофора на перегоне",
            description="Пошаговая проверка реакции на отказ сигнализации"
        )
        db.add(scenario)
        db.flush()

        step1 = ScenarioStep(
            scenario_id=scenario.id,
            text="Светофор не работает. Ваши действия?",
            is_final=False
        )
        step2 = ScenarioStep(
            scenario_id=scenario.id,
            text="Кому вы сообщаете о ситуации?",
            is_final=False
        )
        step_final = ScenarioStep(
            scenario_id=scenario.id,
            text="Ситуация локализована. Поезд остановлен. Сценарий завершён.",
            is_final=True
        )

        db.add_all([step1, step2, step_final])
        db.flush()

        # Choices
        db.add_all([
            ScenarioChoice(step_id=step1.id, choice_text="Сообщить дежурному по станции", next_step_id=step2.id, is_critical_error=False),
            ScenarioChoice(step_id=step1.id, choice_text="Проигнорировать и двигаться дальше", next_step_id=step_final.id, is_critical_error=True),
            ScenarioChoice(step_id=step2.id, choice_text="Диспетчеру участка", next_step_id=step_final.id, is_critical_error=False),
            ScenarioChoice(step_id=step2.id, choice_text="Сменщику", next_step_id=step_final.id, is_critical_error=True)
        ])
        db.flush()

        # Scenario log (симуляция прохождения)
        db.add_all([
            ScenarioLog(user_id=student.id, scenario_id=scenario.id, step_id=step1.id, choice_id=step1.choices[0].id, time_taken=10),
            ScenarioLog(user_id=student.id, scenario_id=scenario.id, step_id=step2.id, choice_id=step2.choices[0].id, time_taken=8)
        ])

        db.commit()
        print("✅ Данные успешно добавлены.")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при заполнении тестовых данных: {e}")
        raise
