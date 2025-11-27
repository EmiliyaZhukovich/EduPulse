from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    groups = relationship("Group", back_populates="faculty")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculties.id"))
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    faculty = relationship("Faculty", back_populates="groups")
    surveys = relationship("Survey", back_populates="group")
    survey_links = relationship("SurveyLink", back_populates="group")
