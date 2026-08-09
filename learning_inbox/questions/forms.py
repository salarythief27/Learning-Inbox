from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


QUESTION_STATUS_CHOICES = [
    ("unresolved", "未解決"),
    ("resolved", "解決済み"),
]

QUESTION_STATUS_LABELS = dict(QUESTION_STATUS_CHOICES)


def strip_text(value):
    return value.strip() if value else value


class QuestionForm(FlaskForm):
    title = StringField(
        "タイトル",
        filters=[strip_text],
        validators=[
            DataRequired(message="タイトルを入力してください。"),
            Length(max=200, message="タイトルは200文字以内で入力してください。"),
        ],
    )
    answer = TextAreaField(
        "回答",
        filters=[strip_text],
        validators=[
            Length(max=5000, message="回答は5000文字以内で入力してください。"),
        ],
    )
    notes = TextAreaField(
        "補足メモ",
        filters=[strip_text],
        validators=[
            Optional(),
            Length(max=5000, message="補足メモは5000文字以内で入力してください。"),
        ],
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
        choices=QUESTION_STATUS_CHOICES,
        default="unresolved",
        validators=[DataRequired(message="状態を選択してください。")],
    )
    submit = SubmitField("保存")

    def validate_answer(self, field):
        if self.status.data == "resolved" and not field.data:
            raise ValidationError("解決済みにする場合は回答を入力してください。")


class DeleteQuestionForm(FlaskForm):
    submit = SubmitField("削除")
