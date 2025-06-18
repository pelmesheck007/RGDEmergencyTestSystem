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
        test_name="Теоретическая аттестация по безопасности",
        description="Проверка знаний правил и норм по безопасности на транспорте",
        creator_id=teacher.id,
        test_type=TestType.TRAINING,
        passing_score=70,
        theme_id=theme1.id,
        time_limit=45
    )
    db.add(test)
    db.flush()

    db.add(GroupAssignedTest(group_id=group.id, test_id=test.id))

    # ---------- Теоретический вопрос 1 ----------
    task1 = Task(
        test_id=test.id,
        question="Что означает сигнал 'Стоп' на железнодорожном транспорте?",
        question_details="Объясните значение и порядок действий при получении сигнала 'Стоп'.",
        interaction_type=1,
        difficulty_level=1
    )
    db.add(task1)
    db.flush()

    var1_1 = VariableAnswer(task_id=task1.id, string_answer="Немедленная остановка поезда", truthful=True)
    var1_2 = VariableAnswer(task_id=task1.id, string_answer="Продолжить движение с осторожностью", truthful=False)
    var1_3 = VariableAnswer(task_id=task1.id, string_answer="Игнорировать сигнал", truthful=False)
    db.add_all([var1_1, var1_2, var1_3])

    # ---------- Теоретический вопрос 2 ----------
    task2 = Task(
        test_id=test.id,
        question="Какие меры предосторожности следует соблюдать при работе с горючими веществами?",
        question_details="Перечислите основные правила и нормы безопасности.",
        interaction_type=1,
        difficulty_level=2
    )
    db.add(task2)
    db.flush()

    var2_1 = VariableAnswer(task_id=task2.id, string_answer="Хранить вдали от источников огня", truthful=True)
    var2_2 = VariableAnswer(task_id=task2.id, string_answer="Использовать защитные средства", truthful=True)
    var2_3 = VariableAnswer(task_id=task2.id, string_answer="Курить вблизи", truthful=False)
    var2_4 = VariableAnswer(task_id=task2.id, string_answer="Оставлять без присмотра", truthful=False)
    db.add_all([var2_1, var2_2, var2_3, var2_4])

    # ---------- Теоретический вопрос 3 ----------
    task3 = Task(
        test_id=test.id,
        question="Что входит в обязанности дежурного по станции при чрезвычайной ситуации?",
        question_details="Опишите основные действия и ответственность дежурного.",
        interaction_type=1,
        difficulty_level=2
    )
    db.add(task3)
    db.flush()

    var3_1 = VariableAnswer(task_id=task3.id, string_answer="Организация эвакуации", truthful=True)
    var3_2 = VariableAnswer(task_id=task3.id, string_answer="Сообщение в экстренные службы", truthful=True)
    var3_3 = VariableAnswer(task_id=task3.id, string_answer="Игнорирование ситуации", truthful=False)
    var3_4 = VariableAnswer(task_id=task3.id, string_answer="Нарушение инструкций", truthful=False)
    db.add_all([var3_1, var3_2, var3_3, var3_4])

    db.flush()

    # Пример ответа студента на первый вопрос
    test_answer = TestAnswer(
        student_id=student.id,
        test_id=test.id,
        score=0.67,
        is_passed=True,
        start_datetime=datetime.utcnow()
    )
    db.add(test_answer)
    db.flush()

    task_answer = TaskAnswer(
        student_id=student.id,
        task_id=task1.id,
        test_answer_id=test_answer.id,
        string_answer="Немедленная остановка поезда",
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
