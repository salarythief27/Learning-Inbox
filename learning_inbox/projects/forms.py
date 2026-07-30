from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


PROJECT_STATUS_CHOICES = [
    ("not_started", "未着手"),
    ("in_progress", "進行中"),
    ("completed", "完了"),
]

PROJECT_STATUS_LABELS = dict(PROJECT_STATUS_CHOICES)
PROJECT_STATUS_LABELS["active"] = "進行中"


def strip_text(value):
    return value.strip() if value else value


class ProjectForm(FlaskForm):
    name = StringField(
        "プロジェクト名",
        filters=[strip_text],
        validators=[
            DataRequired(message="プロジェクト名を入力してください。"),
            Length(max=100, message="プロジェクト名は100文字以内で入力してください。"),
        ],
    )
    description = TextAreaField(
        "説明",
        filters=[strip_text],
        validators=[
            Optional(),
            Length(max=2000, message="説明は2000文字以内で入力してください。"),
        ],
    )
    status = SelectField(
        "状態",
        choices=PROJECT_STATUS_CHOICES,
        validators=[DataRequired(message="状態を選択してください。")],
    )
    target_date = DateField(
        "目標期限",
        validators=[Optional()],
        format="%Y-%m-%d",
    )
    submit = SubmitField("保存")


class DeleteProjectForm(FlaskForm):
    submit = SubmitField("削除")
