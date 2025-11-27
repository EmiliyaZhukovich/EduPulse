from sqlalchemy.orm import Session
from app.models import Faculty, Group, SurveyAnswer, SurveySubmission, SurveyLink, Survey, Curator
from app.schemas import FacultyCreate, FacultyUpdate, GroupCreate, GroupUpdate

def create_faculty(db: Session, faculty_data: FacultyCreate) -> Faculty:
    """Create new faculty"""
    faculty = Faculty(
        name=faculty_data.name,
        description=faculty_data.description
    )
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return faculty

def get_faculty(db: Session, faculty_id: int) -> Faculty:
    """Get faculty by ID"""
    return db.query(Faculty).filter(Faculty.id == faculty_id).first()

def get_faculties(db: Session, skip: int = 0, limit: int = 100):
    """Get all faculties"""
    return db.query(Faculty).offset(skip).limit(limit).all()

def update_faculty(db: Session, faculty_id: int, faculty_data: FacultyUpdate) -> Faculty:
    """Update faculty"""
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        return None

    if faculty_data.name is not None:
        faculty.name = faculty_data.name
    if faculty_data.description is not None:
        faculty.description = faculty_data.description

    db.commit()
    db.refresh(faculty)
    return faculty

def delete_faculty(db: Session, faculty_id: int) -> bool:
    """Delete faculty"""
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        return False

    db.delete(faculty)
    db.commit()
    return True

def create_group(db: Session, group_data: GroupCreate) -> Group:
    """Create new group"""
    group = Group(
        name=group_data.name,
        faculty_id=group_data.faculty_id,
        year=group_data.year
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

def get_group(db: Session, group_id: int) -> Group:
    """Get group by ID"""
    return db.query(Group).filter(Group.id == group_id).first()

def get_groups(db: Session, skip: int = 0, limit: int = 100):
    """Get all groups"""
    return db.query(Group).offset(skip).limit(limit).all()

def update_group(db: Session, group_id: int, group_data: GroupUpdate) -> Group:
    """Update group"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        return None

    if group_data.name is not None:
        group.name = group_data.name
    if group_data.faculty_id is not None:
        group.faculty_id = group_data.faculty_id
    if group_data.year is not None:
        group.year = group_data.year

    db.commit()
    db.refresh(group)
    return group

def delete_group(db: Session, group_id: int) -> bool:
    """Delete group"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        return False

    try:
        survey_ids = [sid for (sid,) in db.query(Survey.id).filter(Survey.group_id == group_id).all()]
        if survey_ids:
            db.query(SurveyAnswer).filter(SurveyAnswer.survey_id.in_(survey_ids)).delete(synchronize_session=False)

        link_ids = [lid for (lid,) in db.query(SurveyLink.id).filter(SurveyLink.group_id == group_id).all()]
        if link_ids:
            submission_ids = [sid for (sid,) in db.query(SurveySubmission.id).filter(SurveySubmission.survey_link_id.in_(link_ids)).all()]
            if submission_ids:
                db.query(SurveyAnswer).filter(SurveyAnswer.submission_id.in_(submission_ids)).delete(synchronize_session=False)

            db.query(SurveySubmission).filter(SurveySubmission.survey_link_id.in_(link_ids)).delete(synchronize_session=False)

        db.query(SurveyLink).filter(SurveyLink.group_id == group_id).delete(synchronize_session=False)

        db.query(Survey).filter(Survey.group_id == group_id).delete(synchronize_session=False)

        db.query(Curator).filter(Curator.group_id == group_id).delete(synchronize_session=False)

        db.delete(group)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
