from learning_inbox.extensions import db
from learning_inbox.models import utc_now


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False)
    target_date = db.Column(db.Date)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user = db.relationship("User", back_populates="projects")
    tasks = db.relationship(
        "Task",
        back_populates="project",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Project id={self.id} name={self.name!r}>"
