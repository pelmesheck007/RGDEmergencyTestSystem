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


from datetime import datetime

def create_test_with_tasks_and_answers(db, teacher, student, group, themes):
    theme1, theme2, theme3 = themes

    test = Test(
        test_name="Аттестация по ЧС",
        description="Тест по действиям в условиях нештатных ситуаций",
        creator_id=teacher.id,
        test_type=TestType.TRAINING,
        passing_score=60,
        theme_id=theme1.id,
        time_limit=20
    )
    db.add(test)
    db.flush()

    db.add(GroupAssignedTest(group_id=group.id, test_id=test.id))

    # ---------- ЗАДАНИЕ 1 ----------
    task1 = Task(
        test_id=test.id,
        question="Что делать при отказе напольной сигнализации?",
        question_details="Сигнальное оборудование перестало работать на перегоне.",
        interaction_type=1,
        difficulty_level=2
    )
    db.add(task1)
    db.flush()

    var1_1 = VariableAnswer(task_id=task1.id, string_answer="Сообщить дежурному", truthful=True)
    var1_2 = VariableAnswer(task_id=task1.id, string_answer="Продолжить движение", truthful=False)
    db.add_all([var1_1, var1_2])

    # ---------- ЗАДАНИЕ 2 ----------
    task2 = Task(
        test_id=test.id,
        question="Как действовать при обнаружении пожара в вагоне?",
        question_details="Вы видите дым, идущий из соседнего отсека.",
        interaction_type=1,
        difficulty_level=2
    )
    db.add(task2)
    db.flush()

    var2_1 = VariableAnswer(task_id=task2.id, string_answer="Сообщить машинисту и приступить к эвакуации", truthful=True)
    var2_2 = VariableAnswer(task_id=task2.id, string_answer="Спрятаться под сиденье", truthful=False)
    db.add_all([var2_1, var2_2])

    # ---------- ЗАДАНИЕ 3 ----------
    task3 = Task(
        test_id=test.id,
        question="Что предпринять при угрозе террористического акта?",
        question_details="Поступило сообщение об угрозе.",
        interaction_type=1,
        difficulty_level=2
    )
    db.add(task3)
    db.flush()

    var3_1 = VariableAnswer(task_id=task3.id, string_answer="Сообщить в правоохранительные органы", truthful=True)
    var3_2 = VariableAnswer(task_id=task3.id, string_answer="Игнорировать и продолжать работу", truthful=False)
    db.add_all([var3_1, var3_2])

    # ---------- Пример ответа студента только на первое задание ----------
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
        task_id=task1.id,
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
        variable_answer_id=var1_1.id
    ))

