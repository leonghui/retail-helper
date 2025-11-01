from http import HTTPStatus
from logging.config import dictConfig

from flask import jsonify
from flask.app import Flask
from flask.wrappers import Response

# from blueprints.idealo import idealo_blueprint
from blueprints.argos import argos_blueprint
from blueprints.frasers import frasers_blueprint
from blueprints.generic import generic_blueprint
from blueprints.joybuy import joybuy_blueprint

from config import LOG_CONFIG

dictConfig(config=LOG_CONFIG)


def create_app() -> Flask:
    app: Flask = Flask(import_name=__name__)

    # Register each service blueprint under its own URL prefix
    # app.register_blueprint(blueprint=idealo_blueprint, url_prefix="/idealo")
    app.register_blueprint(blueprint=argos_blueprint, url_prefix="/argos")
    app.register_blueprint(blueprint=frasers_blueprint, url_prefix="/frasers")
    app.register_blueprint(blueprint=generic_blueprint, url_prefix="/generic")
    app.register_blueprint(blueprint=joybuy_blueprint, url_prefix="/joybuy")

    @app.route(rule="/", methods=["GET"])
    @app.route(rule="/healthcheck", methods=["GET"])
    def healthcheck() -> tuple[Response, int]:
        return jsonify({"status": "ok"}), HTTPStatus.OK

    return app


if __name__ == "__main__":
    app: Flask = create_app()
    app.run(host="0.0.0.0", port=5000, use_reloader=False)
