from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.schemas.answer import TestAnswerIn
from api.services import answer_service  # если есть логика
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/answers", tags=["Answers"])

@router.post("/")
def submit_answers(data: TestAnswerIn, db: Session = Depends(get_db)):
    # можно вызвать сервис answer_service.submit(...)
    # или сделать всё здесь
    return JSONResponse(content={"detail": "Ответы приняты"})
