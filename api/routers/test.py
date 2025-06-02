# routers/test_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import true
from sqlalchemy.orm import Session
from typing import List
from api.database import get_db
from api.models import Base, TestTask, Test
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


def get_tasks_with_answers(db: Session, test_id: str):
    test_tasks = (
        db.query(TestTask)
        .join(Test, Test.id == TestTask.test_id)
        .filter(Test.id == test_id)
        .filter(Test.is_active.is_(true()))
        .order_by(TestTask.order_number)
        .all()
    )

    tasks_with_answers = []
    for test_task in test_tasks:
        task = test_task.task
        variable_answers = task.variable_answers  # подтягиваются по relationship
        tasks_with_answers.append({
            "task": task,
            "variable_answers": variable_answers,
            "order_number": test_task.order_number,
            "score_weight": test_task.score_weight
        })

    return tasks_with_answers

@router.get("/{test_id}/questions/")
def get_test_questions(test_id: str, db: Session = Depends(get_db)):
    tasks = get_tasks_with_answers(db, test_id)
    if not tasks:
        raise HTTPException(status_code=404, detail="Questions not found")
    return tasks
