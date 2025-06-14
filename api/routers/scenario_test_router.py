from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from typing import List

from api.database import get_db
from api.models import ScenarioTest, ScenarioStep, ScenarioChoice, ScenarioLog
from api.schemas.scenario import (
    ScenarioTestOut, ScenarioTestCreate,
    ScenarioStepOut, ScenarioLogCreate
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
