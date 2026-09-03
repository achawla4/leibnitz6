# -*- coding: utf-8 -*-
"""
Universal GGUF Model Discovery & Local LLM Integration Manager
Discovers available .gguf model files on the system and manages local server connections.
"""

import os
import sys
import glob
import json
import subprocess

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

COMMON_GGUF_SEARCH_PATHS = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
    r"C:\Users\acer\llama-vulkan",
    r"C:\Users\acer\Downloads",
    r"C:\Users\acer\Documents",
    r"C:\Users\acer\.cache",
    r"C:\llama.cpp",
    r"D:\models"
]

class GGUFModelManager:
    def __init__(self):
        self.active_model_path = None
        self.active_server_url = "http://127.0.0.1:8080/v1/chat/completions"
        self.discovered_models = []
        self.scan_for_gguf_models()

    def scan_for_gguf_models(self) -> list:
        """Discovers all available .gguf model files across common directories."""
        found = set()
        
        # Check environment variable first
        env_path = os.environ.get("GGUF_MODEL_PATH")
        if env_path and os.path.exists(env_path) and env_path.endswith(".gguf"):
            found.add(os.path.abspath(env_path))

        # Check known specific GGUF model files
        specific_files = [
            r"C:\Users\acer\llama-vulkan\solar-10.7b-instruct-q4_k_m.gguf",
            os.path.join(WORKSPACE_ROOT, "solar-10.7b-instruct-q4_k_m.gguf"),
            r"C:\llama.cpp\models\solar-10.7b-instruct-q4_k_m.gguf"
        ]
        for f in specific_files:
            if os.path.exists(f):
                found.add(os.path.abspath(f))

        # Search top-level files in search dirs (non-recursive for speed)
        for search_dir in COMMON_GGUF_SEARCH_PATHS:
            if os.path.exists(search_dir):
                try:
                    for entry in os.listdir(search_dir):
                        if entry.endswith(".gguf"):
                            found.add(os.path.abspath(os.path.join(search_dir, entry)))
                except Exception:
                    pass

        self.discovered_models = sorted(list(found))
        if self.discovered_models:
            self.active_model_path = self.discovered_models[0]
        return self.discovered_models

    def set_active_model(self, model_path: str):
        """Sets active .gguf model file."""
        if os.path.exists(model_path):
            self.active_model_path = os.path.abspath(model_path)
            os.environ["GGUF_MODEL_PATH"] = self.active_model_path
            return True
        return False

    def get_active_model_name(self) -> str:
        if self.active_model_path:
            return os.path.basename(self.active_model_path)
        return "No GGUF Model Active (Offline Fallback Active)"

    def get_server_endpoint(self) -> str:
        return os.environ.get("GGUF_SERVER_URL", self.active_server_url)
