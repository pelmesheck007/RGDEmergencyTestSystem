from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, selectinload
from typing import List

from api.database import get_db
from api.models import ScenarioTest, ScenarioStep, ScenarioChoice, ScenarioLog
from api.models.scenario_tests import ScenarioResult
from api.schemas.scenario import (
    ScenarioTestOut, ScenarioTestCreate,
    ScenarioStepOut, ScenarioLogCreate, ScenarioChoiceResult
)

router = APIRouter(prefix="/scenario-tests", tags=["Scenario Tests"])


@router.get("/", response_model=List[ScenarioTestOut])
def list_scenarios(db: Session = Depends(get_db)):
    tests = (
        db.query(ScenarioTest)
        .options(selectinload(ScenarioTest.theme))
        .all()
    )
    return tests


@router.get("/{scenario_id}", response_model=ScenarioTestOut)
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = db.query(ScenarioTest).filter_by(id=scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.post("/", response_model=ScenarioTestOut)
def create_scenario(data: ScenarioTestCreate, db: Session = Depends(get_db)):
    new_scenario = ScenarioTest(**data.dict())
    db.add(new_scenario)
    db.commit()
    db.refresh(new_scenario)
    return new_scenario


@router.delete("/{scenario_id}")
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = db.query(ScenarioTest).filter_by(id=scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(scenario)
    db.commit()
    return {"detail": "Deleted successfully"}


@router.get("/{scenario_id}/steps", response_model=List[ScenarioStepOut])
def get_steps(scenario_id: str, db: Session = Depends(get_db)):
    steps = db.query(ScenarioStep).filter_by(scenario_id=scenario_id).order_by(ScenarioStep.id).all()
    if not steps:
        raise HTTPException(status_code=404, detail="No steps found")
    return steps


@router.post("/{scenario_id}/log")
def log_user_step(scenario_id: str, log_data: ScenarioLogCreate, db: Session = Depends(get_db)):
    log_entry = ScenarioLog(**log_data.dict(), scenario_id=scenario_id)
    db.add(log_entry)
    db.commit()
    return {"detail": "Logged"}

@router.get("/{scenario_id}/start", response_model=ScenarioStepOut)
def start_scenario(scenario_id: str, db: Session = Depends(get_db)):
    step = (
        db.query(ScenarioStep)
        .filter(ScenarioStep.scenario_id == scenario_id)
        .order_by(ScenarioStep.order)
        .first()
    )

    if not step:
        raise HTTPException(status_code=404, detail="First step not found")
    return step



@router.post("/{scenario_id}/step", response_model=ScenarioChoiceResult)
def make_choice(
    scenario_id: str,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    step_id = data.get("step_id")
    choice_id = data.get("choice_id")
    time_taken = data.get("time_taken", 0)

    step = db.query(ScenarioStep).filter_by(id=step_id, scenario_id=scenario_id).first()
    choice = db.query(ScenarioChoice).filter_by(id=choice_id, step_id=step_id).first()

    if not step or not choice:
        raise HTTPException(status_code=404, detail="Step or choice not found")

    # лог
    log = ScenarioLog(
        user_id=data.get("user_id"),
        scenario_id=scenario_id,
        step_id=step_id,
        choice_id=choice_id,
        time_taken=time_taken,
    )
    db.add(log)
    db.commit()

    if choice.is_critical_error:
        scenario_result = ScenarioResult(
            user_id=data["user_id"],
            scenario_id=scenario_id,
            result="fail",
            comment="Критическая ошибка"
        )
        db.add(scenario_result)
        db.commit()
        return ScenarioChoiceResult(
            end=True,
            status="fail",
            message="Критическая ошибка. Сценарий завершён.",
            next_step=None
        )

    next_step = (
        db.query(ScenarioStep)
        .filter_by(id=choice.next_step_id)
        .first()
        if choice.next_step_id else None
    )

    if not next_step:
        # сохраняем результат
        scenario_result = ScenarioResult(
            user_id=data["user_id"],
            scenario_id=scenario_id,
            result="success",
            comment="Завершено успешно"
        )
        db.add(scenario_result)
        db.commit()
        return ScenarioChoiceResult(end=True, status="success", message="Сценарий завершён.", next_step=None)

    elif next_step.is_final and not next_step.choices:
        return ScenarioChoiceResult(
            end=True,
            status="continue",
            message="Финальный шаг",
            next_step=next_step
        )

    else:
        return ScenarioChoiceResult(
            end=False,
            status="continue",
            message="Переход к следующему шагу",
            next_step=next_step
        )

@router.post("/{scenario_id}/restart")
def restart_scenario(scenario_id: str, user_id: str, db: Session = Depends(get_db)):
    logs_deleted = db.query(ScenarioLog).filter_by(user_id=user_id, scenario_id=scenario_id).delete()
    db.commit()
    return {"detail": f"Restarted scenario. Deleted {logs_deleted} logs."}
