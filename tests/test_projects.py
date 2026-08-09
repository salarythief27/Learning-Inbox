from learning_inbox.extensions import db
from learning_inbox.models import Project, Task


def project_form_data(**overrides):
    data = {
        "name": "Python資格学習",
        "description": "資格取得に向けて学習する",
        "status": "in_progress",
        "target_date": "",
    }
    data.update(overrides)
    return data


def test_create_project(app, logged_in_client, users):
    response = logged_in_client.post("/projects/create", data=project_form_data())

    assert response.status_code == 302
    with app.app_context():
        project = db.session.scalar(
            db.select(Project).where(Project.name == "Python資格学習")
        )
        assert project is not None
        assert project.user_id == users["first_id"]


def test_delete_project_makes_task_unassigned(app, logged_in_client, users):
    with app.app_context():
        project = Project(
            user_id=users["first_id"],
            name="削除対象プロジェクト",
            status="not_started",
        )
        task = Task(
            user_id=users["first_id"],
            project=project,
            title="所属タスク",
            status="not_started",
            priority="none",
        )
        db.session.add_all([project, task])
        db.session.commit()
        project_id, task_id = project.id, task.id

    response = logged_in_client.post(f"/projects/{project_id}/delete")

    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(Project, project_id).is_deleted is True
        assert db.session.get(Task, task_id).project_id is None
