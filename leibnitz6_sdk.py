# -*- coding: utf-8 -*-
"""
Leibnitz6 Python SDK for Machine & AI Agent Integration
Allows any external machine, autonomous AI agent, script, or application to 
programmatically execute Suganita Devanagari DSL, stream Sahai anytime signal refinements,
and query Solar AI Copilot over standard HTTP REST APIs.
"""

import os
import requests
import json
from typing import Dict, Any, Generator, Optional

DEFAULT_CLOUD_SERVER = os.environ.get("LEIBNITZ_SERVER_URL", "https://leibnitz6.onrender.com")

class Leibnitz6Client:
    """
    Programmatic Client for Machine & AI Agent Access to Leibnitz 6 Cloud Engine.
    
    Example Usage:
        from leibnitz6_sdk import Leibnitz6Client
        
        client = Leibnitz6Client()
        result = client.execute("रूपरेखा सिग्नलबफर प्रवेश\n  लिखो('Machine Execution')\nनिरोध")
        print(result['summary']['logs'])
    """
    
    def __init__(self, server_url: str = DEFAULT_CLOUD_SERVER, client_id: str = "AI_Agent_Machine"):
        self.server_url = server_url.rstrip('/')
        self.client_id = client_id

    def execute(self, suganita_code: str, filename: str = "agent_script.su") -> Dict[str, Any]:
        """
        Execute Suganita Devanagari DSL script on Leibnitz 6 Cloud Server.
        Returns JSON summary containing execution logs, variable states, and plot data.
        """
        header = f"SUGANITA_TRANSMIT_HEADER v1.0\nFILE: {filename}\nCLIENT: {self.client_id}"
        payload = {
            "header": header,
            "source_code": suganita_code
        }
        headers = {"X-Client-ID": self.client_id}

        try:
            resp = requests.post(f"{self.server_url}/api/transmit", json=payload, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                return resp.json()
            return {"status": "ERROR", "error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            # Fallback to local in-process execution if cloud engine is unreachable
            from suganita_engine import compile_and_run
            summary, su_output = compile_and_run(suganita_code, filename)
            return {"status": "OFFLINE_FALLBACK", "summary": summary, "su_output": su_output}

    def execute_stream(self, suganita_code: str, filename: str = "agent_script.su") -> Generator[Dict[str, Any], None, None]:
        """
        Stream Sahai Anytime Code Refinement layers from Leibnitz 6 Cloud Server.
        Yields successive refinement progress objects (Level 0 Coarse -> Level 2 Full Precision).
        """
        header = f"SUGANITA_TRANSMIT_HEADER v1.0\nFILE: {filename}\nCLIENT: {self.client_id}"
        payload = {
            "header": header,
            "source_code": suganita_code
        }
        headers = {"X-Client-ID": self.client_id}

        try:
            resp = requests.post(f"{self.server_url}/api/transmit_stream", json=payload, headers=headers, stream=True, timeout=10.0)
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        yield json.loads(decoded[6:])
        except Exception as e:
            yield {"status": "ERROR", "error": str(e)}

    def copilot_complete(self, prompt: str) -> str:
        """
        Query Solar-10.7B AI Copilot endpoint served by Leibnitz 6 Engine.
        Returns code completion or AI response string.
        """
        headers = {"X-Client-ID": self.client_id}
        try:
            resp = requests.post(f"{self.server_url}/api/copilot/complete", json={"prompt": prompt}, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('completion', '').strip()
        except Exception:
            pass

        # Offline fallback
        from solar_copilot import SolarLLMClient
        solar = SolarLLMClient()
        return solar.complete_code(prompt)

if __name__ == "__main__":
    # Self-test demonstration
    client = Leibnitz6Client(client_id="SelfTest_Machine_Agent")
    print("Testing Leibnitz6 Machine SDK Execution...")
    res = client.execute("रूपरेखा टेस्टप्रवेश\n  लिखो('Hello from Autonomous AI Agent!')\nनिरोध")
    print(f"Status: {res.get('status')}")
    if res.get('summary', {}).get('logs'):
        print(f"Logs: {res['summary']['logs']}")
