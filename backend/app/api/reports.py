from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from jinja2 import Template

from core.database import get_db
from app.models import Group, SurveyLink, SurveySubmission, SurveyAnswer
from services.survey_service import get_group_statistics

# Словарь перевода показателей на русский язык
QUESTION_LABELS = {
    'comfort': 'Комфорт',
    'engagement': 'Вовлеченность',
    'conflicts': 'Конфликтность',
    'stress': 'Стресс',
    'support': 'Поддержка',
    'open_feedback': 'Ваши дополнительные комментарии и предложения',
    'adaptation': 'Адаптация',
    'satisfaction': 'Удовлетворенность',
    'motivation': 'Мотивация'
}

router = APIRouter()

@router.get("/group/{group_id}/report")
async def generate_group_pdf_report(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Generate PDF report for a group (returns HTML as fallback)"""
    # Verify group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Get statistics
    stats = get_group_statistics(db, group_id)

    # Добавляем русские названия показателей
    for stat in stats:
        stat['question_label'] = QUESTION_LABELS.get(stat['question_code'], stat['question_code'])
    # Get submission count (and link ids) — needed for fetching open answers below
    links = db.query(SurveyLink).filter(SurveyLink.group_id == group_id).all()
    link_ids = [link.id for link in links]
    total_submissions = db.query(SurveySubmission).filter(
        SurveySubmission.survey_link_id.in_(link_ids)
    ).count()

    # Get open (text) answers for report
    open_answers = db.query(SurveyAnswer).join(SurveySubmission).filter(
        SurveySubmission.survey_link_id.in_(link_ids),
        SurveyAnswer.text_value.isnot(None)
    ).order_by(SurveyAnswer.created_at.desc()).all()

    open_answers_list = []
    for ans in open_answers:
        open_answers_list.append({
            'question_code': ans.question_code,
            'question_label': QUESTION_LABELS.get(ans.question_code, ans.question_code),
            'text_value': ans.text_value,
            'submitted_at': ans.created_at
        })

    # Generate HTML report (PDF requires system libraries)
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Отчёт - {{ group_name }}</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h1 { color: #2563eb; }
            h2 { color: #1e40af; margin-top: 30px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #2563eb; color: white; }
            .stats { margin: 15px 0; padding: 10px; background-color: #f3f4f6; }
        </style>
    </head>
    <body>
        <h1>Отчёт по социально-психологическому климату</h1>
        <h2>{{ group_name }}</h2>

        <div class="stats">
            <p><strong>Всего ответов:</strong> {{ total_submissions }}</p>
            <p><strong>Факультет:</strong> {{ group.faculty.name if group.faculty else 'Не указан' }}</p>
            <p><strong>Курс:</strong> {{ group.year }}</p>
        </div>

        <h2>Статистика по вопросам</h2>

        {% for stat in statistics %}
        <div class="stats">
            <h3>{{ stat.question_label }}</h3>
                {% if stat.average is defined and stat.average is not none %}
                <p><strong>Средний балл:</strong> {{ "%.2f"|format(stat.average) }}</p>
                <p><strong>Количество ответов:</strong> {{ stat.count }}</p>
                <p><strong>Минимум:</strong> {{ stat.min }}</p>
                <p><strong>Максимум:</strong> {{ stat.max }}</p>
                {% else %}
                <p><strong>Количество ответов (текстовых):</strong> {{ stat.count }}</p>
                {% endif %}
        </div>
        {% endfor %}

        <h2>Текстовые ответы</h2>
        {% for ans in open_answers %}
        <div class="stats">
            <h3>{{ ans.question_label }}</h3>
            <p>{{ ans.text_value }}</p>
            <p class="text-sm text-gray-500">{{ ans.submitted_at }}</p>
        </div>
        {% endfor %}
    </body>
    </html>
    """

    template = Template(html_template)
    html_content = template.render(
        group_name=group.name,
        group=group,
        total_submissions=total_submissions,
        statistics=stats,
        open_answers=open_answers_list
    )

    return HTMLResponse(content=html_content)
