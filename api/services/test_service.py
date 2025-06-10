from sqlalchemy.orm import Session

from api.models import Task

def get_tasks_with_answers(db: Session, test_id: str):
    tasks = (
        db.query(Task)
        .filter(Task.test_id == test_id)
        .order_by(Task.id)  # или поле order_number, если есть
        .all()
    )

    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "question": task.question,
            "interaction_type": task.interaction_type,
            "answers": [
                {
                    "id": va.id,
                    "text": va.string_answer,
                    "truthful": va.truthful
                }
                for va in task.variable_answers
            ]
        })
    return result
