from learning_inbox.extensions import db
from learning_inbox.models import Task


def task_form_data(**overrides):
    data = {
        "title": "Flaskを復習する",
        "details": "ルーティングを確認する",
        "project_id": "0",
        "category": "Python",
        "status": "not_started",
        "priority": "medium",
        "due_date": "",
        "completed_date": "",
    }
    data.update(overrides)
    return data


def create_task(app, user_id, title="既存タスク"):
    with app.app_context():
        task = Task(
            user_id=user_id,
            title=title,
            status="not_started",
            priority="none",
        )
        db.session.add(task)
        db.session.commit()
        return task.id


def test_create_task(app, logged_in_client, users):
    response = logged_in_client.post("/tasks/create", data=task_form_data())

    assert response.status_code == 302
    with app.app_context():
        task = db.session.scalar(db.select(Task).where(Task.title == "Flaskを復習する"))
        assert task is not None
        assert task.user_id == users["first_id"]


def test_edit_task(app, logged_in_client, users):
    task_id = create_task(app, users["first_id"])

    response = logged_in_client.post(
        f"/tasks/{task_id}/edit",
        data=task_form_data(title="編集後のタスク", status="in_progress"),
    )

    assert response.status_code == 302
    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task.title == "編集後のタスク"
        assert task.status == "in_progress"


def test_logically_delete_task(app, logged_in_client, users):
    task_id = create_task(app, users["first_id"])

    response = logged_in_client.post(f"/tasks/{task_id}/delete")

    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(Task, task_id).is_deleted is True


def test_cannot_access_other_users_task(app, logged_in_client, users):
    task_id = create_task(app, users["second_id"], title="他人のタスク")

    response = logged_in_client.get(f"/tasks/{task_id}")

    assert response.status_code == 404
