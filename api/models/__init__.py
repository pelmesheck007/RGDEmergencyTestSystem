from sqlalchemy.orm import relationship

from .base import Base

# Импорт моделей
from .user import User, StudyGroupMember, UserRole, StudyGroup, GroupAssignedTest
from .test import Test, TestAnswer, Task, VariableAnswer, TaskAnswer, TaskAnswerVariableAnswer, Theme
from .scenario_tests import ScenarioTest, ScenarioLog, ScenarioChoice, ScenarioStep
from .system import Notification, SystemLog, UserSession
# Указание всех экспортируемых объектов
__all__ = [
    'Base', 'User', 'Task', 'VariableAnswer', 'TaskAnswer', 'TaskAnswerVariableAnswer',
    'Test', 'TestAnswer', 'Theme',
    'StudyGroupMember', 'GroupAssignedTest',
    'setup_models', 'UserRole', 'StudyGroup',
    'ScenarioTest', 'ScenarioLog', 'ScenarioChoice', 'ScenarioStep'
]


def setup_models():
    """Настройка всех отношений между моделями"""

    TaskAnswer.task = relationship("Task", back_populates="answers")
    TaskAnswer.student = relationship("User", back_populates="task_answers")
