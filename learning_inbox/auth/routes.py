from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from learning_inbox.auth import auth_bp
from learning_inbox.auth.forms import LoginForm
from learning_inbox.extensions import db
from learning_inbox.models import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            db.select(User).where(User.login_id == form.login_id.data)
        )

        if user is not None and check_password_hash(
            user.password_hash,
            form.password.data,
        ):
            login_user(user, remember=False)
            flash("ログインしました。", "success")
            return redirect(url_for("dashboard.index"))

        flash("ログインIDまたはパスワードが正しくありません。", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("ログアウトしました。", "success")
    return redirect(url_for("auth.login"))
