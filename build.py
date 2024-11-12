import os
import platform
import subprocess
import shutil
import sys
import pkg_resources

def install_requirements():
    """Install requirements with pip"""
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # Install requirements
        subprocess.run([
            sys.executable, 
            '-m', 
            'pip', 
            'install', 
            '--no-cache-dir',  # Avoid using cached wheels
            '-r', 
            'requirements.txt'
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def clean_build():
    """Clean build directories"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def build_app():
    """Build the application for the current platform"""
    clean_build()
    
    # Install dependencies
    if not install_requirements():
        print("Failed to install requirements. Aborting build.")
        sys.exit(1)
    
    try:
        # Run PyInstaller
        subprocess.run(['pyinstaller', 'url-markdown.spec', '--clean'], check=True)
        
        system = platform.system()
        if system == 'Darwin':
            print("macOS build created in dist/URL Markdown.app")
        elif system == 'Windows':
            print("Windows build created in dist/url-markdown.exe")
        else:
            print("Linux build created in dist/url-markdown")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_app()