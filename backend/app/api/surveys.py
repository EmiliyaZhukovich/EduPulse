from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from core.database import get_db
from app.models import Group, SurveyLink, SurveySubmission, Faculty
from app.schemas import SurveySubmissionCreate, SurveyLinkCreate, SurveyGroupSelection
from services.survey_service import create_submission
from services.link_service import generate_unique_token

router = APIRouter()

# Survey questions configuration
SURVEY_QUESTIONS = [
    {
        "code": "comfort",
        "text": "Насколько комфортно вы себя чувствуете в своей учебной группе?",
        "type": "numeric",
        "category": "comfort"
    },
    {
        "code": "engagement",
        "text": "Насколько вы вовлечены в учебный процесс?",
        "type": "numeric",
        "category": "engagement"
    },
    {
        "code": "conflicts",
        "text": "Как часто возникают конфликты в вашей группе?",
        "type": "numeric",
        "category": "conflicts"
    },
    {
        "code": "stress",
        "text": "Как часто вы испытываете стресс из-за учебной нагрузки?",
        "type": "numeric",
        "category": "stress"
    },
    {
        "code": "support",
        "text": "Насколько вы ощущаете поддержку со стороны одногруппников?",
        "type": "numeric",
        "category": "support"
    },
    {
        "code": "open_feedback",
        "text": "Ваши дополнительные комментарии и предложения",
        "type": "text",
        "category": "open_answer"
    }
]

@router.get("/questions")
async def get_survey_questions():
    """Get list of survey questions"""
    return {"questions": SURVEY_QUESTIONS}

@router.post("/submit")
async def submit_survey(
    submission_data: SurveySubmissionCreate,
    db: Session = Depends(get_db)
):
    """Submit anonymous survey"""
    # Verify token
    link = db.query(SurveyLink).filter(
        SurveyLink.unique_token == submission_data.unique_token
    ).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid survey link"
        )

    if not link.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey link is inactive"
        )

    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey link has expired"
        )

    submission = create_submission(db, link.id, submission_data.answers)

    return {
        "message": "Survey submitted successfully",
        "submission_id": submission.id
    }

@router.post("/submit-group")
async def submit_survey_by_group(
    submission_data: SurveyGroupSelection,
    db: Session = Depends(get_db)
):
    """Submit survey by group selection (for public survey)"""
    # Verify group exists
    group = db.query(Group).filter(Group.id == submission_data.group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Create a temporary survey link for this submission
    unique_token = generate_unique_token()
    survey_link = SurveyLink(
        unique_token=unique_token,
        group_id=submission_data.group_id,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(hours=1)  # Expire in 1 hour
    )

    db.add(survey_link)
    db.flush()

    # Create submission
    submission = create_submission(db, survey_link.id, submission_data.answers)

    return {
        "message": "Survey submitted successfully",
        "submission_id": submission.id
    }

@router.post("/links")
async def create_survey_link(
    link_data: SurveyLinkCreate,
    db: Session = Depends(get_db)
):
    """Create new survey link (admin/curator only)"""
    # Check group exists
    group = db.query(Group).filter(Group.id == link_data.group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Generate unique token
    unique_token = generate_unique_token()

    # Create link
    survey_link = SurveyLink(
        unique_token=unique_token,
        group_id=link_data.group_id,
        expires_at=link_data.expires_at,
        is_active=True
    )

    db.add(survey_link)
    db.commit()
    db.refresh(survey_link)

    return {
        "id": survey_link.id,
        "unique_token": survey_link.unique_token,
        "link_url": f"http://localhost:3000/survey/{survey_link.unique_token}",
        "group_id": survey_link.group_id,
        "created_at": survey_link.created_at,
        "expires_at": survey_link.expires_at,
        "is_active": survey_link.is_active
    }

@router.get("/groups")
async def get_survey_groups(
    db: Session = Depends(get_db)
):
    """Get all groups for public survey selection"""
    groups = db.query(Group).join(Faculty).all()

    result = []
    for group in groups:
        result.append({
            "id": group.id,
            "name": group.name,
            "faculty_name": group.faculty.name if group.faculty else "Неизвестный факультет",
            "year": group.year
        })

    return {"groups": result}

@router.get("/links")
async def get_survey_links(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all survey links with submission counts"""
    links = db.query(SurveyLink).offset(skip).limit(limit).all()

    result = []
    for link in links:
        submission_count = db.query(SurveySubmission).filter(
            SurveySubmission.survey_link_id == link.id
        ).count()

        result.append({
            "id": link.id,
            "unique_token": link.unique_token,
            "link_url": f"http://localhost:3000/survey/{link.unique_token}",
            "group_id": link.group_id,
            "group_name": link.group.name if link.group else None,
            "created_at": link.created_at,
            "expires_at": link.expires_at,
            "is_active": link.is_active,
            "submission_count": submission_count
        })

    return {"links": result}
