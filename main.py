import subprocess
import os
import glob

def remove_files(pattern):
    try:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"Removed {file}")
    except OSError as e:
        print(f"Error removing file {file}: {e}")
        
remove_files("*.log")
remove_files("*.session")
download_dir = os.path.abspath("downloads")
remove_files(os.path.join(download_dir, "*.ogg"))
remove_files(os.path.join(download_dir, "*.m4a"))
remove_files(os.path.join(download_dir, "*.mp3"))
try:
    subprocess.run(["python3", "-m", "osint"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running OSINT module: {e}")
except FileNotFoundError:
    print("The OSINT module could not be found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
