from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class QuestionOptionBase(BaseModel):
    text: str
    value: int


class QuestionOptionCreate(QuestionOptionBase):
    pass


class QuestionOption(QuestionOptionBase):
    id: int
    order: int

    class Config:
        from_attributes = True


class SurveyQuestionBase(BaseModel):
    text: str
    options: List[QuestionOptionCreate]


class SurveyQuestionCreate(SurveyQuestionBase):
    pass


class SurveyQuestionUpdate(SurveyQuestionBase):
    id: Optional[int] = None
    options: List[QuestionOption]


class SurveyQuestion(SurveyQuestionBase):
    id: int
    question_code: str
    order: int
    options: List[QuestionOption]

    class Config:
        from_attributes = True


class SurveyTemplateBase(BaseModel):
    title: str
    description: str


class SurveyTemplateCreate(SurveyTemplateBase):
    questions: List[SurveyQuestionCreate]


class SurveyTemplateUpdate(SurveyTemplateBase):
    questions: List[SurveyQuestionUpdate]


class SurveyTemplateDetail(SurveyTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    questions: List[SurveyQuestion]

    class Config:
        from_attributes = True


class QuestionCategory(str, Enum):
    COMFORT = "comfort"
    ENGAGEMENT = "engagement"
    CONFLICTS = "conflicts"
    STRESS = "stress"
    SUPPORT = "support"
    OPEN_ANSWER = "open_answer"


class SurveyAnswerCreate(BaseModel):
    question_code: str
    question_text: str
    numeric_value: Optional[float] = None
    text_value: Optional[str] = None


class SurveySubmissionCreate(BaseModel):
    unique_token: str
    answers: List[SurveyAnswerCreate]


class SurveyGroupSelection(BaseModel):
    group_id: int
    answers: List[SurveyAnswerCreate]


class SurveySubmissionResponse(BaseModel):
    id: int
    submitted_at: datetime

    class Config:
        from_attributes = True


class SurveyAnswerResponse(BaseModel):
    id: int
    question_code: str
    question_text: str
    numeric_value: Optional[float] = None
    text_value: Optional[str] = None

    class Config:
        from_attributes = True


class SurveyLinkCreate(BaseModel):
    group_id: int
    expires_at: Optional[datetime] = None


class SurveyLinkResponse(BaseModel):
    id: int
    unique_token: str
    group_id: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    submission_count: Optional[int] = 0

    class Config:
        from_attributes = True
