from __future__ import annotations

import logging
import os
from pathlib import Path

from flask import Flask, jsonify, render_template
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from .config import get_settings
from .db import get_engine

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    settings = get_settings()
    app.config["APP_URL"] = settings.app_url

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        try:
            with get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
            return jsonify(status="ok")
        except Exception as exc:
            logger.error("Health check failed: %s", exc)
            return jsonify(status="error", detail=str(exc)), 503

    @app.route("/data")
    def data():
        try:
            with get_engine().connect() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT * FROM priced
                        WHERE model IN ('accord', 'civic', 'camry', 'corolla')
                        ORDER BY delta DESC
                        """
                    )
                )
                rows = [dict(row._mapping) for row in result]
        except ProgrammingError:
            logger.warning("priced table not ready — run scraper then pricer")
            rows = []
        return jsonify(items=rows)

    return app
