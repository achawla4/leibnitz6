# -*- coding: utf-8 -*-
"""
WSGI Entry Point for Gunicorn Web Server Deployment (Render / AWS / Railway)
"""

from leibnitz6_server.server import app

if __name__ == "__main__":
    app.run()
