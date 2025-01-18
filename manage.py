#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import venv
import shutil
from pathlib import Path
import time

GITHUB_REPO = "https://github.com/yu314-coder/Advanced_search_download.git"
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

def check_and_install_system_dependencies():
    print("Checking system dependencies...")
    
    # Check pip
    try:
        import pip
        print("pip is already installed.")
    except ImportError:
        print("Installing pip...")
        subprocess.run([get_python_cmd(), "-m", "ensurepip", "--default-pip"], check=True)

    # Check git
    if is_windows():
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            print("git is already installed.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Please install Git for Windows from https://git-scm.com/download/win")
            sys.exit(1)
    else:
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            print("git is already installed.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            if os.path.exists("/etc/debian_version"):
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "git"], check=True)
            elif os.path.exists("/etc/redhat-release"):
                subprocess.run(["sudo", "yum", "install", "-y", "git"], check=True)
            else:
                print("Please install git manually for your system")
                sys.exit(1)

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
        print("Virtual environment already exists.")
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
    
    check_and_install_system_dependencies()
    
    if not create_virtual_env():
        return False
    
    if not install_requirements():
        return False
    
    if not install_playwright():
        return False
    
    print("Setup completed successfully!")
    return True

def display_menu():
    print("\n--- Advanced Search Download Manager ---")
    print("1. Update all scripts from GitHub")
    print("2. Update installed packages")
    print("3. Run Advanced Search Download")
    print("4. Clean environment")
    print("5. Exit")

def handle_menu_choice(choice):
    if choice == "1":
        print("\nUpdating from GitHub...")
        clone_or_pull_repo()
        time.sleep(1)
        
    elif choice == "2":
        print("\nUpdating packages...")
        install_requirements()
        install_playwright()
        time.sleep(1)
        
    elif choice == "3":
        print("\nStarting Advanced Search Download...")
        run_search_script()
        
    elif choice == "4":
        print("\nCleaning environment...")
        if os.path.exists(VENV_DIR):
            shutil.rmtree(VENV_DIR)
        if os.path.exists("__pycache__"):
            shutil.rmtree("__pycache__")
        print("Environment cleaned!")
        setup()
        
    elif choice == "5":
        print("\nExiting...")
        sys.exit(0)
        
    else:
        print("\nInvalid choice. Please try again.")

def main():
    # Initial setup check
    if not os.path.exists(VENV_DIR):
        print("First-time setup detected. Installing dependencies...")
        setup()
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ")
        handle_menu_choice(choice)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
