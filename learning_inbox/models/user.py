from flask_login import UserMixin

from learning_inbox.extensions import db
from learning_inbox.models import utc_now


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    projects = db.relationship("Project", back_populates="user")
    tasks = db.relationship("Task", back_populates="user")
    questions = db.relationship("Question", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} login_id={self.login_id!r}>"
