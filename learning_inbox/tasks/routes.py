from flask import abort, render_template, request
from flask_login import current_user, login_required

from learning_inbox.extensions import db
from learning_inbox.models import Project
from learning_inbox.tasks import tasks_bp


@tasks_bp.route("/")
@login_required
def index():
    return render_template("tasks/index.html")


@tasks_bp.route("/create")
@login_required
def create():
    project = None
    project_id = request.args.get("project_id", type=int)
    if project_id is not None:
        project = db.session.scalar(
            db.select(Project).where(
                Project.id == project_id,
                Project.user_id == current_user.id,
                Project.is_deleted.is_(False),
            )
        )
        if project is None:
            abort(404)

    return render_template("tasks/create.html", project=project)
