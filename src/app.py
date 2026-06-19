import logging
import os
from pathlib import Path

from flask import Flask, jsonify, render_template
from sqlalchemy import text

from .db import get_engine

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config["APP_URL"] = os.environ.get("APP_URL", "")

    logging.basicConfig(level=logging.INFO)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/data")
    def data():
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT * FROM priced
                    WHERE date IN (
                        SELECT date FROM priced
                        WHERE model IN ('accord', 'civic', 'camry', 'corolla')
                        ORDER BY date
                    )
                    ORDER BY delta DESC
                    """
                )
            )
            rows = [dict(row._mapping) for row in result]
        return jsonify(items=rows)

    return app
