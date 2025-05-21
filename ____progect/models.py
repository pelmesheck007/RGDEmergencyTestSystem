
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(256), nullable=False, unique=True)
    normalized_username = Column(String(256))
    email = Column(String(256))
    email_confirmed = Column(Boolean, default=False)
    password_hash = Column(Text)
    security_stamp = Column(Text)
    access_flags = Column(Integer, default=0)
    full_name = Column(String(256))
    position = Column(String(256))
    department = Column(String(256))
    last_login_date = Column(DateTime)
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    created_groups = relationship("UserGroup", back_populates="creator")
    created_tasks = relationship("Task", back_populates="creator")
    created_tests = relationship("Test", back_populates="creator")
    assigned_tests = relationship("Test", back_populates="student", foreign_keys="[Test.student_id]")
    test_answers = relationship("TestAnswer", back_populates="student")
    task_answers = relationship("TaskAnswer", back_populates="student")
    authored_materials = relationship("LearningMaterial", back_populates="author")
    approved_materials = relationship("LearningMaterial", back_populates="approver")
    authored_scenarios = relationship("SimulationScenario", back_populates="author")
    approved_scenarios = relationship("SimulationScenario", back_populates="approver")
    simulation_results = relationship("SimulationResult", back_populates="user")
    material_progress = relationship("MaterialProgress", back_populates="user")
    material_ratings = relationship("MaterialRating", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    logs = relationship("SystemLog", back_populates="user")
    user_groups = relationship("UserUserGroup", back_populates="user")


class UserGroup(Base):
    __tablename__ = 'user_groups'

    id = Column(String, primary_key=True, default=generate_uuid)
    group_name = Column(String(256), nullable=False)
    description = Column(Text)
    group_creator_id = Column(String, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.utcnow)
    is_system_group = Column(Boolean, default=False)

    # Relationships
    creator = relationship("User", back_populates="created_groups")
    members = relationship("UserUserGroup", back_populates="user_group")


class UserUserGroup(Base):
    __tablename__ = 'user_user_groups'

    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    user_group_id = Column(String, ForeignKey('user_groups.id'), primary_key=True)
    join_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_groups")
    user_group = relationship("UserGroup", back_populates="members")


class ThemeTask(Base):
    __tablename__ = 'theme_tasks'

    id = Column(String, primary_key=True, default=generate_uuid)
    theme = Column(String(256), nullable=False)
    description = Column(Text)
    parent_theme_id = Column(String, ForeignKey('theme_tasks.id'))
    created_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    parent_theme = relationship("ThemeTask", remote_side=[id])
    child_themes = relationship("ThemeTask", back_populates="parent_theme")
    tasks = relationship("TaskThemeTask", back_populates="theme_task")
    learning_materials = relationship("LearningMaterialThemeTask", back_populates="theme_task")
    simulation_scenarios = relationship("SimulationScenarioThemeTask", back_populates="theme_task")


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, default=generate_uuid)
    question = Column(Text, nullable=False)
    question_details = Column(Text)
    interaction_type = Column(Integer, nullable=False)  # 1=single answer, 2=multiple, 3=text, etc.
    creator_id = Column(String, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime)
    difficulty_level = Column(Integer, default=1)
    count_variables = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    time_limit = Column(Integer)  # in seconds

    # Relationships
    creator = relationship("User", back_populates="created_tasks")
    variable_answers = relationship("VariableAnswer", back_populates="task")
    theme_tasks = relationship("TaskThemeTask", back_populates="task")
    test_tasks = relationship("TestTask", back_populates="task")
    task_answers = relationship("TaskAnswer", back_populates="answered_task")


class VariableAnswer(Base):
    __tablename__ = 'variable_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    string_answer = Column(Text, nullable=False)
    truthful = Column(Boolean, nullable=False)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    order_number = Column(Integer, default=0)
    explanation = Column(Text)

    # Relationships
    task = relationship("Task", back_populates="variable_answers")
    task_answers = relationship("TaskAnswerVariableAnswer", back_populates="variable_answer")


class Test(Base):
    __tablename__ = 'tests'

    id = Column(String, primary_key=True, default=generate_uuid)
    test_name = Column(String(256), nullable=False)
    description = Column(Text)
    creator_id = Column(String, ForeignKey('users.id'))
    creation_time = Column(DateTime, default=datetime.utcnow)
    modified_time = Column(DateTime)
    fantom_name = Column(String(256))
    student_id = Column(String, ForeignKey('users.id'))
    time_limit = Column(Integer)  # total time in minutes
    passing_score = Column(Float)
    test_type = Column(Integer, default=0)  # 0=training, 1=certification
    is_random_order = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    attempts_limit = Column(Integer)

    # Relationships
    creator = relationship("User", back_populates="created_tests", foreign_keys=[creator_id])
    student = relationship("User", back_populates="assigned_tests", foreign_keys=[student_id])
    test_answers = relationship("TestAnswer", back_populates="answered_test")
    tasks = relationship("TestTask", back_populates="test")


class TestAnswer(Base):
    __tablename__ = 'test_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey('users.id'), nullable=False)
    answered_test_id = Column(String, ForeignKey('tests.id'), nullable=False)
    start_datetime = Column(DateTime, default=datetime.utcnow)
    end_datetime = Column(DateTime)
    passing_datetime = Column(DateTime)
    score = Column(Float, nullable=False)
    max_possible_score = Column(Float, nullable=False)
    fantom_name = Column(String(256), nullable=False)
    is_passed = Column(Boolean)
    attempt_number = Column(Integer, default=1)
    time_spent = Column(Integer)  # in seconds

    # Relationships
    student = relationship("User", back_populates="test_answers")
    answered_test = relationship("Test", back_populates="test_answers")
    task_answers = relationship("TaskAnswer", back_populates="test_answer")


class TaskAnswer(Base):
    __tablename__ = 'task_answers'

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey('users.id'), nullable=False)
    answered_task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    string_answer = Column(Text)
    test_answer_id = Column(String, ForeignKey('test_answers.id'), nullable=False)
    score = Column(Float)
    is_correct = Column(Boolean)
    time_spent = Column(Integer)  # in seconds
    answer_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="task_answers")
    answered_task = relationship("Task", back_populates="task_answers")
    test_answer = relationship("TestAnswer", back_populates="task_answers")
    variable_answers = relationship("TaskAnswerVariableAnswer", back_populates="task_answer")


class TaskThemeTask(Base):
    __tablename__ = 'task_theme_tasks'

    task_id = Column(String, ForeignKey('tasks.id'), primary_key=True)
    theme_task_id = Column(String, ForeignKey('theme_tasks.id'), primary_key=True)

    # Relationships
    task = relationship("Task", back_populates="theme_tasks")
    theme_task = relationship("ThemeTask", back_populates="tasks")


class TestTask(Base):
    __tablename__ = 'test_tasks'

    test_id = Column(String, ForeignKey('tests.id'), primary_key=True)
    task_id = Column(String, ForeignKey('tasks.id'), primary_key=True)
    order_number = Column(Integer, default=0)
    score_weight = Column(Float, default=1.0)

    # Relationships
    test = relationship("Test", back_populates="tasks")
    task = relationship("Task", back_populates="test_tasks")


class TaskAnswerVariableAnswer(Base):
    __tablename__ = 'task_answer_variable_answers'

    task_answer_id = Column(String, ForeignKey('task_answers.id'), primary_key=True)
    variable_answer_id = Column(String, ForeignKey('variable_answers.id'), primary_key=True)

    # Relationships
    task_answer = relationship("TaskAnswer", back_populates="variable_answers")
    variable_answer = relationship("VariableAnswer", back_populates="task_answers")


class MaterialCategory(Base):
    __tablename__ = 'material_categories'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(256), nullable=False)
    description = Column(Text)
    parent_category_id = Column(String, ForeignKey('material_categories.id'))
    created_date = Column(DateTime, default=datetime.utcnow)
    order_number = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Relationships
    parent_category = relationship("MaterialCategory", remote_side=[id])
    child_categories = relationship("MaterialCategory", back_populates="parent_category")
    learning_materials = relationship("LearningMaterial", back_populates="category")


class LearningMaterial(Base):
    __tablename__ = 'learning_materials'

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    content_type = Column(Integer, nullable=False)  # 1=text, 2=video, 3=PDF, 4=presentation
    content_url = Column(Text)
    text_content = Column(Text)
    thumbnail_url = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime)
    author_id = Column(String, ForeignKey('users.id'))
    category_id = Column(String, ForeignKey('material_categories.id'))
    is_published = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    approver_id = Column(String, ForeignKey('users.id'))
    approval_date = Column(DateTime)
    view_count = Column(Integer, default=0)
    duration = Column(Integer)  # in minutes for videos

    # Relationships
    author = relationship("User", back_populates="authored_materials", foreign_keys=[author_id])
    approver = relationship("User", back_populates="approved_materials", foreign_keys=[approver_id])
    category = relationship("MaterialCategory", back_populates="learning_materials")
    theme_tasks = relationship("LearningMaterialThemeTask", back_populates="learning_material")
    progress_records = relationship("MaterialProgress", back_populates="material")
    ratings = relationship("MaterialRating", back_populates="material")


class LearningMaterialThemeTask(Base):
    __tablename__ = 'learning_material_theme_tasks'

    learning_material_id = Column(String, ForeignKey('learning_materials.id'), primary_key=True)
    theme_task_id = Column(String, ForeignKey('theme_tasks.id'), primary_key=True)

    # Relationships
    learning_material = relationship("LearningMaterial", back_populates="theme_tasks")
    theme_task = relationship("ThemeTask", back_populates="learning_materials")


class MaterialProgress(Base):
    __tablename__ = 'material_progress'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    material_id = Column(String, ForeignKey('learning_materials.id'), nullable=False)
    progress = Column(Float, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime)
    time_spent = Column(Integer, default=0)  # in seconds

    # Relationships
    user = relationship("User", back_populates="material_progress")
    material = relationship("LearningMaterial", back_populates="progress_records")


class MaterialRating(Base):
    __tablename__ = 'material_ratings'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    material_id = Column(String, ForeignKey('learning_materials.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    review = Column(Text)
    review_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="material_ratings")
    material = relationship("LearningMaterial", back_populates="ratings")


class SimulationScenario(Base):
    __tablename__ = 'simulation_scenarios'

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    difficulty_level = Column(Integer, default=1)
    estimated_duration = Column(Integer)  # in minutes
    scenario_data = Column(Text)  # JSON with scenario data
    instructions = Column(Text)
    is_published = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime)
    author_id = Column(String, ForeignKey('users.id'))
    approver_id = Column(String, ForeignKey('users.id'))
    approval_date = Column(DateTime)
    version = Column(String(50))
    min_score_to_pass = Column(Float)
    is_active = Column(Boolean, default=True)

    # Relationships
    author = relationship("User", back_populates="authored_scenarios", foreign_keys=[author_id])
    approver = relationship("User", back_populates="approved_scenarios", foreign_keys=[approver_id])
    theme_tasks = relationship("SimulationScenarioThemeTask", back_populates="scenario")
    results = relationship("SimulationResult", back_populates="scenario")
    checkpoints = relationship("ScenarioCheckpoint", back_populates="scenario")


class SimulationScenarioThemeTask(Base):
    __tablename__ = 'simulation_scenario_theme_tasks'

    scenario_id = Column(String, ForeignKey('simulation_scenarios.id'), primary_key=True)
    theme_task_id = Column(String, ForeignKey('theme_tasks.id'), primary_key=True)

    # Relationships
    scenario = relationship("SimulationScenario", back_populates="theme_tasks")
    theme_task = relationship("ThemeTask", back_populates="simulation_scenarios")


class SimulationResult(Base):
    __tablename__ = 'simulation_results'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    scenario_id = Column(String, ForeignKey('simulation_scenarios.id'), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    score = Column(Float)
    max_possible_score = Column(Float)
    is_completed = Column(Boolean, default=False)
    is_passed = Column(Boolean)
    actions_log = Column(Text)
    mistakes_count = Column(Integer, default=0)
    correct_actions_count = Column(Integer, default=0)
    time_spent = Column(Integer)  # in seconds
    attempt_number = Column(Integer, default=1)
    device_info = Column(String(256))

    # Relationships
    user = relationship("User", back_populates="simulation_results")
    scenario = relationship("SimulationScenario", back_populates="results")
    checkpoint_results = relationship("CheckpointResult", back_populates="simulation_result")


class ScenarioCheckpoint(Base):
    __tablename__ = 'scenario_checkpoints'

    id = Column(String, primary_key=True, default=generate_uuid)
    scenario_id = Column(String, ForeignKey('simulation_scenarios.id'), nullable=False)
    checkpoint_name = Column(String(256), nullable=False)
    description = Column(Text)
    order_number = Column(Integer, nullable=False)
    expected_actions = Column(Text)
    max_score = Column(Float, default=1.0)
    time_limit = Column(Integer)  # in seconds
    is_critical = Column(Boolean, default=False)

    # Relationships
    scenario = relationship("SimulationScenario", back_populates="checkpoints")
    checkpoint_results = relationship("CheckpointResult", back_populates="checkpoint")


class CheckpointResult(Base):
    __tablename__ = 'checkpoint_results'

    id = Column(String, primary_key=True, default=generate_uuid)
    simulation_result_id = Column(String, ForeignKey('simulation_results.id'), nullable=False)
    checkpoint_id = Column(String, ForeignKey('scenario_checkpoints.id'), nullable=False)
    is_passed = Column(Boolean, default=False)
    time_spent = Column(Integer)  # in seconds
    mistakes_count = Column(Integer, default=0)
    score = Column(Float)
    feedback = Column(Text)
    details = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    # Relationships
    simulation_result = relationship("SimulationResult", back_populates="checkpoint_results")
    checkpoint = relationship("ScenarioCheckpoint", back_populates="checkpoint_results")


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    title = Column(String(256), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Integer, nullable=False)
    is_read = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    read_date = Column(DateTime)
    related_entity_id = Column(String)
    related_entity_type = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="notifications")


class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(256), nullable=False)
    device_info = Column(String(256))
    ip_address = Column(String(50))
    login_date = Column(DateTime, default=datetime.utcnow)
    last_activity_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")


class SystemLog(Base):
    __tablename__ = 'system_logs'

    id = Column(String, primary_key=True, default=generate_uuid)
    log_level = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    exception = Column(Text)
    source = Column(String(256))
    user_id = Column(String, ForeignKey('users.id'))
    created_date = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))
    action = Column(String(256))
    entity_type = Column(String(256))
    entity_id = Column(String)

    # Relationships
    user = relationship("User", back_populates="logs")

