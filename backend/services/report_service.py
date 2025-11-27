from app.models import Group
from weasyprint import HTML
from jinja2 import Template
import os

def generate_pdf_report(group: Group, statistics: list, total_submissions: int) -> str:
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
            <p><strong>Факультет:</strong> {{ faculty }}</p>
            <p><strong>Курс:</strong> {{ year }}</p>
        </div>

        <h2>Статистика по вопросам</h2>

        {% for stat in statistics %}
        <div class="stats">
            <h3>{{ stat.question_code }}</h3>
            <p><strong>Средний балл:</strong> {{ "%.2f"|format(stat.average) }}</p>
            <p><strong>Количество ответов:</strong> {{ stat.count }}</p>
            <p><strong>Минимум:</strong> {{ stat.min }}</p>
            <p><strong>Максимум:</strong> {{ stat.max }}</p>
        </div>
        {% endfor %}

        <p style="margin-top: 50px; font-size: 12px; color: #6b7280;">
            Отчёт сгенерирован автоматически
        </p>
    </body>
    </html>
    """

    # Render template
    template = Template(html_template)
    html_content = template.render(
        group_name=group.name,
        faculty=group.faculty,
        year=group.year,
        total_submissions=total_submissions,
        statistics=statistics
    )

    # Generate PDF
    pdf_filename = f"/tmp/report_group_{group.id}.pdf"

    try:
        # Create /tmp if it doesn't exist
        os.makedirs('/tmp', exist_ok=True)

        # Generate PDF using WeasyPrint
        HTML(string=html_content).write_pdf(pdf_filename)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # Fallback: save as HTML
        with open(pdf_filename.replace('.pdf', '.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)

    return pdf_filename
