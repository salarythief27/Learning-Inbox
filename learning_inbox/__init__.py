from pathlib import Path

from flask import Flask, redirect, url_for

from learning_inbox.commands import register_commands
from learning_inbox.config import Config
from learning_inbox.extensions import csrf, db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEYが設定されていません。")

    # SQLiteファイルを置くinstanceフォルダを作成します。
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # create_all()がモデルを認識できるように読み込みます。
    from learning_inbox import models

    from learning_inbox.auth import auth_bp
    from learning_inbox.dashboard import dashboard_bp
    from learning_inbox.projects import projects_bp
    from learning_inbox.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(dashboard_bp)
    register_commands(app)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app
