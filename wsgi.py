"""WSGI entry point for Flask application."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from leap_ielts.web.app import create_app
from leap_ielts.utils.config import get_config

config = get_config()
app = create_app(config)

if __name__ == "__main__":
    app.run(debug=True)
