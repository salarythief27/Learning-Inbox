from learning_inbox.extensions import db
from learning_inbox.models import utc_now


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    title = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.Text)
    notes = db.Column(db.Text)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), nullable=False, default="unresolved")
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user = db.relationship("User", back_populates="questions")

    def __repr__(self):
        return f"<Question id={self.id} title={self.title!r}>"
