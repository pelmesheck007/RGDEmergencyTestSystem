from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import TestTask
from api.models.task import Task, VariableAnswer
from api.schemas.theme_task import TasksBatchCreate

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
