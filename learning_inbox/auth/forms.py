from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    login_id = StringField(
        "ログインID",
        validators=[
            DataRequired(message="ログインIDを入力してください。"),
            Length(max=50, message="ログインIDは50文字以内で入力してください。"),
        ],
    )
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(message="パスワードを入力してください。"),
            Length(max=128, message="パスワードは128文字以内で入力してください。"),
        ],
    )
    submit = SubmitField("ログイン")
