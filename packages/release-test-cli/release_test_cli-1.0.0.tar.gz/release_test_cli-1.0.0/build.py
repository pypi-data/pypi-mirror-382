#!/usr/bin/env python3
"""Build script for creating CLI binary."""

import shutil
import subprocess
import sys
import os
from pathlib import Path


def clean_build_directories() -> None:
    """Clean up previous build artifacts."""
    print('🧹 Cleaning up previous build artifacts...')

    build_dirs = ['build', 'dist', '__pycache__']
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            print(f'  Removing {dir_name}/')
            shutil.rmtree(dir_name)

    # Clean up .pyc files
    for root, _dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

    print('✅ Cleanup complete!')


def check_pyinstaller() -> bool:
    """Check if PyInstaller is available."""
    try:
        subprocess.run(
            ['uv', 'run', 'pyinstaller', '--version'], check=True, capture_output=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            '❌ PyInstaller is not available. Use --install-pyinstaller flag or install manually with:'
        )
        print('   uv add --dev pyinstaller')
        return False



def build_executable(
    spec_file: str = 'cli.spec',
    clean: bool = True,
) -> bool:
    """Build the executable using PyInstaller."""
    if clean:
        clean_build_directories()

    # Check if PyInstaller is available (installation is handled by build.sh)
    if not check_pyinstaller():
        return False

    print(f'🔨 Building executable using {spec_file}...')

    try:
        # Run PyInstaller with uv
        cmd = ['uv', 'run', 'pyinstaller', spec_file, '--clean']

        print(f'Running: {" ".join(cmd)}')
        subprocess.run(cmd, check=True, capture_output=True, text=True)

        print('✅ Build completed successfully!')

        # Check if the executable was created
        dist_dir = Path('dist')
        if dist_dir.exists():
            executables = list(dist_dir.glob('*'))
            if executables:
                print('📁 Executable(s) created in dist/:')
                for exe in executables:
                    size = exe.stat().st_size / (1024 * 1024)  # Size in MB
                    print(f'  - {exe.name} ({size:.1f} MB)')
            else:
                print('⚠️  No executables found in dist/ directory')

        return True

    except subprocess.CalledProcessError as e:
        print(f'❌ Build failed: {e}')
        if e.stdout:
            print('STDOUT:', e.stdout)
        if e.stderr:
            print('STDERR:', e.stderr)
        return False



def main():
    build_executable()


if __name__ == "__main__":
    main()