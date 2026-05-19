"""Flask application for the Examen 3 de Telemática.

This module defines a web service with:

* ``/`` – Main page with embedded Tetris game (JavaScript/Canvas).
* ``/health`` – JSON health check endpoint.
* ``/api/info`` – JSON project metadata endpoint.

The application listens on ``0.0.0.0:5000`` inside Docker; map host port 8080 with
``-p 8080:5000`` to access from the browser.

Author: Juan Sebastián Quintero Hwernández
Date: 2026-05-18
"""

from flask import Flask, jsonify, render_template


def create_app() -> Flask:
    """Factory function to create and configure the Flask app.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__, static_url_path='/static', static_folder='static')

    @app.route('/')
    def index():
        """Serve the main page with the Tetris web game."""
        return render_template('index.html')

    @app.route('/health')
    def health():
        """Return a JSON object indicating service health."""
        return jsonify({
            "status": "ok",
            "service": "Servicio Telemático Dockerizado",
            "container": "running",
            "game": "tetris-web",
        })

    @app.route('/api/info')
    def api_info():
        """Return a JSON object with project information."""
        return jsonify({
            "project": "Examen 3 - Telemática",
            "description": (
                "Servicio web telemático con Tetris en el navegador, "
                "desplegado mediante contenedores Docker"
            ),
            "technology": ["Python", "Flask", "Docker", "JavaScript", "HTML5 Canvas"],
            "version": "2.0.0",
            "author": "Juan Sebastián Quintero Hwernández",
            "status": "active",
            "features": [
                "Tetris web interactivo",
                "Temas visuales (clásico, oscuro, neon, retro)",
                "Modos Clásico, Maratón y Zen",
                "Hold, pieza fantasma y récord local",
            ],
            "routes": {
                "/": "Página principal con juego",
                "/health": "Estado del servicio",
                "/api/info": "Metadatos del proyecto",
            },
            "game": "static/tetris/ (JavaScript + Canvas)",
        })

    return app


# Gunicorn importa ``app:app``; en desarrollo local se usa ``python app.py``
app = create_app()

if __name__ == '__main__':
    # Servidor de desarrollo Flask (solo local). En Docker se usa Gunicorn.
    app.run(host='0.0.0.0', port=5000, debug=False)
