from flask import Blueprint


tasks_bp = Blueprint(
    "tasks",
    __name__,
    url_prefix="/tasks",
    template_folder="templates",
)

from learning_inbox.tasks import routes
