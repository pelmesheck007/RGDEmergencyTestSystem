from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from api.database import get_db
from api.dependencies import get_current_user
from api.models import VariableAnswer, Task, User
from api.schemas.theme_task import CreateTasksRequest

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/")
def create_tasks(
    data: CreateTasksRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    batch: bool = Query(False, description="Пакетное добавление (без учёта автора)")
):
    created_tasks = []

    for i, task_data in enumerate(data.tasks):
        task = Task(
            id=str(uuid4()),
            test_id=data.test_id,  # 👈 теперь привязка к тесту напрямую
            question=task_data.question,
            question_details=task_data.question_details,
            interaction_type=task_data.interaction_type,
            difficulty_level=task_data.difficulty_level,
            created_date=datetime.utcnow(),
            modified_date=datetime.utcnow()
        )

        if not batch:
            task.creator_id = current_user.id  # если поле осталось

        db.add(task)
        db.flush()

        for j, answer_data in enumerate(task_data.variable_answers or []):
            answer = VariableAnswer(
                id=str(uuid4()),
                task_id=task.id,
                string_answer=answer_data.string_answer,
                truthful=answer_data.truthful,
                explanation=answer_data.explanation,
                order_number=answer_data.order_number or j
            )
            db.add(answer)

        created_tasks.append(task)

    db.commit()
    return {
        "created": len(created_tasks),
        "task_ids": [task.id for task in created_tasks],
        "batch_mode": batch
    }
