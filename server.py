from flask import Flask, jsonify
from logging.config import dictConfig
import chai

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(process)d][%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


app = Flask(__name__)


chai.flask_setup(app)


@app.route("/")
def hello():
    return "hello"


@app.route("/config")
def config():
    return jsonify(chai.get_config("connect_client", dict(error="CONFIG NOT FOUND")))


if __name__ == "__main__":
    app.run()
