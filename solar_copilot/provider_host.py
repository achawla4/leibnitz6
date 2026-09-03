# -*- coding: utf-8 -*-
"""
Leibnitz 7.0 Solar GGUF Provider Host Manager
Implements multi-provider cloud GPU/RAM routing for Solar GGUF models as specified in leibnitz7RAMv1.txt.
Supports E2E Networks, RunPod, Vast.ai, AWS India, Local Vulkan GPU, and Render Cloud.
"""

import os
import requests
from typing import Dict, Any, Optional

# Supported Cloud GPU & High-RAM Providers (leibnitz7RAMv1.txt)
PROVIDER_REGISTRY = {
    "vast_ai": {
        "name": "Vast.ai Burst GPU",
        "gpu": "RTX 4090",
        "ram": "64 GB",
        "price_per_hr": "$0.67 (~₹55/hr)",
        "feasibility": "Lowest headline rates, fast 4-bit/8-bit GGUF inference",
        "default_endpoint": os.environ.get("VAST_AI_ENDPOINT", "http://127.0.0.1:8080/v1/chat/completions")
    },
    "runpod": {
        "name": "RunPod Cloud GPU",
        "gpu": "A100 40GB / RTX 4090",
        "ram": "64 GB",
        "price_per_hr": "$1.99 (~₹165/hr)",
        "feasibility": "Community GPUs, spot pricing, high throughput",
        "default_endpoint": os.environ.get("RUNPOD_ENDPOINT", "http://127.0.0.1:8080/v1/chat/completions")
    },
    "e2e_networks": {
        "name": "E2E Networks India",
        "gpu": "L4 / A100",
        "ram": "64–128 GB",
        "price_per_hr": "₹49–₹219/hr",
        "feasibility": "INR billing, Delhi NCR Data Center, ultra-low latency",
        "default_endpoint": os.environ.get("E2E_ENDPOINT", "http://127.0.0.1:8080/v1/chat/completions")
    },
    "aws_india": {
        "name": "AWS India EC2",
        "gpu": "G4dn / A100",
        "ram": "64–128 GB",
        "price_per_hr": "₹150–₹300/hr",
        "feasibility": "Stable enterprise infrastructure, quota-managed",
        "default_endpoint": os.environ.get("AWS_INDIA_ENDPOINT", "http://127.0.0.1:8080/v1/chat/completions")
    },
    "local_vulkan": {
        "name": "Local llama-server (GPU/Vulkan)",
        "gpu": "RTX 3060/4060 / Intel Iris Xe",
        "ram": "32–64 GB",
        "price_per_hr": "₹0 (Local Hardware)",
        "feasibility": "Zero cost, continuous day-to-day testing",
        "default_endpoint": "http://127.0.0.1:8080/v1/chat/completions"
    },
    "render_cloud": {
        "name": "Leibnitz 7 Render Cloud Gateway",
        "gpu": "Cloud CPU/GPU Hybrid",
        "ram": "512 MB – 8 GB",
        "price_per_hr": "Render Managed",
        "feasibility": "Always-on web API gateway",
        "default_endpoint": "https://leibnitz7-cloud-engine.onrender.com/api/copilot/complete"
    }
}


class GGUFProviderHostManager:
    """
    Manages Solar .gguf model provider endpoints and dynamic routing for Leibnitz 7.0.
    """

    def __init__(self):
        self.active_provider_key = os.environ.get("SOLAR_GPU_PROVIDER", "local_vulkan")
        self.custom_endpoint = os.environ.get("SOLAR_PROVIDER_ENDPOINT")
        self.api_key = os.environ.get("SOLAR_PROVIDER_API_KEY")

    def get_active_provider_info(self) -> Dict[str, Any]:
        """Return specs, pricing, and health of active Solar GGUF provider host."""
        provider_data = PROVIDER_REGISTRY.get(self.active_provider_key, PROVIDER_REGISTRY["local_vulkan"]).copy()
        
        endpoint = self.custom_endpoint or provider_data["default_endpoint"]
        provider_data["active_endpoint"] = endpoint
        provider_data["provider_key"] = self.active_provider_key
        provider_data["has_api_key"] = bool(self.api_key)
        provider_data["ram_budget_tier"] = "₹800–₹1,600/month (10–20 hrs burst capacity)"
        
        return provider_data

    def set_active_provider(self, provider_key: str, endpoint: Optional[str] = None, api_key: Optional[str] = None) -> bool:
        """Switch active Solar GGUF provider host at runtime."""
        if provider_key in PROVIDER_REGISTRY:
            self.active_provider_key = provider_key
            if endpoint:
                self.custom_endpoint = endpoint
            if api_key:
                self.api_key = api_key
            return True
        return False

    def query_provider(self, endpoint_url: str, payload: dict, timeout: float = 30.0) -> Optional[dict]:
        """Send completion request to provider endpoint with optional Bearer token auth."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            resp = requests.post(endpoint_url, json=payload, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None
