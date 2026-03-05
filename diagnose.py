import subprocess
import os
import sys

def check_command(cmd):
    try:
        # Use shell=True for 'where' on Windows
        subprocess.run(f"where {cmd}", shell=True, capture_output=True, check=True)
        return True
    except:
        return False

def find_file_recursive(base_path, filename):
    for root, dirs, files in os.walk(base_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

print("--- ShadowDragon Thorough Diagnostics ---")
print(f"Python Executable: {sys.executable}")
print(f"FFmpeg in PATH: {'Yes' if check_command('ffmpeg') else 'No'}")

# Search for piper.exe in common locations
user_home = os.path.expanduser("~")
search_locations = [
    os.path.join(os.path.dirname(sys.executable), "Scripts"),
    os.path.join(user_home, "AppData", "Local", "Packages", "PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0", "LocalCache", "local-packages", "Python311", "Scripts"),
    os.path.join(user_home, "AppData", "Roaming", "Python", "Python311", "Scripts"),
    os.path.join(user_home, "AppData", "Local", "Programs", "Python", "Python311", "Scripts"),
]

piper_path = None
if check_command("piper"):
    piper_path = "piper (in PATH)"
else:
    for loc in search_locations:
        if os.path.exists(loc):
            potential = os.path.join(loc, "piper.exe")
            if os.path.exists(potential):
                piper_path = potential
                break

if not piper_path:
    # Last ditch: search local package list
    print("Searching user AppData for piper.exe (this may take a moment)...")
    piper_path = find_file_recursive(os.path.join(user_home, "AppData", "Local", "Packages"), "piper.exe")

print(f"Piper Executable: {piper_path if piper_path else 'NOT FOUND'}")

if not check_command("ffmpeg"):
    print("\nCRITICAL: FFmpeg is missing.")
    print("Action: Download from https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z and add to PATH.")
