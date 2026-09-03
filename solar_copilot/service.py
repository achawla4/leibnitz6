# -*- coding: utf-8 -*-
"""
Solar-10.7B Copilot REST Helper Service
Provides endpoints for Structured Notepad v3 integration.
"""

import os
import sys
from flask import Flask, request, jsonify

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from solar_copilot.client import SolarLLMClient

app = Flask(__name__)
client = SolarLLMClient()

@app.route('/api/copilot/complete', methods=['POST'])
def complete():
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get('prompt', '')
    completion = client.complete_code(prompt)
    return jsonify({
        'status': 'SUCCESS',
        'prompt': prompt,
        'completion': completion
    })

@app.route('/api/copilot/explain', methods=['POST'])
def explain():
    data = request.get_json(force=True, silent=True) or {}
    code = data.get('code', '')
    explanation = client.explain_code(code)
    return jsonify({
        'status': 'SUCCESS',
        'code': code,
        'explanation': explanation
    })

@app.route('/api/copilot/models', methods=['GET', 'POST'])
def handle_models():
    if request.method == 'POST':
        data = request.get_json(force=True, silent=True) or {}
        model_path = data.get('model_path')
        if model_path and client.select_gguf_model(model_path):
            return jsonify({'status': 'SUCCESS', 'active_info': client.get_active_model_info()})
        return jsonify({'status': 'ERROR', 'message': f'Model path not found: {model_path}'}), 400

    return jsonify({'status': 'SUCCESS', 'info': client.get_active_model_info()})

if __name__ == '__main__':
    port = int(os.environ.get('COPILOT_PORT', 5007))
    print(f"[*] Launching Solar Copilot Service on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
