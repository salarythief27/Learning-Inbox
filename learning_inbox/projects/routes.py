from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from learning_inbox.extensions import db
from learning_inbox.models import Project
from learning_inbox.projects import projects_bp
from learning_inbox.projects.forms import (
    DeleteProjectForm,
    PROJECT_STATUS_LABELS,
    ProjectForm,
)


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


def get_active_tasks(project):
    return [
        task
        for task in project.tasks
        if task.user_id == current_user.id and not task.is_deleted
    ]


@projects_bp.route("/")
@login_required
def index():
    projects = db.session.scalars(
        db.select(Project)
        .where(
            Project.user_id == current_user.id,
            Project.is_deleted.is_(False),
        )
        .order_by(Project.created_at.desc())
    ).all()
    project_rows = [
        {
            "project": project,
            "task_count": len(get_active_tasks(project)),
        }
        for project in projects
    ]
    return render_template(
        "projects/index.html",
        project_rows=project_rows,
        status_labels=PROJECT_STATUS_LABELS,
    )


@projects_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            user_id=current_user.id,
            name=form.name.data,
            description=form.description.data or None,
            status=form.status.data,
            target_date=form.target_date.data,
        )
        db.session.add(project)
        db.session.commit()
        flash("プロジェクトを登録しました。", "success")
        return redirect(url_for("projects.detail", project_id=project.id))

    return render_template("projects/create.html", form=form)


@projects_bp.route("/<int:project_id>")
@login_required
def detail(project_id):
    project = get_owned_project_or_404(project_id)
    return render_template(
        "projects/detail.html",
        project=project,
        tasks=get_active_tasks(project),
        status_labels=PROJECT_STATUS_LABELS,
        delete_form=DeleteProjectForm(),
    )


@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit(project_id):
    project = get_owned_project_or_404(project_id)
    form = ProjectForm(obj=project)

    if request.method == "GET" and project.status == "active":
        form.status.data = "in_progress"

    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data or None
        project.status = form.status.data
        project.target_date = form.target_date.data
        db.session.commit()
        flash("プロジェクトを更新しました。", "success")
        return redirect(url_for("projects.detail", project_id=project.id))

    return render_template("projects/edit.html", form=form, project=project)


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
def delete(project_id):
    project = get_owned_project_or_404(project_id)
    form = DeleteProjectForm()
    if not form.validate_on_submit():
        abort(400)

    for task in list(project.tasks):
        if task.user_id == current_user.id:
            task.project = None

    project.is_deleted = True
    db.session.commit()
    flash("プロジェクトを削除しました。所属タスクは削除されていません。", "success")
    return redirect(url_for("projects.index"))
