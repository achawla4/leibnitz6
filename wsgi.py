# -*- coding: utf-8 -*-
"""
WSGI Entry Point for Gunicorn Web Server Deployment (Render / AWS / Railway)
"""

import os
from leibnitz6_server.server import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5006))
    app.run(host="0.0.0.0", port=port)

