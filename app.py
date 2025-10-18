from logging.config import dictConfig

from flask.app import Flask

from blueprints.frasers import frasers_blueprint
# from blueprints.idealo import idealo_blueprint
from config import LOG_CONFIG

dictConfig(config=LOG_CONFIG)


def create_app() -> Flask:
    app: Flask = Flask(import_name=__name__)

    # Register each service blueprint under its own URL prefix
    # app.register_blueprint(blueprint=idealo_blueprint, url_prefix="/idealo")
    app.register_blueprint(blueprint=frasers_blueprint, url_prefix="/frasers")

    return app


if __name__ == "__main__":
    create_app().run()
