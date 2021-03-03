from flask import Flask

def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():
        # Import parts of our core Flask app
        import routes

        # Import Dash application
        from dashboards.dashboard_stocks_analysis import create_dashboard_stocks_analysis
        app = create_dashboard_stocks_analysis(app)

        return app
