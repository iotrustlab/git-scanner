import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_executable():
    # Clean previous builds
    for dir in ['build', 'dist']:
        if os.path.exists(dir):
            shutil.rmtree(dir)
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Create single executable
        '--name', 'git-scanner',
        '--add-data', 'README.md:.',
        '--icon', 'icon.ico' if os.name == 'nt' else 'icon.icns',
        'main.py'
    ]
    
    # Add platform-specific options
    if sys.platform == 'win32':
        cmd.extend(['--noconsole'])
    
    # Run PyInstaller
    subprocess.run(cmd)
    
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
        print("\n❌ Build failed")

if __name__ == '__main__':
    build_executable()