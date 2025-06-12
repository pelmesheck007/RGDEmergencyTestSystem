from sqlalchemy.orm import Session

from api.models import Task
from sqlalchemy.orm import Session
from typing import Optional, List
from api.models import Test
from api.schemas.test import TestUpdate, TestCreate


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





def get_tests(db: Session) -> List[Test]:
    return db.query(Test).order_by(Test.creation_time.desc()).all()


def get_test(db: Session, test_id: str) -> Optional[Test]:
    return db.query(Test).filter(Test.id == test_id).first()


def create_test(db: Session, data: TestCreate) -> Test:
    test = Test(**data.dict())
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


def update_test(db: Session, test_id: str, updates: dict) -> Optional[Test]:
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        return None

    for key, value in updates.items():
        if hasattr(test, key) and value is not None:
            setattr(test, key, value)

    db.commit()
    db.refresh(test)
    return test


def delete_test(db: Session, test_id: str) -> bool:
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        return False

    db.delete(test)
    db.commit()
    return True
