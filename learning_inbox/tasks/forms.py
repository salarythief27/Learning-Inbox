from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


TASK_STATUS_CHOICES = [
    ("not_started", "未着手"),
    ("in_progress", "学習中"),
    ("completed", "完了"),
]

TASK_STATUS_LABELS = dict(TASK_STATUS_CHOICES)
TASK_STATUS_LABELS["todo"] = "未着手"

TASK_PRIORITY_CHOICES = [
    ("none", "未指定"),
    ("low", "低"),
    ("medium", "中"),
    ("high", "高"),
]

TASK_PRIORITY_LABELS = dict(TASK_PRIORITY_CHOICES)


def strip_text(value):
    return value.strip() if value else value


class TaskForm(FlaskForm):
    title = StringField(
        "タイトル",
        filters=[strip_text],
        validators=[
            DataRequired(message="タイトルを入力してください。"),
            Length(max=200, message="タイトルは200文字以内で入力してください。"),
        ],
    )
    details = TextAreaField(
        "詳細・メモ",
        filters=[strip_text],
        validators=[
            Optional(),
            Length(max=5000, message="詳細・メモは5000文字以内で入力してください。"),
        ],
    )
    project_id = SelectField(
        "プロジェクト",
        choices=[],
        coerce=int,
        validate_choice=False,
    )
    category = StringField(
        "カテゴリ",
        filters=[strip_text],
        validators=[
            Optional(),
            Length(max=50, message="カテゴリは50文字以内で入力してください。"),
        ],
    )
    status = SelectField(
        "状態",
        choices=TASK_STATUS_CHOICES,
        validators=[DataRequired(message="状態を選択してください。")],
    )
    priority = SelectField(
        "優先度",
        choices=TASK_PRIORITY_CHOICES,
        validators=[DataRequired(message="優先度を選択してください。")],
    )
    due_date = DateField(
        "期限",
        validators=[Optional()],
        format="%Y-%m-%d",
    )
    completed_date = DateField(
        "完了日",
        validators=[Optional()],
        format="%Y-%m-%d",
    )
    submit = SubmitField("保存")

    def validate_project_id(self, field):
        allowed_project_ids = {value for value, label in field.choices}
        if field.data not in allowed_project_ids:
            raise ValidationError("選択したプロジェクトは利用できません。")


class DeleteTaskForm(FlaskForm):
    submit = SubmitField("削除")
