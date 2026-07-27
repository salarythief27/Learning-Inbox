from learning_inbox.extensions import db
from learning_inbox.models import utc_now


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    title = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user = db.relationship("User", back_populates="tasks")
    project = db.relationship("Project", back_populates="tasks")

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r}>"
