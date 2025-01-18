#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import venv
import shutil
from pathlib import Path
import time

# Set working directory to script location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
        
        # Install Linux-specific dependencies
        try:
            print("Installing Linux dependencies...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y",
                "libgstgl-1.0-0",
                "gstreamer1.0-plugins-base",
                "libavif13",
                "libenchant-2",
                "libsecret-1-0",
                "libhyphen0",
                "libmanette-0.2-0",
                "gstreamer1.0-plugins-bad",
                "libgstreamer1.0-0",
                "libgstreamer-plugins-base1.0-0",
                "libgstreamer-plugins-bad1.0-0",
                "gstreamer1.0-plugins-good",
                "gstreamer1.0-plugins-ugly"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Error installing some Linux dependencies: {e}")
            print("You may need to install missing dependencies manually.")

def run_command(cmd, cwd=None, shell=False):
    try:
        process = subprocess.run(cmd, cwd=cwd, check=True, shell=shell,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.stdout:
            print(process.stdout.decode())
        if process.stderr:
            print(process.stderr.decode())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command {cmd}:")
        if e.stdout:
            print(e.stdout.decode())
        if e.stderr:
            print(e.stderr.decode())
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
    
    if not os.path.exists("requirements.txt"):
        print("Creating requirements.txt...")
        with open("requirements.txt", "w") as f:
            f.write("""gradio>=4.0.0
playwright>=1.40.0
beautifulsoup4>=4.12.0
PyPDF2>=3.0.0
asyncio>=3.4.3
urllib3>=2.0.0""")
    
    print("Installing requirements...")
    return run_command([pip, "install", "-r", "requirements.txt"])

def install_playwright():
    python = get_venv_python()
    print("Installing Playwright browsers...")
    success = run_command([python, "-m", "playwright", "install"])
    if not success:
        print("Warning: Playwright installation might have issues. Continuing anyway...")
    return True

def clone_or_pull_repo():
    print("Checking repository status...")
    
    # List of expected files
    expected_files = [
        "README.md",
        "manage.py",
        "Advanced_search.py",
        "requirements.txt"
    ]
    
    if not os.path.exists(".git"):
        print("Initializing new repository...")
        if run_command(["git", "init"]):
            run_command(["git", "remote", "add", "origin", GITHUB_REPO])
            print("Remote added successfully.")
        else:
            print("Failed to initialize repository.")
            return False
    
    # Stash any local changes
    print("Saving local changes...")
    run_command(["git", "stash"])
    
    # Force pull from remote
    print("Pulling latest version...")
    success = run_command(["git", "fetch", "origin"])
    if success:
        success = run_command(["git", "reset", "--hard", "origin/main"])
        if success:
            print("Repository updated successfully!")
            
            # Verify all required files exist
            missing_files = [f for f in expected_files if not os.path.exists(f)]
            if missing_files:
                print("\nWarning: Missing files after update:", missing_files)
                return False
            return True
    
    print("Failed to update repository.")
    return False

def run_search_script():
    python = get_venv_python()
    script_name = "Advanced_search.py"
    
    if not os.path.exists(script_name):
        print(f"Error: {script_name} not found!")
        return False
    
    print(f"Running {script_name}...")
    return run_command([python, script_name])

def check_script_configuration():
    required_files = [
        "README.md",
        "manage.py",
        "Advanced_search.py",
        "requirements.txt"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("\nWarning: Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    return True

def setup():
    if not check_python_version():
        return False
    
    check_and_install_system_dependencies()
    
    if not create_virtual_env():
        return False
    
    if not install_requirements():
        return False
    
    if not install_playwright():
        print("Warning: Playwright installation might have issues.")
        choice = input("Continue anyway? (y/n): ")
        if choice.lower() != 'y':
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
        
    elif choice == "2":
        print("\nUpdating packages...")
        install_requirements()
        install_playwright()
        
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
        if not setup():
            print("Setup failed. Please check the errors above.")
            sys.exit(1)
    
    if not check_script_configuration():
        print("\nWarning: Some required files are missing.")
        choice = input("Continue anyway? (y/n): ")
        if choice.lower() != 'y':
            sys.exit(1)
    
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
