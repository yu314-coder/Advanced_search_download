#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import argparse
import venv
import shutil
from pathlib import Path

GITHUB_REPO = "https://github.com/yu314-coder/Advanced_search_download"
VENV_DIR = "venv"
REQUIRED_PYTHON_VERSION = (3, 8)

def is_windows():
    return platform.system().lower() == "windows"

def get_python_cmd():
    return "python" if is_windows() else "python3"

def get_venv_bin_dir():
    return "Scripts" if is_windows() else "bin"

def get_venv_python():
    bin_dir = get_venv_bin_dir()
    python_exe = "python.exe" if is_windows() else "python"
    return os.path.join(VENV_DIR, bin_dir, python_exe)

def get_venv_pip():
    bin_dir = get_venv_bin_dir()
    pip_exe = "pip.exe" if is_windows() else "pip"
    return os.path.join(VENV_DIR, bin_dir, pip_exe)

def run_command(cmd, cwd=None, shell=False):
    try:
        subprocess.run(cmd, cwd=cwd, check=True, shell=shell)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command {cmd}: {e}")
        return False

def check_python_version():
    current_version = sys.version_info[:2]
    if current_version < REQUIRED_PYTHON_VERSION:
        print(f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]} or higher is required")
        return False
    return True

def create_virtual_env():
    if os.path.exists(VENV_DIR):
        print(f"Virtual environment already exists in {VENV_DIR}")
        return True
    
    print("Creating virtual environment...")
    try:
        venv.create(VENV_DIR, with_pip=True)
        return True
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return False

def install_requirements():
    pip = get_venv_pip()
    print("Upgrading pip...")
    run_command([pip, "install", "--upgrade", "pip"])
    
    print("Installing requirements...")
    return run_command([pip, "install", "-r", "requirements.txt"])

def install_playwright():
    python = get_venv_python()
    print("Installing Playwright browsers...")
    return run_command([python, "-m", "playwright", "install"])

def clone_or_pull_repo():
    if not os.path.exists(".git"):
        print("Cloning repository...")
        return run_command(["git", "clone", GITHUB_REPO, "."])
    else:
        print("Updating repository...")
        return run_command(["git", "pull"])

def run_search_script():
    python = get_venv_python()
    return run_command([python, "download_script.py"])

def setup():
    if not check_python_version():
        return False
    
    if not create_virtual_env():
        return False
    
    if not install_requirements():
        return False
    
    if not install_playwright():
        return False
    
    print("Setup completed successfully!")
    return True

def main():
    parser = argparse.ArgumentParser(description="Manage the Advanced File Downloader project")
    parser.add_argument("command", choices=["setup", "run", "update", "clean"],
                       help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup()
    
    elif args.command == "run":
        if not os.path.exists(VENV_DIR):
            print("Virtual environment not found. Running setup first...")
            if not setup():
                return
        run_search_script()
    
    elif args.command == "update":
        clone_or_pull_repo()
        setup()
    
    elif args.command == "clean":
        if os.path.exists(VENV_DIR):
            print("Removing virtual environment...")
            shutil.rmtree(VENV_DIR)
        if os.path.exists("__pycache__"):
            print("Removing Python cache...")
            shutil.rmtree("__pycache__")
        print("Cleanup completed!")

if __name__ == "__main__":
    main()
