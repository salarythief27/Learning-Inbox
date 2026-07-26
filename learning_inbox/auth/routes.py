from flask import render_template

from learning_inbox.auth import auth_bp


@auth_bp.route("/login")
def login():
    return render_template("auth/login.html")
