from sqlalchemy.orm import relationship

from .base import Base

# Импорт моделей
from .user import User, UserProgress, StudyGroupMember, UserRole, StudyGroup
from .task import Task, VariableAnswer, TaskAnswer, TaskAnswerVariableAnswer
from .test import Test, TestTask, TestAnswer
from .learning import LearningMaterial,  MaterialProgress, MaterialRating
from .theme_tasks import ThemeTask

# Указание всех экспортируемых объектов
__all__ = [
    'Base', 'User', 'Task', 'VariableAnswer', 'TaskAnswer', 'TaskAnswerVariableAnswer',
    'Test', 'TestTask', 'TestAnswer',
    'LearningMaterial',
    'ThemeTask', 'UserProgress', 'MaterialProgress', 'MaterialRating',
    'StudyGroupMember',
    'setup_models', 'UserRole', 'StudyGroup'
]


def setup_models():
    """Настройка всех отношений между моделями"""

    TaskAnswer.task = relationship("Task", back_populates="answers")
    TaskAnswer.student = relationship("User", back_populates="task_answers")
