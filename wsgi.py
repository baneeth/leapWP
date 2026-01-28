"""WSGI entry point for Flask application."""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from leap_ielts.web.app import create_app
    from leap_ielts.utils.config import get_config

    config = get_config()
    app = create_app(config)

    logging.info("Flask application initialized successfully")

except Exception as e:
    logging.error(f"Failed to create Flask application: {e}", exc_info=True)
    # Create a minimal app that shows the error
    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def error():
        return f"<h1>Application Error</h1><p>{str(e)}</p>", 500

if __name__ == "__main__":
    app.run(debug=True)
