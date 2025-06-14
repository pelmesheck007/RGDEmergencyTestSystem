import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import TestAnswer, TaskAnswer, TaskAnswerVariableAnswer, VariableAnswer
from api.schemas.answer import TestAnswerIn
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/answers", tags=["Answers"])

@router.post("/")
def submit_answers(data: TestAnswerIn, db: Session = Depends(get_db)):
    test_answer = TestAnswer(
        id=str(uuid.uuid4()),
        student_id=data.student_id,
        test_id=data.test_id,
        start_datetime=datetime.utcnow(),
        end_datetime=datetime.utcnow(),
        score=0.0,
        is_passed=False
    )
    db.add(test_answer)
    db.flush()

    total_score = 0
    for ans in data.answers:
        task_answer = TaskAnswer(
            id=str(uuid.uuid4()),
            test_answer_id=test_answer.id,
            task_id=ans.task_id,
            student_id=data.student_id,
            time_spent=ans.time_spent,
            answer_date=datetime.utcnow()
        )

        if ans.string_answer:
            task_answer.string_answer = ans.string_answer

        db.add(task_answer)
        db.flush()


        for var_id in ans.selected_variable_ids:
            db.add(TaskAnswerVariableAnswer(
                task_answer_id=task_answer.id,
                variable_answer_id=var_id
            ))

            variable = db.query(VariableAnswer).filter_by(id=var_id).first()
            if variable and variable.truthful:
                total_score += 1


    test_answer.score = total_score
    test_answer.is_passed = total_score >= 1

    db.commit()

    return JSONResponse(content={"detail": "Ответы успешно сохранены", "score": total_score})
