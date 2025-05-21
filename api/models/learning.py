
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, declarative_base
import uuid

from .base import Base

# def generate_uuid():
#     return str(uuid.uuid4())
#
#
# class ThemeTask(Base):
#     __tablename__ = 'theme_tasks'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     theme = Column(String(256), nullable=False)
#     description = Column(Text)
#     parent_theme_id = Column(String, ForeignKey('theme_tasks.id'))
#     created_date = Column(DateTime, default=datetime.utcnow)
#     is_active = Column(Boolean, default=True)
#
#     # Relationships
#     parent_theme = relationship("ThemeTask", remote_side=[id])
#     child_themes = relationship("ThemeTask", back_populates="parent_theme")
#     tasks = relationship("TaskThemeTask", back_populates="theme_task")
#     learning_materials = relationship("LearningMaterialThemeTask", back_populates="theme_task")
#     simulation_scenarios = relationship("SimulationScenarioThemeTask", back_populates="theme_task")
#
#
# class Task(Base):
#     __tablename__ = 'tasks'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     question = Column(Text, nullable=False)
#     question_details = Column(Text)
#     interaction_type = Column(Integer, nullable=False)  # 1=single answer, 2=multiple, 3=text, etc.
#     creator_id = Column(String, ForeignKey('users.id'))
#     created_date = Column(DateTime, default=datetime.utcnow)
#     modified_date = Column(DateTime)
#     difficulty_level = Column(Integer, default=1)
#     count_variables = Column(Integer, default=0)
#     is_active = Column(Boolean, default=True)
#     time_limit = Column(Integer)  # in seconds
#
#     # Relationships
#     creator = relationship("User", back_populates="created_tasks")
#     variable_answers = relationship("VariableAnswer", back_populates="task")
#     theme_tasks = relationship("TaskThemeTask", back_populates="task")
#     test_tasks = relationship("TestTask", back_populates="task")
#     task_answers = relationship("TaskAnswer", back_populates="answered_task")
#
#
# class VariableAnswer(Base):
#     __tablename__ = 'variable_answers'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     string_answer = Column(Text, nullable=False)
#     truthful = Column(Boolean, nullable=False)
#     task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
#     order_number = Column(Integer, default=0)
#     explanation = Column(Text)
#
#     # Relationships
#     task = relationship("Task", back_populates="variable_answers")
#     task_answers = relationship("TaskAnswerVariableAnswer", back_populates="variable_answer")
#
#
# class Test(Base):
#     __tablename__ = 'tests'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     test_name = Column(String(256), nullable=False)
#     description = Column(Text)
#     creator_id = Column(String, ForeignKey('users.id'))
#     creation_time = Column(DateTime, default=datetime.utcnow)
#     modified_time = Column(DateTime)
#     fantom_name = Column(String(256))
#     student_id = Column(String, ForeignKey('users.id'))
#     time_limit = Column(Integer)  # total time in minutes
#     passing_score = Column(Float)
#     test_type = Column(Integer, default=0)  # 0=training, 1=certification
#     is_random_order = Column(Boolean, default=False)
#     is_active = Column(Boolean, default=True)
#     attempts_limit = Column(Integer)
#
#     # Relationships
#     creator = relationship("User", back_populates="created_tests", foreign_keys=[creator_id])
#     student = relationship("User", back_populates="assigned_tests", foreign_keys=[student_id])
#     test_answers = relationship("TestAnswer", back_populates="answered_test")
#     tasks = relationship("TestTask", back_populates="test")
#
#
# class TestAnswer(Base):
#     __tablename__ = 'test_answers'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     student_id = Column(String, ForeignKey('users.id'), nullable=False)
#     answered_test_id = Column(String, ForeignKey('tests.id'), nullable=False)
#     start_datetime = Column(DateTime, default=datetime.utcnow)
#     end_datetime = Column(DateTime)
#     passing_datetime = Column(DateTime)
#     score = Column(Float, nullable=False)
#     max_possible_score = Column(Float, nullable=False)
#     fantom_name = Column(String(256), nullable=False)
#     is_passed = Column(Boolean)
#     attempt_number = Column(Integer, default=1)
#     time_spent = Column(Integer)  # in seconds
#
#     # Relationships
#     student = relationship("User", back_populates="test_answers")
#     answered_test = relationship("Test", back_populates="test_answers")
#     task_answers = relationship("TaskAnswer", back_populates="test_answer")
#
#
# class TaskAnswer(Base):
#     __tablename__ = 'task_answers'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     student_id = Column(String, ForeignKey('users.id'), nullable=False)
#     answered_task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
#     string_answer = Column(Text)
#     test_answer_id = Column(String, ForeignKey('test_answers.id'), nullable=False)
#     score = Column(Float)
#     is_correct = Column(Boolean)
#     time_spent = Column(Integer)  # in seconds
#     answer_date = Column(DateTime, default=datetime.utcnow)
#
#     # Relationships
#     student = relationship("User", back_populates="task_answers")
#     answered_task = relationship("Task", back_populates="task_answers")
#     test_answer = relationship("TestAnswer", back_populates="task_answers")
#     variable_answers = relationship("TaskAnswerVariableAnswer", back_populates="task_answer")
#
#
# class TaskThemeTask(Base):
#     __tablename__ = 'task_theme_tasks'
#
#     task_id = Column(String, ForeignKey('tasks.id'), primary_key=True)
#     theme_task_id = Column(String, ForeignKey('theme_tasks.id'), primary_key=True)
#
#     # Relationships
#     task = relationship("Task", back_populates="theme_tasks")
#     theme_task = relationship("ThemeTask", back_populates="tasks")
#
#
# class TestTask(Base):
#     __tablename__ = 'test_tasks'
#
#     test_id = Column(String, ForeignKey('tests.id'), primary_key=True)
#     task_id = Column(String, ForeignKey('tasks.id'), primary_key=True)
#     order_number = Column(Integer, default=0)
#     score_weight = Column(Float, default=1.0)
#
#     # Relationships
#     test = relationship("Test", back_populates="tasks")
#     task = relationship("Task", back_populates="test_tasks")
#
#
# class TaskAnswerVariableAnswer(Base):
#     __tablename__ = 'task_answer_variable_answers'
#
#     task_answer_id = Column(String, ForeignKey('task_answers.id'), primary_key=True)
#     variable_answer_id = Column(String, ForeignKey('variable_answers.id'), primary_key=True)
#
#     # Relationships
#     task_answer = relationship("TaskAnswer", back_populates="variable_answers")
#     variable_answer = relationship("VariableAnswer", back_populates="task_answers")
#
#
# class MaterialCategory(Base):
#     __tablename__ = 'material_categories'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     name = Column(String(256), nullable=False)
#     description = Column(Text)
#     parent_category_id = Column(String, ForeignKey('material_categories.id'))
#     created_date = Column(DateTime, default=datetime.utcnow)
#     order_number = Column(Integer, default=0)
#     is_active = Column(Boolean, default=True)
#
#     # Relationships
#     parent_category = relationship("MaterialCategory", remote_side=[id])
#     child_categories = relationship("MaterialCategory", back_populates="parent_category")
#     learning_materials = relationship("LearningMaterial", back_populates="category")
#
#
# class LearningMaterial(Base):
#     __tablename__ = 'learning_materials'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     title = Column(String(256), nullable=False)
#     description = Column(Text)
#     content_type = Column(Integer, nullable=False)  # 1=text, 2=video, 3=PDF, 4=presentation
#     content_url = Column(Text)
#     text_content = Column(Text)
#     thumbnail_url = Column(Text)
#     upload_date = Column(DateTime, default=datetime.utcnow)
#     modified_date = Column(DateTime)
#     author_id = Column(String, ForeignKey('users.id'))
#     category_id = Column(String, ForeignKey('material_categories.id'))
#     is_published = Column(Boolean, default=False)
#     is_approved = Column(Boolean, default=False)
#     approver_id = Column(String, ForeignKey('users.id'))
#     approval_date = Column(DateTime)
#     view_count = Column(Integer, default=0)
#     duration = Column(Integer)  # in minutes for videos
#
#     # Relationships
#     author = relationship("User", back_populates="authored_materials", foreign_keys=[author_id])
#     approver = relationship("User", back_populates="approved_materials", foreign_keys=[approver_id])
#     category = relationship("MaterialCategory", back_populates="learning_materials")
#     theme_tasks = relationship("LearningMaterialThemeTask", back_populates="learning_material")
#     progress_records = relationship("MaterialProgress", back_populates="material")
#     ratings = relationship("MaterialRating", back_populates="material")
#
#
# class LearningMaterialThemeTask(Base):
#     __tablename__ = 'learning_material_theme_tasks'
#
#     learning_material_id = Column(String, ForeignKey('learning_materials.id'), primary_key=True)
#     theme_task_id = Column(String, ForeignKey('theme_tasks.id'), primary_key=True)
#
#     # Relationships
#     learning_material = relationship("LearningMaterial", back_populates="theme_tasks")
#     theme_task = relationship("ThemeTask", back_populates="learning_materials")
#
#
# class MaterialProgress(Base):
#     __tablename__ = 'material_progress'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     user_id = Column(String, ForeignKey('users.id'), nullable=False)
#     material_id = Column(String, ForeignKey('learning_materials.id'), nullable=False)
#     progress = Column(Float, default=0)
#     last_accessed = Column(DateTime, default=datetime.utcnow)
#     is_completed = Column(Boolean, default=False)
#     completion_date = Column(DateTime)
#     time_spent = Column(Integer, default=0)  # in seconds
#
#     # Relationships
#     user = relationship("User", back_populates="material_progress")
#     material = relationship("LearningMaterial", back_populates="progress_records")
#
#
# class MaterialRating(Base):
#     __tablename__ = 'material_ratings'
#
#     id = Column(String, primary_key=True, default=generate_uuid)
#     user_id = Column(String, ForeignKey('users.id'), nullable=False)
#     material_id = Column(String, ForeignKey('learning_materials.id'), nullable=False)
#     rating = Column(Integer, nullable=False)
#     review = Column(Text)
#     review_date = Column(DateTime, default=datetime.utcnow)
#
#     # Relationships
#     user = relationship("User", back_populates="material_ratings")
#     material = relationship("LearningMaterial", back_populates="ratings")
#
