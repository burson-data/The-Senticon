import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    try:
        import dotenv
    except ImportError:
        print("dotenv not found. Installing...")
        install("python-dotenv")
        print("dotenv installed successfully.")
