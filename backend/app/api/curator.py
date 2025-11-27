from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from app.models import SurveyLink, SurveySubmission, SurveyAnswer, Group
from services.survey_service import get_group_statistics

router = APIRouter()

@router.get("/groups")
async def get_curator_groups(
    # curator = Depends(get_current_curator),
    db: Session = Depends(get_db)
):
    """Get all groups (in production, filtered by curator)"""
    groups = db.query(Group).all()

    result = []
    for group in groups:
        result.append({
            "id": group.id,
            "name": group.name,
            "faculty": group.faculty,
            "year": group.year,
            "created_at": group.created_at
        })

    return {"groups": result}

@router.get("/groups/{group_id}/statistics")
async def get_group_statistics_route(
    group_id: int,
    # curator = Depends(get_current_curator),
    db: Session = Depends(get_db)
):
    """Get statistics for specific group"""
    # Verify group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Get statistics
    stats = get_group_statistics(db, group_id)

    # Get total submission count
    links = db.query(SurveyLink).filter(SurveyLink.group_id == group_id).all()
    link_ids = [link.id for link in links]
    total_submissions = db.query(SurveySubmission).filter(
        SurveySubmission.survey_link_id.in_(link_ids)
    ).count()

    # Get open answers
    answers = db.query(SurveyAnswer).join(SurveySubmission).filter(
        SurveySubmission.survey_link_id.in_(link_ids),
        SurveyAnswer.text_value.isnot(None)
    ).order_by(SurveyAnswer.created_at.desc()).all()

    open_answers = []
    for answer in answers:
        open_answers.append({
            "question_code": answer.question_code,
            "question_text": answer.question_text,
            "text_value": answer.text_value,
            "submitted_at": answer.created_at
        })

    return {
        "group_id": group.id,
        "group_name": group.name,
        "faculty": group.faculty,
        "total_submissions": total_submissions,
        "question_stats": stats,
        "open_answers": open_answers[:50]  # Limit to last 50
    }

@router.get("/groups/{group_id}/links")
async def get_group_links(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Get all survey links for a group"""
    links = db.query(SurveyLink).filter(SurveyLink.group_id == group_id).all()

    result = []
    for link in links:
        submission_count = db.query(SurveySubmission).filter(
            SurveySubmission.survey_link_id == link.id
        ).count()

        result.append({
            "id": link.id,
            "unique_token": link.unique_token,
            "link_url": f"http://localhost:3000/survey/{link.unique_token}",
            "created_at": link.created_at,
            "expires_at": link.expires_at,
            "is_active": link.is_active,
            "submission_count": submission_count
        })

    return {"links": result}
