from uuid import uuid4

from api.schemas.theme_task import TasksBatchCreate
from fastapi import APIRouter, Depends, HTTPException
from pydantic.schema import datetime
from sqlalchemy.orm import Session
from typing import List
from api.database import get_db
from api.dependencies import get_current_user
from api.models import TestTask, VariableAnswer, Task, User
from api.services import theme_task_service
from api.schemas.theme_task import ThemeTaskCreate, ThemeTaskUpdate, ThemeTaskOut, CreateTasksRequest

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/batch/")
def create_tasks_batch(data: TasksBatchCreate, db: Session = Depends(get_db)):
    created_tasks = []

    for i, task_data in enumerate(data.tasks):
        # Создание задачи
        new_task = Task(
            question=task_data.question,
            question_details=task_data.question_details,
            interaction_type=task_data.interaction_type,
            difficulty_level=task_data.difficulty_level,
            count_variables=len(task_data.variable_answers or []),
            time_limit=task_data.time_limit,
            theme=task_data.theme
        )
        db.add(new_task)
        db.flush()  # получаем id

        # Создание ответов
        for j, answer in enumerate(task_data.variable_answers or []):
            db.add(VariableAnswer(
                task_id=new_task.id,
                string_answer=answer.string_answer,
                truthful=answer.truthful,
                explanation=answer.explanation,
                order_number=answer.order_number or j
            ))

        # Привязка к тесту
        db.add(TestTask(
            test_id=data.test_id,
            task_id=new_task.id,
            order_number=i
        ))

        created_tasks.append(new_task)

    db.commit()
    return {"detail": f"Создано {len(created_tasks)} заданий и привязано к тесту {data.test_id}"}

@router.post("/")
def create_tasks(data: CreateTasksRequest, db: Session = Depends(get_db)):
    created_tasks = []

    for task_data in data.tasks:
        variable_answers_data = task_data.variable_answers
        current_user = db.query(User).filter(User.id == data.creator_id).first()

        task = Task(
            id=str(uuid4()),
            question=task_data.question,
            interaction_type=task_data.interaction_type,
            difficulty_level=task_data.difficulty_level,
            count_variables=len(variable_answers_data) if variable_answers_data else 0,
            time_limit=task_data.time_limit,
            theme=task_data.theme,
            creator_id=current_user.id,
            created_date=datetime.utcnow(),
            modified_date=datetime.utcnow(),
        )

        if variable_answers_data:
            for answer_data in variable_answers_data:
                variable_answer = VariableAnswer(
                    id=str(uuid4()),
                    string_answer=answer_data.string_answer,
                    truthful=answer_data.truthful,
                    order_number=answer_data.order_number or 0,
                    explanation=answer_data.explanation
                )
                task.variable_answers.append(variable_answer)

        db.add(task)
        db.flush()

        test_task = TestTask(
            test_id=data.test_id,
            task_id=task.id
        )
        db.add(test_task)
        created_tasks.append(task)

    db.commit()

    return {"created": len(created_tasks), "task_ids": [task.id for task in created_tasks]}