from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from datetime import datetime

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SqlEnum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(SqlEnum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)

    project = relationship("Project", back_populates="tasks")
    owner = relationship("User", back_populates="tasks")
