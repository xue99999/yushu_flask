from flask import Flask
from app.models.base import db
from flask_login import LoginManager
from flask_migrate import Migrate

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.setting')
    app.config.from_object('app.secure')
    register_blueprint(app)

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    login_manager.message = '请登录或者注册'

    db.create_all(app=app)
    return app


def register_blueprint(app):
    from app.web import web
    app.register_blueprint(web)

