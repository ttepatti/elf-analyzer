#!/usr/bin/python3

from app import create_app
from models import db, Quote

# Quotes to seed
quotes = [
    {"text": "The quieter you become, the more you can hear.", "author": "Anonymous"},
    {"text": "Exploring binaries is like solving a puzzle, byte by byte.", "author": "Unknown Hacker"},
    {"text": "Reverse engineering is an art form.", "author": "Hacker Wisdom"},
    {"text": "Code is read more often than it is written.", "author": "Guido van Rossum"},
    {"text": "The best way to learn is to break things.", "author": "Anonymous"},
]

# Initialize the Flask app and context
app = create_app()
with app.app_context():
    # Ensure the database is initialized
    db.create_all()

    # Seed the quotes
    for quote in quotes:
        existing_quote = Quote.query.filter_by(text=quote["text"]).first()
        if not existing_quote:  # Avoid duplicates
            db.session.add(Quote(text=quote["text"], author=quote["author"]))

    # Commit the changes
    db.session.commit()
    print(f"Seeded {len(quotes)} quotes successfully!")
