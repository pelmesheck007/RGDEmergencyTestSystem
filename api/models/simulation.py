import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from .base import Base
#
# def generate_uuid():
#     return str(uuid.uuid4())
#
# class SimulationScenario(Base):
#     __tablename__ = 'simulation_scenarios'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     title = Column(String(256), nullable=False)
#     description = Column(Text)
#     difficulty_level = Column(Integer, default=1)
#     estimated_duration = Column(Integer)  # in minutes
#     scenario_data = Column(Text)  # JSON with scenario data
#     instructions = Column(Text)
#     is_published = Column(Boolean, default=False)
#     created_date = Column(DateTime, default=datetime.utcnow)
#     modified_date = Column(DateTime)
#     author_id = Column(String, ForeignKey('users.id'))
#     approver_id = Column(String, ForeignKey('users.id'))
#     approval_date = Column(DateTime)
#     version = Column(String(50))
#     min_score_to_pass = Column(Float)
#     is_active = Column(Boolean, default=True)
#
#     # Relationships
#     author = relationship("User", back_populates="authored_scenarios", foreign_keys=[author_id])
#     approver = relationship("User", back_populates="approved_scenarios", foreign_keys=[approver_id])
#     theme_tasks = relationship("SimulationScenarioThemeTask", back_populates="scenario")
#     results = relationship("SimulationResult", back_populates="scenario")
#     checkpoints = relationship("ScenarioCheckpoint", back_populates="scenario")
#
#
# class SimulationScenarioThemeTask(Base):
#     __tablename__ = 'simulation_scenario_theme_tasks'
#
#     scenario_id = Column(String, ForeignKey('simulation_scenarios.id'), primary_key=True)
#     theme_task_id = Column(String, ForeignKey('theme_tasks.id'), primary_key=True)
#
#     # Relationships
#     scenario = relationship("SimulationScenario", back_populates="theme_tasks")
#     theme_task = relationship("ThemeTask", back_populates="simulation_scenarios")
#
#
# class SimulationResult(Base):
#     __tablename__ = 'simulation_results'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     user_id = Column(String, ForeignKey('users.id'), nullable=False)
#     scenario_id = Column(String, ForeignKey('simulation_scenarios.id'), nullable=False)
#     start_time = Column(DateTime, default=datetime.utcnow)
#     end_time = Column(DateTime)
#     score = Column(Float)
#     max_possible_score = Column(Float)
#     is_completed = Column(Boolean, default=False)
#     is_passed = Column(Boolean)
#     actions_log = Column(Text)
#     mistakes_count = Column(Integer, default=0)
#     correct_actions_count = Column(Integer, default=0)
#     time_spent = Column(Integer)  # in seconds
#     attempt_number = Column(Integer, default=1)
#     device_info = Column(String(256))
#
#     # Relationships
#     user = relationship("User", back_populates="simulation_results")
#     scenario = relationship("SimulationScenario", back_populates="results")
#     checkpoint_results = relationship("CheckpointResult", back_populates="simulation_result")
#
#
# class ScenarioCheckpoint(Base):
#     __tablename__ = 'scenario_checkpoints'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     scenario_id = Column(String, ForeignKey('simulation_scenarios.id'), nullable=False)
#     checkpoint_name = Column(String(256), nullable=False)
#     description = Column(Text)
#     order_number = Column(Integer, nullable=False)
#     expected_actions = Column(Text)
#     max_score = Column(Float, default=1.0)
#     time_limit = Column(Integer)  # in seconds
#     is_critical = Column(Boolean, default=False)
#
#     # Relationships
#     scenario = relationship("SimulationScenario", back_populates="checkpoints")
#     checkpoint_results = relationship("CheckpointResult", back_populates="checkpoint")
#
#
# class CheckpointResult(Base):
#     __tablename__ = 'checkpoint_results'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     simulation_result_id = Column(String, ForeignKey('simulation_results.id'), nullable=False)
#     checkpoint_id = Column(String, ForeignKey('scenario_checkpoints.id'), nullable=False)
#     is_passed = Column(Boolean, default=False)
#     time_spent = Column(Integer)  # in seconds
#     mistakes_count = Column(Integer, default=0)
#     score = Column(Float)
#     feedback = Column(Text)
#     details = Column(Text)
#     start_time = Column(DateTime)
#     end_time = Column(DateTime)
#
#     # Relationships
#     simulation_result = relationship("SimulationResult", back_populates="checkpoint_results")
#     checkpoint = relationship("ScenarioCheckpoint", back_populates="checkpoint_results")
