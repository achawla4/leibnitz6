# -*- coding: utf-8 -*-
"""
Leibnitz6 Platform & Structured Notepad v4 - Automated Installer & Environment Setup
Installs dependencies, configures runtime paths, generates launcher shortcuts, and runs verification.
"""

import sys
import os
import subprocess
import shutil

WORKSPACE_ROOT = os.path.abspath(os.path.dirname(__file__))

REQUIRED_PACKAGES = [
    'numpy',
    'scipy',
    'matplotlib',
    'flask',
    'requests',
    'pillow',
    'pytest'
]

def check_and_install_dependencies():
    print("==========================================================================")
    print("        LEIBNITZ6 PLATFORM & STRUCTURED NOTEPAD v4 INSTALLER              ")
    print("==========================================================================")
    print("\n[Step 1/4] Verifying Python Environment & Package Dependencies...")

    installed = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
            installed.append(pkg)
        except ImportError:
            print(f"  [+] Installing missing package: {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            installed.append(pkg)

    print(f"  [OK] All required packages verified: {', '.join(installed)}")

def verify_directory_structure():
    print("\n[Step 2/4] Verifying Workspace Structure & Required Directories...")
    dirs = ['suganita_engine', 'leibnitz6_server', 'solar_copilot', 'structured_notepad_ext', 'processed', 'examples', 'tests']
    for d in dirs:
        dir_path = os.path.join(WORKSPACE_ROOT, d)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"  [+] Created directory: {d}")
        else:
            print(f"  [OK] Found directory: {d}")

def create_launcher_shortcuts():
    print("\n[Step 3/4] Creating Desktop Launcher Scripts...")
    
    # 1. Structured Notepad v4 Launcher
    notepad_bat = os.path.join(WORKSPACE_ROOT, "StructuredNotepad_v4.bat")
    with open(notepad_bat, 'w', encoding='utf-8') as f:
        f.write(f'@echo off\ncd /d "{WORKSPACE_ROOT}"\nstart "Structured Notepad v4" "{sys.executable}" -m structured_notepad_ext.notepad_app\n')
    print(f"  [OK] Created launcher: {notepad_bat}")

    # 2. Leibnitz6 Server Launcher
    server_bat = os.path.join(WORKSPACE_ROOT, "Leibnitz6_Server.bat")
    with open(server_bat, 'w', encoding='utf-8') as f:
        f.write(f'@echo off\ncd /d "{WORKSPACE_ROOT}"\nstart "Leibnitz6 Server" "{sys.executable}" -m leibnitz6_server.server\n')
    print(f"  [OK] Created launcher: {server_bat}")

    # 3. Solar Copilot Launcher
    copilot_bat = os.path.join(WORKSPACE_ROOT, "Solar_Copilot.bat")
    with open(copilot_bat, 'w', encoding='utf-8') as f:
        f.write(f'@echo off\ncd /d "{WORKSPACE_ROOT}"\nstart "Solar Copilot" "{sys.executable}" -m solar_copilot.service\n')
    print(f"  [OK] Created launcher: {copilot_bat}")

def run_system_verification():
    print("\n[Step 4/4] Executing Platform Verification Test Suite...")
    res = subprocess.run([sys.executable, "-m", "pytest", "tests/"], cwd=WORKSPACE_ROOT)
    if res.returncode == 0:
        print("\n==========================================================================")
        print("  [SUCCESS] LEIBNITZ6 PLATFORM & STRUCTURED NOTEPAD v4 INSTALLED & VERIFIED!")
        print("  Launch Structured Notepad v4 via: StructuredNotepad_v4.bat")
        print("==========================================================================")
    else:
        print("\n[!] Installation completed with test warnings. Please review test output.")

if __name__ == "__main__":
    check_and_install_dependencies()
    verify_directory_structure()
    create_launcher_shortcuts()
    run_system_verification()
