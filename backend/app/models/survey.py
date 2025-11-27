from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class SurveyLink(Base):
    __tablename__ = "survey_links"

    id = Column(Integer, primary_key=True, index=True)
    unique_token = Column(String, unique=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    group = relationship("Group", back_populates="survey_links")
    submissions = relationship("SurveySubmission", back_populates="survey_link")


class SurveyTemplate(Base):
    __tablename__ = "survey_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    questions = relationship("SurveyQuestion", back_populates="template", cascade="all, delete-orphan")


class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("survey_templates.id"))
    question_code = Column(String, nullable=False)  # e.g., "comfort", "engagement", "stress"
    question_text = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("SurveyTemplate", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("survey_questions.id"))
    text = Column(String, nullable=False)
    value = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("SurveyQuestion", back_populates="options")


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("survey_templates.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("SurveyTemplate")
    group = relationship("Group", back_populates="surveys")
    answers = relationship("SurveyAnswer", back_populates="survey")


class SurveySubmission(Base):
    __tablename__ = "survey_submissions"

    id = Column(Integer, primary_key=True, index=True)
    survey_link_id = Column(Integer, ForeignKey("survey_links.id"))
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    survey_link = relationship("SurveyLink", back_populates="submissions")
    answers = relationship("SurveyAnswer", back_populates="submission")


class SurveyAnswer(Base):
    __tablename__ = "survey_answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("survey_submissions.id"))
    survey_id = Column(Integer, ForeignKey("surveys.id"))
    # Older schema used question_code/text instead of question_id foreign key.
    # Keep fields compatible with existing DB data which may have question_code/question_text.
    question_code = Column(String, nullable=True)
    question_text = Column(String, nullable=True)
    option_id = Column(Integer, ForeignKey("question_options.id"), nullable=True)
    numeric_value = Column(Float, nullable=True)
    text_value = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    submission = relationship("SurveySubmission", back_populates="answers")
    survey = relationship("Survey", back_populates="answers")
    option = relationship("QuestionOption")
