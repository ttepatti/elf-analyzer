from flask import Blueprint, jsonify, render_template, redirect, url_for, send_file, abort
from models import Binary

binary_routes = Blueprint("binary_routes", __name__)

@binary_routes.route("/binary/<int:binary_id>", methods=["GET"])
def get_binary(binary_id):
    """Fetch details for a specific binary."""
    binary = Binary.query.get(binary_id)
    if not binary:
        return jsonify({"error": "Binary not found"}), 404

    # TODO: Fix this, it's still broken/set up for React. Needs to be turned into better version lol.
    return jsonify({
        "id": binary.id,
        "name": binary.name,
        "path": binary.path,
        "sha256": binary.sha256,
        "file_type": binary.file_type,
        "strings_count": binary.strings_count,
        "project_id": binary.project_id,
    })

@binary_routes.route("/binaries/<int:binary_id>", methods=["GET"])
def binary_details(binary_id):
    """Render a detailed view of a single binary."""
    binary = Binary.query.get_or_404(binary_id)

    # Read the strings from the file
    strings = []
    try:
        with open(binary.strings_file, "r") as f:
            strings = f.readlines()
    except Exception as e:
        print(f"Error reading strings file for binary {binary.name}: {e}")

    return render_template(
        "binary_details.html",
        binary=binary,
        strings=strings,
    )

@binary_routes.route("/binaries/<int:binary_id>/strings", methods=["GET"])
def get_binary_strings(binary_id):
    """Serve the strings file for download."""
    binary = Binary.query.get_or_404(binary_id)

    if not binary.strings_file:
        abort(404, description="Strings file not found.")

    try:
        return send_file(binary.strings_file, as_attachment=True)
    except Exception as e:
        abort(500, description=f"Error retrieving strings file: {e}")