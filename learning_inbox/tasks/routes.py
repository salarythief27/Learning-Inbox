from datetime import date

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from learning_inbox.extensions import db
from learning_inbox.models import Project, Task
from learning_inbox.tasks import tasks_bp
from learning_inbox.tasks.forms import (
    DeleteTaskForm,
    TASK_PRIORITY_LABELS,
    TASK_STATUS_CHOICES,
    TASK_STATUS_LABELS,
    TaskForm,
)

TASK_SORT_CHOICES = [
    ("newest", "作成日時が新しい順"),
    ("oldest", "作成日時が古い順"),
    ("due_date", "期限が近い順"),
]


def get_owned_task_or_404(task_id):
    task = db.session.scalar(
        db.select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id,
            Task.is_deleted.is_(False),
        )
    )
    if task is None:
        abort(404)
    return task


def get_owned_project_or_404(project_id):
    project = db.session.scalar(
        db.select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
            Project.is_deleted.is_(False),
        )
    )
    if project is None:
        abort(404)
    return project


def set_project_choices(form):
    projects = db.session.scalars(
        db.select(Project)
        .where(
            Project.user_id == current_user.id,
            Project.is_deleted.is_(False),
        )
        .order_by(Project.name)
    ).all()
    form.project_id.choices = [(0, "所属なし")] + [
        (project.id, project.name) for project in projects
    ]


def set_completed_date(task, status, completed_date):
    if status == "completed":
        task.completed_date = completed_date or date.today()
    else:
        task.completed_date = None


@tasks_bp.route("/")
@login_required
def index():
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "")
    project_value = request.args.get("project", "")
    category = request.args.get("category", "")
    show_completed_value = request.args.get("show_completed", "")
    sort = request.args.get("sort", "newest")

    projects = db.session.scalars(
        db.select(Project)
        .where(
            Project.user_id == current_user.id,
            Project.is_deleted.is_(False),
        )
        .order_by(Project.name)
    ).all()
    categories = db.session.scalars(
        db.select(Task.category)
        .where(
            Task.user_id == current_user.id,
            Task.is_deleted.is_(False),
            Task.category.is_not(None),
            Task.category != "",
        )
        .distinct()
        .order_by(Task.category)
    ).all()

    allowed_statuses = {value for value, label in TASK_STATUS_CHOICES}
    allowed_sorts = {value for value, label in TASK_SORT_CHOICES}
    allowed_project_ids = {project.id for project in projects}

    if len(keyword) > 100:
        abort(400, description="キーワードは100文字以内で指定してください。")
    if status and status not in allowed_statuses:
        abort(400, description="不正な状態が指定されました。")
    if category and category not in categories:
        abort(400, description="不正なカテゴリが指定されました。")
    if show_completed_value not in {"", "1"}:
        abort(400, description="完了済みタスクの表示条件が不正です。")
    if sort not in allowed_sorts:
        abort(400, description="不正な並び順が指定されました。")

    selected_project_id = None
    if project_value not in {"", "none"}:
        try:
            selected_project_id = int(project_value)
        except ValueError:
            abort(400, description="不正なプロジェクトが指定されました。")
        if selected_project_id not in allowed_project_ids:
            abort(400, description="不正なプロジェクトが指定されました。")
        project_value = str(selected_project_id)

    statement = db.select(Task).where(
        Task.user_id == current_user.id,
        Task.is_deleted.is_(False),
    )

    if keyword:
        escaped_keyword = (
            keyword.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        keyword_pattern = f"%{escaped_keyword}%"
        statement = statement.where(
            or_(
                Task.title.ilike(keyword_pattern, escape="\\"),
                Task.details.ilike(keyword_pattern, escape="\\"),
            )
        )

    if status:
        if status == "not_started":
            statement = statement.where(Task.status.in_(["not_started", "todo"]))
        else:
            statement = statement.where(Task.status == status)

    show_completed = show_completed_value == "1"
    if not show_completed and status != "completed":
        statement = statement.where(Task.status != "completed")

    if project_value == "none":
        statement = statement.where(Task.project_id.is_(None))
    elif selected_project_id is not None:
        statement = statement.where(Task.project_id == selected_project_id)

    if category:
        statement = statement.where(Task.category == category)

    if sort == "oldest":
        statement = statement.order_by(Task.created_at.asc())
    elif sort == "due_date":
        statement = statement.order_by(
            Task.due_date.is_(None).asc(),
            Task.due_date.asc(),
            Task.created_at.desc(),
        )
    else:
        statement = statement.order_by(Task.created_at.desc())

    tasks = db.session.scalars(statement).all()
    filters = {
        "keyword": keyword,
        "status": status,
        "project": project_value,
        "category": category,
        "show_completed": show_completed,
        "sort": sort,
    }

    return render_template(
        "tasks/index.html",
        tasks=tasks,
        projects=projects,
        categories=categories,
        filters=filters,
        status_choices=TASK_STATUS_CHOICES,
        sort_choices=TASK_SORT_CHOICES,
        status_labels=TASK_STATUS_LABELS,
        priority_labels=TASK_PRIORITY_LABELS,
    )


@tasks_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = TaskForm()
    set_project_choices(form)

    query_project_id = request.args.get("project_id", type=int)
    if request.method == "GET" and "project_id" in request.args:
        if query_project_id is None:
            abort(404)
        get_owned_project_or_404(query_project_id)
        form.project_id.data = query_project_id

    if form.validate_on_submit():
        project_id = None
        if form.project_id.data != 0:
            project_id = get_owned_project_or_404(form.project_id.data).id

        task = Task(
            user_id=current_user.id,
            project_id=project_id,
            title=form.title.data,
            details=form.details.data or None,
            category=form.category.data or None,
            status=form.status.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
        )
        set_completed_date(task, form.status.data, form.completed_date.data)
        db.session.add(task)
        db.session.commit()
        flash("タスクを登録しました。", "success")
        return redirect(url_for("tasks.detail", task_id=task.id))

    return render_template("tasks/create.html", form=form)


@tasks_bp.route("/<int:task_id>")
@login_required
def detail(task_id):
    task = get_owned_task_or_404(task_id)
    return render_template(
        "tasks/detail.html",
        task=task,
        status_labels=TASK_STATUS_LABELS,
        priority_labels=TASK_PRIORITY_LABELS,
        delete_form=DeleteTaskForm(),
    )


@tasks_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit(task_id):
    task = get_owned_task_or_404(task_id)
    form = TaskForm(obj=task)
    set_project_choices(form)

    if request.method == "GET":
        if task.project_id is None:
            form.project_id.data = 0
        if task.status == "todo":
            form.status.data = "not_started"

    if form.validate_on_submit():
        project_id = None
        if form.project_id.data != 0:
            project_id = get_owned_project_or_404(form.project_id.data).id

        task.project_id = project_id
        task.title = form.title.data
        task.details = form.details.data or None
        task.category = form.category.data or None
        task.status = form.status.data
        task.priority = form.priority.data
        task.due_date = form.due_date.data
        set_completed_date(task, form.status.data, form.completed_date.data)
        db.session.commit()
        flash("タスクを更新しました。", "success")
        return redirect(url_for("tasks.detail", task_id=task.id))

    return render_template("tasks/edit.html", form=form, task=task)


@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete(task_id):
    task = get_owned_task_or_404(task_id)
    form = DeleteTaskForm()
    if not form.validate_on_submit():
        abort(400)

    task.is_deleted = True
    db.session.commit()
    flash("タスクを削除しました。", "success")
    return redirect(url_for("tasks.index"))
