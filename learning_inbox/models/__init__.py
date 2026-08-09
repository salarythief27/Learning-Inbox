from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)


from learning_inbox.models.project import Project
from learning_inbox.models.question import Question
from learning_inbox.models.task import Task
from learning_inbox.models.user import User

__all__ = ["Project", "Question", "Task", "User"]
