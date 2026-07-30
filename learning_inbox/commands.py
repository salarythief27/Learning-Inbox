import click
from werkzeug.security import generate_password_hash

from learning_inbox.extensions import db
from learning_inbox.models import Project, Task, User


def register_commands(app):
    @app.cli.command("init-db")
    def init_db_command():
        """データベースに未作成のテーブルを作成します。"""
        db.create_all()
        click.echo("データベースを初期化しました。")

    @app.cli.command("seed-demo")
    def seed_demo_command():
        """デモユーザーとサンプルデータを登録します。"""
        db.create_all()

        demo_user = db.session.scalar(
            db.select(User).where(User.login_id == "demo")
        )

        if demo_user is None:
            password = click.prompt(
                "デモユーザーのパスワード",
                hide_input=True,
                confirmation_prompt="パスワードを再入力",
            )
            if len(password) < 8:
                raise click.UsageError("パスワードは8文字以上にしてください。")
            if len(password) > 128:
                raise click.UsageError("パスワードは128文字以内にしてください。")

            demo_user = User(
                login_id="demo",
                password_hash=generate_password_hash(password),
            )
            db.session.add(demo_user)
            db.session.flush()
            click.echo("デモユーザーを登録しました。")
        else:
            click.echo("デモユーザーは登録済みです。")

        sql_project = db.session.scalar(
            db.select(Project).where(
                Project.user_id == demo_user.id,
                Project.name == "SQL Silver取得",
            )
        )
        if sql_project is None:
            sql_project = Project(
                user=demo_user,
                name="SQL Silver取得",
                description="SQL Silverの取得に向けた学習を管理します。",
                status="in_progress",
            )
            db.session.add(sql_project)
            db.session.flush()

        python_project = db.session.scalar(
            db.select(Project).where(
                Project.user_id == demo_user.id,
                Project.name == "Python Webアプリ学習",
            )
        )
        if python_project is None:
            python_project = Project(
                user=demo_user,
                name="Python Webアプリ学習",
                description="Flaskを使ったWebアプリ開発の学習を管理します。",
                status="in_progress",
            )
            db.session.add(python_project)
            db.session.flush()

        sample_tasks = [
            {
                "project": sql_project,
                "title": "JOINの種類を復習する",
                "details": "INNER JOINとOUTER JOINの違いを整理します。",
                "category": "SQL",
                "status": "not_started",
                "priority": "high",
            },
            {
                "project": sql_project,
                "title": "模擬問題を30問解く",
                "details": "間違えた問題は理由も記録します。",
                "category": "SQL",
                "status": "not_started",
                "priority": "medium",
            },
            {
                "project": python_project,
                "title": "FlaskのBlueprintについて調べる",
                "details": "機能ごとに処理を分ける仕組みを確認します。",
                "category": "Python",
                "status": "not_started",
                "priority": "medium",
            },
        ]

        for task_data in sample_tasks:
            existing_task = db.session.scalar(
                db.select(Task).where(
                    Task.user_id == demo_user.id,
                    Task.title == task_data["title"],
                )
            )
            if existing_task is None:
                db.session.add(Task(user=demo_user, **task_data))

        db.session.commit()
        click.echo("デモデータを作成しました。")
