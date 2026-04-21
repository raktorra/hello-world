"""Run this script to produce a standalone a-eye.exe via PyInstaller."""
import subprocess
import sys

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--name", "a-eye",
    "main.py",
]

subprocess.run(cmd, check=True)
print("\nBuild complete. Your executable is at: dist/a-eye.exe")
