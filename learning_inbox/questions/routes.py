from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from learning_inbox.extensions import db
from learning_inbox.models import Question
from learning_inbox.questions import questions_bp
from learning_inbox.questions.forms import (
    DeleteQuestionForm,
    QUESTION_STATUS_CHOICES,
    QUESTION_STATUS_LABELS,
    QuestionForm,
)


QUESTION_SORT_CHOICES = [
    ("newest", "作成日時が新しい順"),
    ("oldest", "作成日時が古い順"),
    ("updated", "更新日時が新しい順"),
]


def get_owned_question_or_404(question_id):
    question = db.session.scalar(
        db.select(Question).where(
            Question.id == question_id,
            Question.user_id == current_user.id,
            Question.is_deleted.is_(False),
        )
    )
    if question is None:
        abort(404)
    return question


@questions_bp.route("/")
@login_required
def index():
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "")
    category = request.args.get("category", "")
    sort = request.args.get("sort", "newest")

    categories = db.session.scalars(
        db.select(Question.category)
        .where(
            Question.user_id == current_user.id,
            Question.is_deleted.is_(False),
            Question.category.is_not(None),
            Question.category != "",
        )
        .distinct()
        .order_by(Question.category)
    ).all()

    allowed_statuses = {value for value, label in QUESTION_STATUS_CHOICES}
    allowed_sorts = {value for value, label in QUESTION_SORT_CHOICES}

    if len(keyword) > 100:
        abort(400, description="キーワードは100文字以内で指定してください。")
    if status and status not in allowed_statuses:
        abort(400, description="不正な状態が指定されました。")
    if category and category not in categories:
        abort(400, description="不正なカテゴリが指定されました。")
    if sort not in allowed_sorts:
        abort(400, description="不正な並び順が指定されました。")

    statement = db.select(Question).where(
        Question.user_id == current_user.id,
        Question.is_deleted.is_(False),
    )

    if keyword:
        escaped_keyword = (
            keyword.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        keyword_pattern = f"%{escaped_keyword}%"
        statement = statement.where(
            or_(
                Question.title.ilike(keyword_pattern, escape="\\"),
                Question.answer.ilike(keyword_pattern, escape="\\"),
            )
        )

    if status:
        statement = statement.where(Question.status == status)
    if category:
        statement = statement.where(Question.category == category)

    if sort == "oldest":
        statement = statement.order_by(Question.created_at.asc())
    elif sort == "updated":
        statement = statement.order_by(Question.updated_at.desc())
    else:
        statement = statement.order_by(Question.created_at.desc())

    questions = db.session.scalars(statement).all()
    filters = {
        "keyword": keyword,
        "status": status,
        "category": category,
        "sort": sort,
    }

    return render_template(
        "questions/index.html",
        questions=questions,
        categories=categories,
        filters=filters,
        status_choices=QUESTION_STATUS_CHOICES,
        status_labels=QUESTION_STATUS_LABELS,
        sort_choices=QUESTION_SORT_CHOICES,
    )


@questions_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(
            user_id=current_user.id,
            title=form.title.data,
            answer=form.answer.data or None,
            notes=form.notes.data or None,
            category=form.category.data or None,
            status=form.status.data,
        )
        db.session.add(question)
        db.session.commit()
        flash("ギモンを登録しました。", "success")
        return redirect(url_for("questions.detail", question_id=question.id))

    return render_template("questions/create.html", form=form)


@questions_bp.route("/<int:question_id>")
@login_required
def detail(question_id):
    question = get_owned_question_or_404(question_id)
    return render_template(
        "questions/detail.html",
        question=question,
        status_labels=QUESTION_STATUS_LABELS,
        delete_form=DeleteQuestionForm(),
    )


@questions_bp.route("/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
def edit(question_id):
    question = get_owned_question_or_404(question_id)
    form = QuestionForm(obj=question)

    if form.validate_on_submit():
        question.title = form.title.data
        question.answer = form.answer.data or None
        question.notes = form.notes.data or None
        question.category = form.category.data or None
        question.status = form.status.data
        db.session.commit()
        flash("ギモンを更新しました。", "success")
        return redirect(url_for("questions.detail", question_id=question.id))

    return render_template("questions/edit.html", form=form, question=question)


@questions_bp.route("/<int:question_id>/delete", methods=["POST"])
@login_required
def delete(question_id):
    question = get_owned_question_or_404(question_id)
    form = DeleteQuestionForm()
    if not form.validate_on_submit():
        abort(400)

    question.is_deleted = True
    db.session.commit()
    flash("ギモンを削除しました。", "success")
    return redirect(url_for("questions.index"))
