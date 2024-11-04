import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    # Clean previous builds
    for dir in ['build', 'dist', 'release']:
        if os.path.exists(dir):
            shutil.rmtree(dir)

    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--clean',
        '--name', 'git-scanner',
        '--add-data', f'README.md{os.pathsep}.',
        'main.py'
    ]

    # Run PyInstaller
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Build failed:\n{result.stderr}")
        sys.exit(1)

    # Move executable to release folder
    release_dir = Path('release')
    release_dir.mkdir(exist_ok=True)

    executable = 'git-scanner.exe' if sys.platform == 'win32' else 'git-scanner'
    src = Path('dist') / executable
    dst = release_dir / executable

    if src.exists():
        shutil.copy2(src, dst)
        print(f"\n✅ Built {dst}")
    else:
        print("\n❌ Build failed - executable not found")
        sys.exit(1)

if __name__ == '__main__':
    build_executable()