from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from models import Project, db, Binary
import os

project_routes = Blueprint("project_routes", __name__)

@project_routes.route("/projects/create", methods=["GET", "POST"])
def create_project():
    if request.method == "POST":
        name = request.form["name"]
        folder_path = request.form["folder_path"]
        description = request.form.get("description", "")
        
        # Save project to the database
        project = Project(name=name, folder_path=folder_path, description=description)
        db.session.add(project)
        db.session.commit()
        
        # Redirect to the Projects page
        return redirect(url_for("project_routes.list_projects"))
    
    # Render the Create Project form
    return render_template("create_project.html")


@project_routes.route("/projects", methods=["GET"])
def list_projects():
    """List all existing projects."""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects.html", projects=projects)


@project_routes.route("/projects/<int:project_id>", methods=["GET", "POST"])
def get_project_details(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        # Trigger scanning logic
        from scan_folder import scan_folder
        scan_folder(project.folder_path, project_id)
        return redirect(url_for("project_routes.get_project_details", project_id=project.id))

    binaries = [{
        "id": binary.id,
        "name": binary.name,
        "path": binary.path,
        "sha256": binary.sha256,
        "file_type": binary.file_type,
        "strings_count": binary.strings_count,
        "shared_libraries": binary.shared_libraries or []
    } for binary in project.binaries]

    return render_template("details.html", project=project, binaries=binaries)

@project_routes.route("/projects/<int:project_id>/search_strings", methods=["GET"])
def search_strings(project_id):
    query = request.args.get("query", "").lower()

    if not query:
        return jsonify([])  # Return empty if no query provided

    binaries = Binary.query.filter_by(project_id=project_id).all()
    results = []

    for binary in binaries:
        if binary.strings_file:
            try:
                strings_file_path = binary.strings_file
                with open(strings_file_path, "r") as file:
                    strings = file.readlines()
                    matching_strings = [
                        s.strip() for s in strings if query in s.lower()
                    ]
                    if matching_strings:
                        results.append({
                            "binary_id": binary.id,
                            "binary_name": binary.name,
                            "matching_strings": matching_strings,
                        })
            except Exception as e:
                print(f"Error reading strings file for binary {binary.name}: {e}")

    return jsonify(results)