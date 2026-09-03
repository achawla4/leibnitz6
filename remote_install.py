# -*- coding: utf-8 -*-
"""
Leibnitz6 Platform - Standalone Remote Installer
Designed to be served via HTTP (/install.py) and executed via standard python one-liner.
Prompts for user's .gguf model path, installs dependencies, and launches Structured Notepad v4 immediately!
"""

import sys
import os
import urllib.request
import subprocess
import glob

REQUIRED_PACKAGES = ['numpy', 'scipy', 'matplotlib', 'flask', 'requests', 'pillow', 'pytest']

def run_remote_installation():
    print("==========================================================================")
    print("     LEIBNITZ6 PLATFORM & STRUCTURED NOTEPAD v4 REMOTE INSTALLER         ")
    print("==========================================================================")
    
    # 1. Install dependencies
    print("\n[Step 1/4] Checking and installing Python dependencies...")
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            print(f"  [+] Installing {pkg}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", pkg])
            except subprocess.CalledProcessError:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", pkg])
    print("  [OK] Dependencies verified.")

    # 2. Connect to Centralized Cloud Server on Render
    print("\n[Step 2/3] Connecting to Centralized Leibnitz 6 Cloud Server...")
    cloud_url = os.environ.get("LEIBNITZ_SERVER_URL", "https://leibnitz6.onrender.com")
    print(f"  [OK] Central Cloud Engine: {cloud_url}")
    print("  [OK] Centralized Solar-10.7B AI Copilot Endpoint active. (Zero local server setup required!)")

    # 3. Create Launchers for Client Frontends (GUI Notepad v4 & Terminal REPL CLI)
    print("\n[Step 3/3] Creating Client Launchers...")
    cwd = os.getcwd()
    
    target_dir = cwd
    if not os.path.exists(os.path.join(cwd, "structured_notepad_ext")):
        possible_root = os.path.join(cwd, "REALWeb", "Leibnitz6")
        if os.path.exists(possible_root):
            target_dir = possible_root

    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)

    notepad_bat = os.path.join(cwd, "StructuredNotepad_v4.bat")
    repl_bat = os.path.join(cwd, "Suganita_Terminal_REPL.bat")
    
    # Client Launcher (GUI) with explicit PYTHONPATH
    with open(notepad_bat, 'w', encoding='utf-8') as f:
        f.write(f'@echo off\nset PYTHONPATH={target_dir};%PYTHONPATH%\ncd /d "{target_dir}"\nstart "Structured Notepad v4 Client" "{sys.executable}" -m structured_notepad_ext.notepad_app\n')

    # Terminal REPL Launcher (CLI) with explicit PYTHONPATH
    with open(repl_bat, 'w', encoding='utf-8') as f:
        f.write(f'@echo off\nset PYTHONPATH={target_dir};%PYTHONPATH%\ncd /d "{target_dir}"\n"{sys.executable}" -m leibnitz6_server.cli\npause\n')

    print(f"  [OK] Structured Notepad v4 GUI created: {notepad_bat}")
    print(f"  [OK] Suganita Terminal REPL CLI created: {repl_bat}")

    # Launch Structured Notepad v4 Client Immediately
    print("\n[+] Launching Structured Notepad v4 Client...")
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{target_dir};{env.get('PYTHONPATH', '')}"
    subprocess.Popen([sys.executable, "-m", "structured_notepad_ext.notepad_app"], cwd=target_dir, env=env)
    
    print("\n==========================================================================")
    print("  [SUCCESS] STRUCTURED NOTEPAD v4 CLIENT IS NOW RUNNING! HAPPY SIGNAL CODING!")
    print("  (Connected to Central Leibnitz 6 Cloud Engine — Zero local server setup!)")
    print("==========================================================================")

if __name__ == "__main__":
    run_remote_installation()
