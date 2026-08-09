from learning_inbox.extensions import db
from learning_inbox.models import Question


def question_form_data(**overrides):
    data = {
        "title": "Flaskのsessionとは何か",
        "answer": "",
        "notes": "",
        "category": "Flask",
        "status": "unresolved",
    }
    data.update(overrides)
    return data


def create_question(app, user_id, title="既存のギモン"):
    with app.app_context():
        question = Question(
            user_id=user_id,
            title=title,
            status="unresolved",
        )
        db.session.add(question)
        db.session.commit()
        return question.id


def test_create_question_with_title_only(app, logged_in_client, users):
    response = logged_in_client.post("/questions/new", data=question_form_data())

    assert response.status_code == 302
    with app.app_context():
        question = db.session.scalar(
            db.select(Question).where(Question.title == "Flaskのsessionとは何か")
        )
        assert question is not None
        assert question.answer is None
        assert question.status == "unresolved"


def test_add_answer_and_resolve_question(app, logged_in_client, users):
    question_id = create_question(app, users["first_id"])

    response = logged_in_client.post(
        f"/questions/{question_id}/edit",
        data=question_form_data(
            title="既存のギモン",
            answer="署名付きCookieに保存される",
            status="resolved",
        ),
    )

    assert response.status_code == 302
    with app.app_context():
        question = db.session.get(Question, question_id)
        assert question.answer == "署名付きCookieに保存される"
        assert question.status == "resolved"


def test_cannot_resolve_question_without_answer(app, logged_in_client, users):
    question_id = create_question(app, users["first_id"])

    response = logged_in_client.post(
        f"/questions/{question_id}/edit",
        data=question_form_data(title="既存のギモン", status="resolved"),
    )

    assert response.status_code == 200
    assert "解決済みにする場合は回答を入力してください。" in response.get_data(
        as_text=True
    )
    with app.app_context():
        assert db.session.get(Question, question_id).status == "unresolved"


def test_cannot_access_other_users_question(app, logged_in_client, users):
    question_id = create_question(
        app,
        users["second_id"],
        title="他人のギモン",
    )

    response = logged_in_client.get(f"/questions/{question_id}")

    assert response.status_code == 404


def test_logically_delete_question(app, logged_in_client, users):
    question_id = create_question(app, users["first_id"])

    response = logged_in_client.post(f"/questions/{question_id}/delete")

    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(Question, question_id).is_deleted is True
