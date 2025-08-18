"""Main application entry point for AI Travel web application.

This module creates and runs the Flask application instance
for the AI-powered travel recommendation system.
"""
from src.backend.create_app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
