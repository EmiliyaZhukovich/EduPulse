from sqlalchemy.orm import Session
from datetime import datetime
from app.models import SurveySubmission, SurveyAnswer, Survey, SurveyLink, Group
from app.schemas import SurveyAnswerCreate

def create_submission(db: Session, survey_link_id: int, answers: list[SurveyAnswerCreate]) -> SurveySubmission:
    """Create survey submission with answers"""

    # Create submission
    submission = SurveySubmission(
        survey_link_id=survey_link_id,
        submitted_at=datetime.utcnow()
    )
    db.add(submission)
    db.flush()

    # Get group from survey link
    survey_link = db.query(SurveyLink).filter(SurveyLink.id == survey_link_id).first()

    # Create survey if doesn't exist
    survey = db.query(Survey).filter(Survey.group_id == survey_link.group_id).first()
    if not survey:
        survey = Survey(group_id=survey_link.group_id)
        db.add(survey)
        db.flush()

    # Create answers
    for answer_data in answers:
        answer = SurveyAnswer(
            submission_id=submission.id,
            survey_id=survey.id,
            question_code=answer_data.question_code,
            question_text=answer_data.question_text,
            numeric_value=answer_data.numeric_value,
            text_value=answer_data.text_value
        )
        db.add(answer)

    db.commit()
    db.refresh(submission)

    return submission

def get_group_statistics(db: Session, group_id: int):
    """Calculate statistics for a group"""
    # Get all submissions for this group's links
    links = db.query(SurveyLink).filter(SurveyLink.group_id == group_id).all()
    link_ids = [link.id for link in links]

    if not link_ids:
        return []

    # Get all answers
    answers = db.query(SurveyAnswer).join(SurveySubmission).filter(
        SurveySubmission.survey_link_id.in_(link_ids)
    ).all()

    # Group by question_code
    stats_by_question = {}
    for answer in answers:
        if answer.numeric_value is not None:
            if answer.question_code not in stats_by_question:
                stats_by_question[answer.question_code] = []
            stats_by_question[answer.question_code].append(answer.numeric_value)

    # Calculate statistics
    result = []
    for question_code, values in stats_by_question.items():
        if values:
            result.append({
                "question_code": question_code,
                "average": sum(values) / len(values),
                "count": len(values),
                "min": min(values),
                "max": max(values)
            })

    return result

def get_all_group_statistics(db: Session):
    """Get statistics for all groups"""
    groups = db.query(Group).all()

    result = []
    for group in groups:
        stats = get_group_statistics(db, group.id)
        total_submissions = len(stats[0]['values']) if stats and stats[0].get('values') else 0

        result.append({
            "group_id": group.id,
            "group_name": group.name,
            "faculty": group.faculty,
            "total_submissions": total_submissions,
            "question_stats": stats
        })

    return result
