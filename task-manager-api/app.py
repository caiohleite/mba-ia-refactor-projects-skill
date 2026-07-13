from flask import Flask
from flask_cors import CORS

from config import Config
from database import db
from middlewares.error_handler import register_error_handlers
from routes import category_bp, report_bp, task_bp, user_bp
from utils.time import utc_now


def create_app(config_overrides=None):
    application = Flask(__name__)
    application.config.from_object(Config)
    if config_overrides:
        application.config.update(config_overrides)

    CORS(application)
    db.init_app(application)
    register_error_handlers(application)

    application.register_blueprint(task_bp)
    application.register_blueprint(user_bp)
    application.register_blueprint(report_bp)
    application.register_blueprint(category_bp)

    @application.get("/health")
    def health():
        return {"status": "ok", "timestamp": str(utc_now())}

    @application.get("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    with application.app_context():
        db.create_all()

    return application


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["HOST"],
        port=app.config["PORT"],
    )
