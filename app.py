"""Flask application for the Examen 3 de Telemática.

This module defines a simple web service with three routes:

* ``/`` – A basic HTML page presenting the service information.
* ``/health`` – A JSON endpoint for health checks.
* ``/api/info`` – A JSON endpoint describing the project.

The application is designed to run behind a Docker container. When
executed directly (``python app.py``), it will listen on all network
interfaces (``0.0.0.0``) on port ``5000``. In Docker the port can be
mapped to a host port such as ``8080``.

Author: [NOMBRE DEL ESTUDIANTE]
Date: 2026-05-18
"""

from flask import Flask, jsonify, render_template_string


def create_app() -> Flask:
    """Factory function to create and configure the Flask app.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__, static_url_path='/static', static_folder='static')

    @app.route('/')
    def index():
        """Serve the main page.

        Returns:
            str: Rendered HTML string.
        """
        html_template = """
        <!doctype html>
        <html lang="es">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <title>Servicio Telemático Dockerizado</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
          </head>
          <body>
            <div class="container">
              <h1>Servicio Telemático Dockerizado</h1>
              <p class="welcome">¡Bienvenido(a) a la aplicación del Examen 3 de Telemática!</p>
              <p>Este servicio fue desarrollado como parte del examen para demostrar competencias en el
              diseño e implementación de servicios telemáticos utilizando <strong>Python</strong>,
              <strong>Flask</strong>, <strong>Docker</strong>, <strong>GitHub</strong> y <strong>Linux</strong>.</p>
              <p>Estado del servicio: <span class="status">Funcionando</span></p>
              <p>La aplicación se ejecuta dentro de un contenedor Docker y escucha en el puerto <code>5000</code> interno.
              Al publicar el puerto mediante <code>-p 8080:5000</code>, puede accederse desde el navegador mediante
              <code>http://localhost:8080</code> o con la IP pública de la instancia en la nube.</p>
              <h2>Rutas disponibles</h2>
              <ul>
                <li><code>/</code> – Página principal (esta página).</li>
                <li><code>/health</code> – Comprueba el estado del servicio y devuelve JSON.</li>
                <li><code>/api/info</code> – Devuelve información detallada del proyecto en formato JSON.</li>
              </ul>
              <footer>
                <p>Desarrollado para el Examen 3 de Telemática.</p>
              </footer>
            </div>
          </body>
        </html>
        """
        return render_template_string(html_template)

    @app.route('/health')
    def health():
        """Return a JSON object indicating service health.

        Returns:
            flask.Response: JSON response with health status.
        """
        data = {
            "status": "ok",
            "service": "Servicio Telemático Dockerizado",
            "container": "running"
        }
        return jsonify(data)

    @app.route('/api/info')
    def api_info():
        """Return a JSON object with project information.

        Returns:
            flask.Response: JSON response with project metadata.
        """
        data = {
            "project": "Examen 3 - Telemática",
            "description": "Servicio web desplegado mediante contenedores Docker",
            "technology": ["Python", "Flask", "Docker"],
            "version": "1.0.0",
            "author": "[NOMBRE DEL ESTUDIANTE]",
            "status": "active"
        }
        return jsonify(data)

    return app


if __name__ == '__main__':
    # Create the Flask application and run it. When executed inside a Docker
    # container, the host and port are configured so that the container can
    # accept external connections. Debug mode is disabled for production
    # stability.
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)