import hashlib
import subprocess
import os
import re

def calculate_sha256(binary_path):
    """Calculate the SHA256 hash of a binary."""
    sha256 = hashlib.sha256()
    with open(binary_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_strings(binary_path, output_dir="strings_dumps"):
    """
    Extract strings from a binary and save them to a file.

    Args:
        binary_path (str): Path to the binary file.
        output_dir (str): Directory to save the strings file.

    Returns:
        tuple: (strings_file_path, strings_count)
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # File path for the strings output
    strings_file = os.path.join(output_dir, f"{os.path.basename(binary_path)}.strings")

    try:
        # Run the `strings` command
        result = subprocess.run(
            ["strings", binary_path],
            capture_output=True,
            text=True,
            check=True
        )

        # Write the strings to the file
        strings = result.stdout.splitlines()
        with open(strings_file, "w") as f:
            f.write("\n".join(strings))

        return strings_file, len(strings)

    except Exception as e:
        print(f"Error extracting strings from {binary_path}: {e}")
        return None, 0


def determine_file_type(binary_path):
    """Determine the file type using the 'file' command."""
    try:
        result = subprocess.run(["file", binary_path], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error determining file type: {e}")
        return "Unknown"

def extract_shared_libraries(binary_path):
    """Extract shared libraries using the 'readelf' command."""
    try:
        result = subprocess.run(["readelf", "-d", binary_path], capture_output=True, text=True, check=True)
        libraries = []
        for line in result.stdout.splitlines():
            if "Shared library:" in line:  # Match lines showing shared libraries
                # Use re.search() to get everything between the [ ] characters
                libraries.append(re.search('\[(.*)\]', line).group(1))
        return libraries
    except Exception as e:
        print(f"Error extracting shared libraries for {binary_path}: {e}")
        return []