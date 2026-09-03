# -*- coding: utf-8 -*-
"""
Solar Copilot Package
"""

from .client import SolarLLMClient
from .prompts import SUGANITA_SYSTEM_PROMPT, build_completion_prompt, build_explanation_prompt
from .service import app
