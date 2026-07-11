from flask import Flask
from flask_cors import CORS

from loja.config import Config
from loja.database import init_app as init_database_lifecycle
from loja.database import init_database
from loja.errors import register_error_handlers


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    CORS(app)
    init_database_lifecycle(app)
    register_error_handlers(app)

    from loja.views.order_routes import order_blueprint
    from loja.views.product_routes import product_blueprint
    from loja.views.system_routes import system_blueprint
    from loja.views.user_routes import user_blueprint

    app.register_blueprint(product_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(order_blueprint)
    app.register_blueprint(system_blueprint)

    with app.app_context():
        init_database()

    return app
