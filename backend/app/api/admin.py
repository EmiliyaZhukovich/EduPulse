from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.database import get_db
from app.models import Group, SurveyLink, SurveySubmission
from app.schemas import FacultyCreate, FacultyUpdate, GroupCreate, GroupUpdate
from services.survey_service import get_group_statistics
from services.faculty_service import (
    create_faculty, get_faculty, get_faculties, update_faculty, delete_faculty,
    create_group, get_group, get_groups, update_group, delete_group
)
from services.auth_service import get_admin_user

router = APIRouter()

@router.get("/faculties")
async def get_all_faculties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Get all faculties"""
    faculties = get_faculties(db, skip, limit)

    result = []
    for faculty in faculties:
        # Get group count
        group_count = db.query(Group).filter(Group.faculty_id == faculty.id).count()

        result.append({
            "id": faculty.id,
            "name": faculty.name,
            "description": faculty.description,
            "created_at": faculty.created_at,
            "group_count": group_count
        })

    return {"faculties": result}

@router.post("/faculties")
async def create_faculty_endpoint(
    faculty_data: FacultyCreate,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Create new faculty"""
    try:
        faculty = create_faculty(db, faculty_data)
        return {
            "id": faculty.id,
            "name": faculty.name,
            "description": faculty.description,
            "created_at": faculty.created_at
        }
    except IntegrityError as e:
        # Likely duplicate faculty name
        db.rollback()
        raise HTTPException(status_code=400, detail="Faculty with this name already exists")

@router.get("/faculties/{faculty_id}")
async def get_faculty_endpoint(
    faculty_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Get faculty by ID"""
    faculty = get_faculty(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {
        "id": faculty.id,
        "name": faculty.name,
        "description": faculty.description,
        "created_at": faculty.created_at
    }

@router.put("/faculties/{faculty_id}")
async def update_faculty_endpoint(
    faculty_id: int,
    faculty_data: FacultyUpdate,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Update faculty"""
    faculty = update_faculty(db, faculty_id, faculty_data)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {
        "id": faculty.id,
        "name": faculty.name,
        "description": faculty.description,
        "created_at": faculty.created_at
    }

@router.delete("/faculties/{faculty_id}")
async def delete_faculty_endpoint(
    faculty_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Delete faculty"""
    success = delete_faculty(db, faculty_id)
    if not success:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {"message": "Faculty deleted successfully"}

@router.get("/groups")
async def get_all_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Get all groups"""
    groups = get_groups(db, skip, limit)

    result = []
    for group in groups:
        # Get submission count
        links = db.query(SurveyLink).filter(SurveyLink.group_id == group.id).all()
        link_ids = [link.id for link in links]
        submission_count = db.query(SurveySubmission).filter(
            SurveySubmission.survey_link_id.in_(link_ids)
        ).count()

        result.append({
            "id": group.id,
            "name": group.name,
            "faculty_id": group.faculty_id,
            "faculty_name": group.faculty.name if group.faculty else None,
            "year": group.year,
            "created_at": group.created_at,
            "submission_count": submission_count
        })

    return {"groups": result}

@router.post("/groups")
async def create_group_endpoint(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Create new group"""
    # Verify faculty exists
    faculty = get_faculty(db, group_data.faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    group = create_group(db, group_data)
    return {
        "id": group.id,
        "name": group.name,
        "faculty_id": group.faculty_id,
        "faculty_name": faculty.name,
        "year": group.year,
        "created_at": group.created_at
    }

@router.get("/groups/{group_id}")
async def get_group_endpoint(
    group_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Get group by ID"""
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return {
        "id": group.id,
        "name": group.name,
        "faculty_id": group.faculty_id,
        "faculty_name": group.faculty.name if group.faculty else None,
        "year": group.year,
        "created_at": group.created_at
    }

@router.put("/groups/{group_id}")
async def update_group_endpoint(
    group_id: int,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Update group"""
    # Verify faculty exists if faculty_id is being updated
    if group_data.faculty_id is not None:
        faculty = get_faculty(db, group_data.faculty_id)
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")

    group = update_group(db, group_id, group_data)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return {
        "id": group.id,
        "name": group.name,
        "faculty_id": group.faculty_id,
        "faculty_name": group.faculty.name if group.faculty else None,
        "year": group.year,
        "created_at": group.created_at
    }

@router.delete("/groups/{group_id}")
async def delete_group_endpoint(
    group_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_admin_user)
):
    """Delete group"""
    success = delete_group(db, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")

    return {"message": "Group deleted successfully"}

@router.get("/statistics/all")
async def get_all_statistics(
    db: Session = Depends(get_db)
):
    """Get aggregated statistics for all groups"""
    groups = db.query(Group).all()

    group_stats = []
    faculty_map = {}

    for group in groups:
        # Get statistics
        stats = get_group_statistics(db, group.id)

        # Get submission count
        links = db.query(SurveyLink).filter(SurveyLink.group_id == group.id).all()
        link_ids = [link.id for link in links]
        total_submissions = db.query(SurveySubmission).filter(
            SurveySubmission.survey_link_id.in_(link_ids)
        ).count()

        group_stat = {
            "group_id": group.id,
            "group_name": group.name,
            "faculty": group.faculty.name if group.faculty else None,
            "year": group.year,
            "total_submissions": total_submissions,
            "question_stats": stats
        }

        group_stats.append(group_stat)

        # Group by faculty
        faculty_name = group.faculty.name if group.faculty else "Не указан"
        if faculty_name not in faculty_map:
            faculty_map[faculty_name] = {
                "total_submissions": 0,
                "total_groups": 0,
                "groups": []
            }

        faculty_map[faculty_name]["total_submissions"] += total_submissions
        faculty_map[faculty_name]["total_groups"] += 1
        faculty_map[faculty_name]["groups"].append(group_stat)

    # Convert faculty map to list
    faculty_stats = []
    for faculty, data in faculty_map.items():
        faculty_stats.append({
            "faculty": faculty,
            "total_submissions": data["total_submissions"],
            "total_groups": data["total_groups"],
            "group_stats": data["groups"]
        })

    # Calculate overall totals
    total_submissions_all = sum(f["total_submissions"] for f in faculty_stats)
    total_groups_all = len(groups)

    return {
        "overall": {
            "total_submissions": total_submissions_all,
            "total_groups": total_groups_all,
            "total_faculties": len(faculty_stats)
        },
        "faculties": faculty_stats
    }

@router.get("/statistics/faculty/{faculty_name}")
async def get_faculty_statistics(
    faculty_name: str,
    db: Session = Depends(get_db)
):
    """Get statistics for specific faculty"""
    groups = db.query(Group).filter(Group.faculty == faculty_name).all()

    if not groups:
        raise HTTPException(status_code=404, detail="Faculty not found")

    group_stats = []
    total_submissions = 0

    for group in groups:
        stats = get_group_statistics(db, group.id)

        links = db.query(SurveyLink).filter(SurveyLink.group_id == group.id).all()
        link_ids = [link.id for link in links]
        submissions = db.query(SurveySubmission).filter(
            SurveySubmission.survey_link_id.in_(link_ids)
        ).count()

        total_submissions += submissions

        group_stats.append({
            "group_id": group.id,
            "group_name": group.name,
            "year": group.year,
            "total_submissions": submissions,
            "question_stats": stats
        })

    return {
        "faculty": faculty_name,
        "total_submissions": total_submissions,
        "total_groups": len(groups),
        "group_stats": group_stats
    }
