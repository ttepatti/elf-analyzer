from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    folder_path = db.Column(db.String(1024), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Binary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    path = db.Column(db.String(1024), nullable=False)
    sha256 = db.Column(db.String(64), nullable=False)
    file_type = db.Column(db.String(256))
    strings_file = db.Column(db.Text)  # Stores strings as a text blob
    strings_count = db.Column(db.Integer)
    shared_libraries = db.Column(MutableList.as_mutable(db.PickleType))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    project = db.relationship('Project', backref=db.backref('binaries', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('sha256', 'project_id', name='unique_sha256_per_project'),
    )

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
