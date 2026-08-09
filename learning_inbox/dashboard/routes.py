from datetime import date

from flask import render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from learning_inbox.dashboard import dashboard_bp
from learning_inbox.extensions import db
from learning_inbox.models import Project, Question, Task
from learning_inbox.questions.forms import QUESTION_STATUS_LABELS
from learning_inbox.tasks.forms import TASK_STATUS_LABELS


def count_tasks(*additional_conditions):
    return db.session.scalar(
        db.select(func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.is_deleted.is_(False),
            *additional_conditions,
        )
    )


@dashboard_bp.route("/")
@login_required
def index():
    counts = {
        "all_tasks": count_tasks(),
        "not_started": count_tasks(Task.status.in_(["not_started", "todo"])),
        "in_progress": count_tasks(Task.status == "in_progress"),
        "completed": count_tasks(Task.status == "completed"),
        "overdue": count_tasks(
            Task.due_date < date.today(),
            Task.status != "completed",
        ),
        "active_projects": db.session.scalar(
            db.select(func.count(Project.id)).where(
                Project.user_id == current_user.id,
                Project.is_deleted.is_(False),
                Project.status.in_(["in_progress", "active"]),
            )
        ),
        "unresolved_questions": db.session.scalar(
            db.select(func.count(Question.id)).where(
                Question.user_id == current_user.id,
                Question.is_deleted.is_(False),
                Question.status == "unresolved",
            )
        ),
    }

    recent_tasks = db.session.scalars(
        db.select(Task)
        .where(
            Task.user_id == current_user.id,
            Task.is_deleted.is_(False),
        )
        .order_by(Task.created_at.desc())
        .limit(5)
    ).all()
    recent_items = [
        {
            "type_label": "タスク",
            "title": task.title,
            "status_label": TASK_STATUS_LABELS.get(task.status, task.status),
            "created_at": task.created_at,
            "url": url_for("tasks.detail", task_id=task.id),
        }
        for task in recent_tasks
    ]

    recent_questions = db.session.scalars(
        db.select(Question)
        .where(
            Question.user_id == current_user.id,
            Question.is_deleted.is_(False),
        )
        .order_by(Question.updated_at.desc())
        .limit(5)
    ).all()

    return render_template(
        "dashboard/index.html",
        counts=counts,
        recent_items=recent_items,
        recent_questions=recent_questions,
        question_status_labels=QUESTION_STATUS_LABELS,
    )
