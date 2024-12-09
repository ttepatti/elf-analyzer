#!/usr/bin/python3

from flask import Flask, render_template
# For setting up and migrating the database
from flask_migrate import Migrate, init, migrate, upgrade
# Importing all of our DB models
from models import db, Project, Quote
# Import func for calling random()
from sqlalchemy.sql import func
# Importing all of our routes
from routes.project_routes import project_routes
from routes.binary_routes import binary_routes
from routes.scan_routes import scan_routes
import os

# App factory method!
def create_app(config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elf_analyzer.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Apply custom configurations if provided
    if config:
        app.config.update(config)

    # Initialize Database
    db.init_app(app)

    # Migrate using Flask-Migrate
    migrate_handler = Migrate(app, db)

    # Automatically handle database migrations
    with app.app_context():
        try:
            # Check if migrations directory exists; if not, initialize it
            if not os.path.exists("migrations"):
                print("Initializing migrations folder...")
                init(directory="migrations")

            # Create a migration script if needed
            print("Checking for model changes...")
            migrate(directory="migrations", message="Auto migration")

            # Apply migrations to update the database schema
            print("Applying migrations...")
            upgrade(directory="migrations")

            print("Database setup completed successfully.")
        except Exception as e:
            print(f"Database setup failed: {e}")

    # Register blueprints
    app.register_blueprint(project_routes)
    app.register_blueprint(binary_routes)
    app.register_blueprint(scan_routes)

    # Define index route here
    @app.route("/")
    def index():
        """Render the main frontend."""
        # Fetch the 5 most recent projects, ordered by creation date
        recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
        # Fetch a random quote for the QOTD
        random_quote = Quote.query.order_by(func.random()).first()

        return render_template("index.html", projects=recent_projects, quote=random_quote)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)