from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FacultyCreate(BaseModel):
    name: str
    description: Optional[str] = None


class FacultyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class FacultyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    name: str
    faculty_id: int
    year: int


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    faculty_id: Optional[int] = None
    year: Optional[int] = None


class GroupResponse(BaseModel):
    id: int
    name: str
    faculty_id: int
    faculty_name: Optional[str] = None
    year: int
    created_at: datetime

    class Config:
        from_attributes = True
