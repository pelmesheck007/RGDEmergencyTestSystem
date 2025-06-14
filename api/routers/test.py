# routers/test_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import true
from sqlalchemy.orm import Session, selectinload
from typing import List
from api.database import get_db
from api.models import Base, Test, Task
from api.schemas.test import TestCreate, TestUpdate, TestOut
from api.services import test_service
from api.services.test_service import get_tasks_with_answers

router = APIRouter(prefix="/tests", tags=["Tests"])

@router.get("/", response_model=List[TestOut])
def get_tests(db: Session = Depends(get_db)):
    tests = (
        db.query(Test)
        .options(selectinload(Test.theme))
        .all()
    )
    return tests

@router.post("/", response_model=TestOut)
def create_test(data: TestCreate, db: Session = Depends(get_db)):
    return test_service.create_test(db, data)


@router.put("/{test_id}", response_model=TestOut)
def update_test(test_id: str, data: TestUpdate, db: Session = Depends(get_db)):
    updated = test_service.update_test(db, test_id, data.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Test not found")
    return updated



@router.get("/{test_id}", response_model=TestOut)
def get_test(test_id: str, db: Session = Depends(get_db)):
    test = test_service.get_test(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test


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


