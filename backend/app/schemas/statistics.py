from pydantic import BaseModel
from typing import List
from datetime import datetime


class QuestionStatistics(BaseModel):
    question_code: str
    question_text: str
    average: float
    count: int
    min: float
    max: float


class GroupStatistics(BaseModel):
    group_id: int
    group_name: str
    total_submissions: int
    question_stats: List[QuestionStatistics]


class FacultyStatistics(BaseModel):
    faculty: str
    total_submissions: int
    total_groups: int
    group_stats: List[GroupStatistics]


class OpenAnswerResponse(BaseModel):
    question_code: str
    question_text: str
    text_value: str
    submitted_at: datetime
