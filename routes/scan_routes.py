from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from scan_folder import scan_folder
from state import folder_scan_progress, binary_analysis_progress
from models import Project
import os

scan_routes = Blueprint("scan_routes", __name__)

@scan_routes.route("/start-scan", methods=["POST"])
def start_scan():
    # Read data from form submission
    project_id = request.form.get("project_id")
    folder_path = request.form.get("folder_path")

    if not project_id or not folder_path:
        flash("Invalid project or folder path.")
        return redirect(url_for("project_routes.list_projects"))

    # Start the scan
    scan_folder(folder_path, project_id)

    # Redirect to Progress page
    return redirect(url_for("scan_routes.show_progress", project_id=project_id))


@scan_routes.route("/progress/<int:project_id>", methods=["GET"])
def show_progress(project_id):
    """Render the Progress page with navigation options."""
    return render_template("progress.html", project_id=project_id)

@scan_routes.route("/progress/folder-scan", methods=["GET"])
def get_folder_scan_progress():
    """Return folder scanning progress as JSON."""
    return jsonify({
        "status": folder_scan_progress["status"],
        "progress": folder_scan_progress["progress"],
        "total": folder_scan_progress["total"],
    })


@scan_routes.route("/progress/binary-analysis", methods=["GET"])
def get_binary_analysis_progress():
    """Fetch the progress of binary analysis as JSON."""
    return jsonify({
        "status": binary_analysis_progress["status"],
        "progress": binary_analysis_progress["progress"],
        "total": binary_analysis_progress["total"],
    })