# routers/test_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import true
from sqlalchemy.orm import Session
from typing import List
from api.database import get_db
from api.models import Base, Test, Task
from api.schemas.test import TestCreate, TestUpdate, TestOut, QuestionOut
from api.services import test_service

router = APIRouter(prefix="/tests", tags=["Tests"])

@router.get("/", response_model=List[TestOut])
def list_tests(db: Session = Depends(get_db)):
    return test_service.get_tests(db)

@router.post("/", response_model=TestOut)
def create_test(data: TestCreate, db: Session = Depends(get_db)):
    return test_service.create_test(db, **data.dict())


@router.get("/{test_id}", response_model=TestOut)
def get_test(test_id: str, db: Session = Depends(get_db)):
    test = test_service.get_test(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.put("/{test_id}", response_model=TestOut)
def update_test(test_id: str, data: TestUpdate, db: Session = Depends(get_db)):
    updated = test_service.update_test(db, test_id, data.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Test not found")
    return updated

@router.delete("/{test_id}")
def delete_test(test_id: str, db: Session = Depends(get_db)):
    deleted = test_service.delete_test(db, test_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    return {"detail": "Deleted successfully"}



@router.get("/{test_id}/questions/")
def get_test_questions(test_id: str, db: Session = Depends(get_db)):
    tasks = get_tasks_with_answers(db, test_id)
    if not tasks:
        raise HTTPException(status_code=404, detail="Questions not found")
    return tasks


def serialize_task(task: Task):
    return {
        "id": task.id,
        "question": task.question,
        "question_details": task.question_details,
        "interaction_type": task.interaction_type,
        "difficulty_level": task.difficulty_level,
        "variable_answers": [
            {
                "id": va.id,
                "string_answer": va.string_answer,
                "truthful": va.truthful,
                "order_number": va.order_number,
                "explanation": va.explanation
            } for va in task.variable_answers
        ]
    }

def get_tasks_with_answers(db: Session, test_id: str):
    tasks = (
        db.query(Task)
        .filter(Task.test_id == test_id)
        .order_by(Task.difficulty_level)
        .all()
    )

    return [serialize_task(task) for task in tasks]

