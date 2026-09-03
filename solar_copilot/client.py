# -*- coding: utf-8 -*-
"""
Solar-10.7B LLM Client Proxy
Interfaces with local llama-server (Solar GGUF) and provides offline Suganita completion fallbacks.
"""

import os
import requests
import json
import re
from .prompts import build_completion_prompt, build_explanation_prompt
from .gguf_runner import GGUFModelManager
from .provider_host import GGUFProviderHostManager, PROVIDER_REGISTRY

DEFAULT_SOLAR_URL = "http://127.0.0.1:8080/v1/chat/completions"
DEFAULT_CLOUD_SERVER = os.environ.get("LEIBNITZ_SERVER_URL", "https://leibnitz7-cloud-engine.onrender.com")

class SolarLLMClient:
    def __init__(self, endpoint_url: str = None):
        self.gguf_manager = GGUFModelManager()
        self.provider_host = GGUFProviderHostManager()
        self.endpoint_url = endpoint_url or self.gguf_manager.get_server_endpoint()

    def get_active_model_info(self) -> dict:
        info = {
            'active_model': self.gguf_manager.get_active_model_name(),
            'model_path': self.gguf_manager.active_model_path,
            'endpoint_url': self.endpoint_url,
            'discovered_models': self.gguf_manager.discovered_models,
            'provider_host': self.provider_host.get_active_provider_info()
        }
        return info

    def select_gguf_model(self, model_path: str):
        if self.gguf_manager.set_active_model(model_path):
            return True
        return False

    def complete_code(self, prompt_text: str, timeout: float = 30.0) -> str:
        """
        Send completion request to Solar AI Copilot across multi-provider cloud GPU/RAM hosts.
        Prioritizes high-accuracy neural generation over speed (extended timeouts & max_tokens).
        Priority 1: Configured Cloud GPU Provider Host (RunPod / Vast.ai / E2E Networks with 64 GB RAM / RTX 4090/A100).
        Priority 2: Direct Local llama-server Endpoint (Local GPU / Vulkan Solar GGUF).
        Priority 3: Local Network Server Engine on Port 5006.
        Priority 4: Centralized Cloud Server Gateway on Render.
        Priority 5: Fallback Offline Suganita rule-based autocomplete engine.
        """
        payload = {
            "messages": [
                {"role": "user", "content": build_completion_prompt(prompt_text)}
            ],
            "max_tokens": 300,
            "temperature": 0.2
        }

        # Priority 1: Configured Cloud GPU Provider Host
        provider_info = self.provider_host.get_active_provider_info()
        provider_endpoint = provider_info.get("active_endpoint")
        if provider_endpoint:
            data = self.provider_host.query_provider(provider_endpoint, payload, timeout=timeout)
            if data and 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                if content and content.strip():
                    return content.strip()

        # Priority 2: Direct Local llama-server Endpoint (Local GPU / Vulkan Solar GGUF)
        try:
            resp = requests.post(self.endpoint_url, json=payload, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                if content and content.strip():
                    return content.strip()
        except Exception:
            pass

        # Priority 3: Local Network Server Engine on Port 5006
        try:
            net_resp = requests.post("http://127.0.0.1:5006/api/copilot/complete", json={"prompt": prompt_text}, timeout=timeout)
            if net_resp.status_code == 200:
                data = net_resp.json()
                if data.get('status') == 'SUCCESS' and data.get('completion'):
                    return data['completion'].strip()
        except Exception:
            pass

        # Priority 4: Cloud Server Centralized Copilot on Render
        try:
            cloud_resp = requests.post(f"{DEFAULT_CLOUD_SERVER}/api/copilot/complete", json={"prompt": prompt_text}, timeout=timeout)
            if cloud_resp.status_code == 200:
                data = cloud_resp.json()
                if data.get('status') == 'SUCCESS' and data.get('completion'):
                    return data['completion'].strip()
        except Exception:
            pass

        # Priority 5: Fallback Offline Suganita Autocomplete Engine
        return self._generate_fallback_completion(prompt_text)

    def explain_code(self, code_snippet: str, timeout: float = 30.0) -> str:
        """Send code explanation request to Solar-10.7B llama-server with extended timeout for deep neural reasoning."""
        payload = {
            "messages": [
                {"role": "user", "content": build_explanation_prompt(code_snippet)}
            ],
            "max_tokens": 600,
            "temperature": 0.3
        }
        try:
            resp = requests.post(self.endpoint_url, json=payload, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                return data['choices'][0]['message']['content'].strip()
        except Exception:
            pass

        return self._generate_fallback_explanation(code_snippet)

    def _generate_fallback_completion(self, text: str) -> str:
        """Rule-based offline Suganita autocomplete generator."""
        lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
        last_line = lines[-1] if lines else ""

        if last_line.startswith("लिखो"):
            return 'प्रवेश "Signal_Input_Buffer"\nरुको १०००\nरूपरेखा "Spectral_Analysis"\nनिरोध'
        elif last_line.startswith("प्रवेश"):
            return 'रुको ५००\nरूपरेखा "FFT_Spectrum_Plot"\nनिरोध'
        elif last_line.startswith("रुको"):
            return 'रूपरेखा "Signal_Waveform_Plot"\nनिरोध'
        elif "यदि" in last_line:
            return 'ᳵ\n  लिखो "Condition_True"\n  रूपरेखा "Filtered_Signal"\nᳶ अन्यथा ᳵ\n  लिखो "Condition_False"\nᳶ\nनिरोध'
        else:
            return 'लिखो "REALInstitute"\nप्रवेश "Signal_Data_Field"\nरुको १०००\nरूपरेखा "Signal_Analysis"\nनिरोध'

    def _generate_fallback_explanation(self, code: str) -> str:
        """Offline Suganita script explanation generator."""
        explanations = []
        for line in code.strip().splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#") or line_str.startswith("//"):
                continue
            if line_str.startswith("लिखो"):
                explanations.append(f"• `{line_str}`: Emits a UI label and outputs text log.")
            elif line_str.startswith("प्रवेश"):
                explanations.append(f"• `{line_str}`: Pushes data payload to stack / defines input field.")
            elif line_str.startswith("रुको"):
                explanations.append(f"• `{line_str}`: Delays execution for specified duration.")
            elif line_str.startswith("रूपरेखा"):
                explanations.append(f"• `{line_str}`: Computes FFT spectrum and renders waveform plot.")
            elif line_str.startswith("निरोध"):
                explanations.append(f"• `{line_str}`: Halts execution (Nirodha / Sāṅkhya cessation).")
            else:
                explanations.append(f"• `{line_str}`: Executes Suganita instruction.")

        return "\n".join(explanations)
