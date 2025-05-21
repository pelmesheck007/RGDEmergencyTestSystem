import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

def generate_uuid():
    return str(uuid.uuid4())

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

