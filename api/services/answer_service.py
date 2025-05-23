from sqlalchemy.orm import Session
from api.models import TestAnswer, TaskAnswer, TaskAnswerVariableAnswer
from api.schemas.answer import TestAnswerIn
from api.models import Test
from datetime import datetime
from uuid import uuid4

def submit_test_answer(db: Session, data: TestAnswerIn):
    test = db.query(Test).filter_by(id=data.test_id).first()
    if not test:
        raise ValueError("Test not found")

    total_score = 0
    max_score = 0

    test_answer = TestAnswer(
        id=str(uuid4()),
        student_id=data.student_id,
        test_id=data.test_id,
        start_datetime=datetime.utcnow(),
        score=0,  # подсчитаем позже
        max_possible_score=0,
        is_passed=False
    )
    db.add(test_answer)
    db.flush()

    for ans in data.answers:
        task_score = 1  # заглушка, можно высчитывать
        is_correct = True  # проверить правильность здесь

        task_answer = TaskAnswer(
            id=str(uuid4()),
            student_id=data.student_id,
            task_id=ans.task_id,
            test_answer_id=test_answer.id,
            string_answer=ans.string_answer,
            score=task_score,
            is_correct=is_correct,
            time_spent=ans.time_spent,
            answer_date=datetime.utcnow()
        )
        db.add(task_answer)

        for var_id in ans.selected_variable_ids:
            db.add(TaskAnswerVariableAnswer(
                task_answer_id=task_answer.id,
                variable_answer_id=var_id
            ))

        total_score += task_score
        max_score += 1

    test_answer.score = total_score
    test_answer.max_possible_score = max_score
    test_answer.is_passed = total_score >= (test.passing_score or 0)
    test_answer.end_datetime = datetime.utcnow()
    test_answer.passing_datetime = datetime.utcnow()

    db.commit()
    db.refresh(test_answer)
    return test_answer
