import os
from state import folder_scan_progress, binary_analysis_progress
from utils import calculate_sha256, extract_strings, determine_file_type, extract_shared_libraries

def scan_folder(folder_path, project_id):
    """
    Scan a folder and its subdirectories for ELF binaries.
    Updates the folder scanning progress state and prepares binaries for analysis.
    """
    folder_scan_progress["status"] = "in_progress"
    folder_scan_progress["progress"] = 0
    folder_scan_progress["total"] = 0

    binaries = []  # List to store discovered binaries
    folders_to_scan = []

    # Count all subdirectories for progress tracking
    for root, dirs, files in os.walk(folder_path):
        folders_to_scan.append(root)
    folder_scan_progress["total"] = len(folders_to_scan)

    # Perform the actual folder scan
    for folder_index, folder in enumerate(folders_to_scan, start=1):
        print(f"Scanning folder: {folder} ({folder_index}/{folder_scan_progress['total']})")

        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)

            # Check if the file is a binary
            try:
                if is_elf_binary(file_path):
                    binaries.append(file_path)
            except PermissionError:
                print(f"Permission denied: {file_path}")
            except FileNotFoundError:
                print(f"File not found (possibly a broken link): {file_path}")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

        # Update scanning progress
        folder_scan_progress["progress"] = folder_index

    # Mark folder scanning as complete
    folder_scan_progress["status"] = "complete"

    # Start analyzing the discovered binaries
    analyze_binaries(binaries, project_id)


def is_elf_binary(file_path):
    """
    Determine if a file is an ELF binary.
    This uses the file's magic number (first few bytes of the file).
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            return header == b"\x7fELF"
    except PermissionError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"Unknown error while checking ELF binary: {e}")


def analyze_binaries(binaries, project_id):
    """Analyze a list of ELF binaries."""

    binary_analysis_progress["status"] = "in_progress"
    binary_analysis_progress["progress"] = 0
    binary_analysis_progress["total"] = len(binaries)

    for index, binary in enumerate(binaries, start=1):
        # Extract strings and output to vars
        strings_file, strings_count = extract_strings(binary)

        results = {
            "sha256": calculate_sha256(binary),
            "strings_file": strings_file,
            "strings_count": strings_count,
            "file_type": determine_file_type(binary),
            "shared_libraries": extract_shared_libraries(binary)
        }

        save_binary_analysis_results(binary, project_id, results)

        binary_analysis_progress["progress"] = index

    # Mark binary analysis as complete
    binary_analysis_progress["status"] = "complete"


def save_binary_analysis_results(binary_path, project_id, results):
    """Save the analysis results to the database, avoiding duplicates."""
    from models import Binary, db

    # Check for existing binary with the same SHA256 within the current project
    existing_binary = Binary.query.filter_by(sha256=results["sha256"], project_id=project_id).first()

    # TODO: This has a weird edge case: what if we have the exact same binary 
    # located in multiple folders in our scanned directories?
    # Current behavior means the file path will be overwritten each time it is
    # discovered, so only one file path will be visible at the end... 
    # Should probably address this and list all uniquely-discovered file paths!

    if existing_binary:
        print(f"Binary with SHA256 {results['sha256']} already exists in project {project_id}. Updating entry.")
        existing_binary.name = binary_path.split("/")[-1]
        existing_binary.path = binary_path
        existing_binary.file_type = results["file_type"]
        existing_binary.strings_file = results["strings_file"]
        existing_binary.strings_count = results["strings_count"]
        existing_binary.shared_libraries = results["shared_libraries"]
        db.session.commit()
        return

    # If no existing binary, create a new entry
    binary = Binary(
        name = binary_path.split("/")[-1],
        path = binary_path,
        sha256 = results["sha256"],
        file_type = results["file_type"],
        strings_file = results["strings_file"],
        strings_count = results["strings_count"],
        shared_libraries = results["shared_libraries"],
        project_id = project_id
    )
    db.session.add(binary)
    db.session.commit()