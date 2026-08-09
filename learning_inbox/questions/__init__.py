from flask import Blueprint


questions_bp = Blueprint(
    "questions",
    __name__,
    url_prefix="/questions",
    template_folder="templates",
)

from learning_inbox.questions import routes
