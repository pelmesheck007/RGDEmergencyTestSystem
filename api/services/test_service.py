# services/test_service.py
from sqlalchemy.orm import Session
from api.models.test import Test, TestTask
from typing import List, Optional
from datetime import datetime


def create_test(db: Session, **kwargs) -> Test:
    new_test = Test(**kwargs)
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return new_test


def get_test(db: Session, test_id: str) -> Optional[Test]:
    return db.query(Test).filter(Test.id == test_id).first()


def get_tests(db: Session) -> List[Test]:
    return db.query(Test).all()


def update_test(db: Session, test_id: str, updates: dict) -> Optional[Test]:
    test = get_test(db, test_id)
    if not test:
        return None
    for key, value in updates.items():
        setattr(test, key, value)
    test.modified_time = datetime.utcnow()
    db.commit()
    db.refresh(test)
    return test


def delete_test(db: Session, test_id: str) -> bool:
    test = get_test(db, test_id)
    if not test:
        return False
    db.delete(test)
    db.commit()
    return True

def get_tasks_with_answers(db: Session, test_id: str):
    test_tasks = (
        db.query(TestTask)
        .filter(TestTask.test_id == test_id)
        .order_by(TestTask.order_number)
        .all()
    )

    result = []
    for tt in test_tasks:
        task = tt.task
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
