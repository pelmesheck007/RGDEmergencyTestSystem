from datetime import datetime
from api.models import *
from api.models.test import TestType


def create_themes(db):
    theme1 = Theme(title="ЧС на транспорте", description="Поведение при ЧС")
    theme2 = Theme(title="Пожарная безопасность", description="Правила поведения при пожаре")
    theme3 = Theme(title="Техногенные аварии", description="Реакция на аварии техногенного характера")
    db.add_all([theme1, theme2, theme3])
    db.flush()
    return theme1, theme2, theme3


def create_test_with_tasks_and_answers(db, teacher, student, group, themes):
    theme1, theme2, theme3 = themes
    test = Test(
        test_name="Аттестация по ЧС",
        description="Тест по действиям в условиях нештатных ситуаций",
        creator_id=teacher.id,
        test_type=TestType.TRAINING,
        passing_score=1.0,
        theme_id=theme1.id,
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

