# -*- coding: utf-8 -*-
"""
Leibnitz6 Execution Server
Flask API Server supporting transmission headers, Suganita execution,
and Sahai anytime coding successive refinement streaming.
"""

import os
import sys
import json
import time
from flask import Flask, request, jsonify, send_from_directory, Response

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from leibnitz6_server.protocol import TransmitProtocolHandler
from leibnitz6_server.anytime_coder import AnytimeEncoder, AnytimeDecoder
from leibnitz6_server.telemetry import UsageMonitor
from leibnitz6_server.security import init_security_stack, sanitize_suganita_input
from leibnitz6_server.privacy import init_privacy_stack
from leibnitz6_server.ai_protocols import init_ai_protocol_routes
from leibnitz6_server.finops import init_finops_observability_routes, record_finops_execution
from leibnitz6_server.resilience import init_resilience_routes, global_circuit_breaker, global_event_bus
from leibnitz6_server.observability import init_observability_stack
from leibnitz6_server.accessibility import init_accessibility_routes
from leibnitz6_server.account import init_account_routes

app = Flask(__name__)
app.secret_key = os.environ.get('LEIBNITZ_SECRET_KEY', 'leibnitz6-owasp-asvs5-secure-key')

# Initialize 2026 Security, Privacy, AI Protocols, FinOps, Resilience, Observability, Accessibility, and Account Stacks
init_security_stack(app)
init_privacy_stack(app)
init_ai_protocol_routes(app)
init_finops_observability_routes(app)
init_resilience_routes(app)
init_observability_stack(app)
init_accessibility_routes(app)
init_account_routes(app)

protocol_handler = TransmitProtocolHandler(processed_dir=os.path.join(WORKSPACE_ROOT, 'processed'))
anytime_encoder = AnytimeEncoder()
telemetry_monitor = UsageMonitor()

@app.route('/', methods=['GET'])
def root_index():
    """Root GET handler for Leibnitz 7 Cloud Engine on Render."""
    for base in [WORKSPACE_ROOT, os.path.dirname(__file__), os.getcwd()]:
        file_path = os.path.join(base, 'leibnitz6.html')
        if os.path.exists(file_path):
            return send_from_directory(base, 'leibnitz6.html')
    return jsonify({
        'status': 'ONLINE',
        'server': 'Leibnitz7',
        'service': 'leibnitz7-cloud-engine',
        'hallmark': 'Multi-Column Batch Ingestion & 2D Space-Time Fourier Analysis',
        'health_check': '/health',
        'space_time_analysis_api': '/api/security/space_time_analysis',
        'live_threat_test_api': '/api/security/live_threat_test',
        'hybrid_threat_validation_api': '/api/security/hybrid_threat_validation'
    })

@app.route('/leibnitz6.html', methods=['GET'])
def get_leibnitz6_html():
    """Serve leibnitz6.html interface directly."""
    for base in [WORKSPACE_ROOT, os.path.dirname(__file__), os.getcwd()]:
        file_path = os.path.join(base, 'leibnitz6.html')
        if os.path.exists(file_path):
            return send_from_directory(base, 'leibnitz6.html')
    return Response("<h1>Leibnitz 7.0 Server Online</h1>", mimetype='text/html; charset=utf-8')

@app.route('/intro.txt', methods=['GET'])
def get_intro_txt():
    for base in [WORKSPACE_ROOT, os.path.dirname(__file__), os.getcwd()]:
        file_path = os.path.join(base, 'intro.txt')
        if os.path.exists(file_path):
            return send_from_directory(base, 'intro.txt', mimetype='text/plain; charset=utf-8')
    return Response("WELCOME TO LEIBNITZ 6.0\nRefer to https://github.com/achawla4/leibnitz6/blob/main/intro.txt", mimetype='text/plain; charset=utf-8')

@app.route('/install.py', methods=['GET'])
def get_install_py():
    for base in [WORKSPACE_ROOT, os.path.dirname(__file__), os.getcwd()]:
        file_path = os.path.join(base, 'install.py')
        if os.path.exists(file_path):
            return send_from_directory(base, 'install.py', mimetype='text/x-python; charset=utf-8')
    return Response("# Leibnitz6 Remote Installer\n", mimetype='text/x-python; charset=utf-8')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ONLINE',
        'server': 'Leibnitz7',
        'version': '7.0.0',
        'hallmark': 'Batch and Joint Signal Processing of Multi-Column CSVs and Spreadsheets',
        'accessibility_2026': ['WCAG_2.2_Level_AA', 'European_Accessibility_Act_EAA', 'ADA_Title_III', 'ARIA_1.3_Landmarks', 'WebAuthn_Passkeys'],
        'observability_2026': ['OpenTelemetry_v1.28', 'Prometheus', 'Grafana_Loki', 'Tempo_Jaeger', 'Datadog_APM'],
        'resilience_2026': ['Resilience4j_CircuitBreaker', 'Kafka_EventBridge_EventBus', 'Istio_Linkerd_eBPF', 'Zero_Downtime_RollingUpdate'],
        'cloud_native_2026': ['Kubernetes_HPA', 'FinOps_Pay_Per_Use', 'OpenTelemetry_Prometheus', 'Edge_WASM_Gateway', 'GitOps_Pipeline'],
        'security_compliance': ['OWASP_ASVS_5.0', 'NIST_SP_800_218', 'PCI_DSS_4.0', 'CISA_Secure_by_Design'],
        'privacy_compliance': ['GDPR_Art_32', 'CCPA_CPRA', 'DPDP_Act_2023', 'Global_Privacy_Control_GPC'],
        'ai_protocols': ['Anthropic_MCP_1.0', 'Google_A2A_1.0', 'IBM_ACP_1.0'],
        'features': ['Batch_Joint_MultiColumn_Processing', 'Suganita_VM', 'Sahai_Anytime_Streaming', 'SignalProcessingSuite', 'Telemetry_Monitor', 'Solar_GGUF_Copilot', 'Account_Dashboard_TFA']
    })

@app.route('/dashboard.html', methods=['GET'])
@app.route('/account', methods=['GET'])
def get_dashboard_page():
    for base in [WORKSPACE_ROOT, os.path.dirname(__file__), os.getcwd()]:
        file_path = os.path.join(base, 'dashboard.html')
        if os.path.exists(file_path):
            return send_from_directory(base, 'dashboard.html', mimetype='text/html; charset=utf-8')
    return Response("<h1>Dashboard not found</h1>", mimetype='text/html', status=404)


@app.route('/api/transmit', methods=['POST'])
def transmit():
    """Standard single-shot transmit request."""
    data = request.get_json(force=True, silent=True) or {}
    raw_header = data.get('header', 'SUGANITA_TRANSMIT_HEADER v1.0\nFILE: signal1.su\nCLIENT: Terminal')
    source_code = sanitize_suganita_input(data.get('source_code', ''))

    if not source_code and 'file' in request.files:
        uploaded_file = request.files['file']
        source_code = sanitize_suganita_input(uploaded_file.read().decode('utf-8', errors='ignore'))

    # Record telemetry
    client_ip = request.remote_addr or '127.0.0.1'
    client_id = request.headers.get('X-Client-ID', 'StructuredNotepad_v4')
    telemetry_monitor.record_request(client_ip, client_id, action="transmit", char_count=len(source_code))

    result = protocol_handler.process_transmission(raw_header, source_code)
    return jsonify(result)

@app.route('/api/transmit_stream', methods=['POST'])
def transmit_stream():
    """
    Streaming transmit request implementing Sahai Anytime Coding.
    Yields successive refinement frames (Base -> Midband -> Full Precision).
    """
    data = request.get_json(force=True, silent=True) or {}
    raw_header = data.get('header', 'SUGANITA_TRANSMIT_HEADER v1.0\nFILE: signal1.su')
    source_code = data.get('source_code', '')

    # Record telemetry
    client_ip = request.remote_addr or '127.0.0.1'
    client_id = request.headers.get('X-Client-ID', 'StructuredNotepad_v4')
    telemetry_monitor.record_request(client_ip, client_id, action="transmit_stream", char_count=len(source_code))

    result = protocol_handler.process_transmission(raw_header, source_code)
    payload_str = result['payload']

    # Generate Sahai anytime refinement frames
    frames = anytime_encoder.encode_payload(payload_str)

    def generate_stream():
        for frame in frames:
            chunk = {
                'status': 'STREAMING_REFINEMENT',
                'refinement_level': frame['level'],
                'refinement_score': frame['refinement_score'],
                'content': frame['content'],
                'output_filename': result['output_filename']
            }
            yield f"data: {json.dumps(chunk)}\n\n"
        
        # Final completion frame
        yield f"data: {json.dumps({'status': 'STREAM_COMPLETE', 'result': result})}\n\n"

    return Response(generate_stream(), content_type='text/event-stream')

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """JSON API telemetry endpoint for usage monitoring."""
    return jsonify(telemetry_monitor.get_metrics())

@app.route('/api/copilot/complete', methods=['POST'])
def copilot_complete():
    """
    Centralized Solar GGUF Copilot Endpoint served by the Leibnitz 6 Network Server.
    Clients do not need their own local GGUF model file when connected to Network Mode.
    """
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get('prompt', '')
    
    # Record copilot telemetry
    client_ip = request.remote_addr or '127.0.0.1'
    client_id = request.headers.get('X-Client-ID', 'StructuredNotepad_v4')
    telemetry_monitor.record_request(client_ip, client_id, action="copilot_query", char_count=len(prompt))

    t0 = time.time()
    from solar_copilot import SolarLLMClient
    solar = SolarLLMClient()
    completion = solar.complete_code(prompt)
    duration_ms = (time.time() - t0) * 1000.0

    # Record Solar GGUF AI Copilot FinOps cost & token metrics
    from leibnitz6_server.finops import record_solar_gguf_usage
    record_solar_gguf_usage(prompt, completion, duration_ms)

    return jsonify({
        'status': 'SUCCESS',
        'completion': completion,
        'model': 'Solar-10.7B-GGUF (Served by Leibnitz 7 Provider Host Manager)',
        'server': 'Leibnitz7'
    })

@app.route('/api/copilot/provider_status', methods=['GET'])
def copilot_provider_status():
    """
    Returns active Solar GGUF cloud provider host info, RAM specs (64 GB burst tier), 
    and pricing breakdown as specified in leibnitz7RAMv1.txt.
    """
    from solar_copilot.provider_host import GGUFProviderHostManager, PROVIDER_REGISTRY
    manager = GGUFProviderHostManager()
    return jsonify({
        'status': 'SUCCESS',
        'server': 'Leibnitz7',
        'active_provider': manager.get_active_provider_info(),
        'available_providers': PROVIDER_REGISTRY
    })

@app.route('/api/copilot/set_provider', methods=['POST'])
def copilot_set_provider():
    """
    Switch active Solar GGUF cloud provider host at runtime (e.g. vast_ai, runpod, e2e_networks, aws_india, local_vulkan).
    """
    from solar_copilot.provider_host import GGUFProviderHostManager
    data = request.get_json(force=True, silent=True) or {}
    provider_key = data.get('provider_key')
    endpoint = data.get('endpoint')
    api_key = data.get('api_key')

    manager = GGUFProviderHostManager()
    success = manager.set_active_provider(provider_key, endpoint=endpoint, api_key=api_key)

    if success:
        return jsonify({
            'status': 'SUCCESS',
            'message': f"Active Solar GGUF provider switched to '{provider_key}'",
            'provider_info': manager.get_active_provider_info()
        })
    return jsonify({
        'status': 'ERROR',
        'message': f"Invalid provider key '{provider_key}'. Valid keys: vast_ai, runpod, e2e_networks, aws_india, local_vulkan, render_cloud"
    }), 400

@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Real-time HTML monitoring dashboard for server administrators."""
    return Response(telemetry_monitor.render_dashboard_html(), mimetype='text/html')

@app.route('/api/processed/<filename>', methods=['GET'])
def get_processed_file(filename):
    processed_dir = protocol_handler.processed_dir
    return send_from_directory(processed_dir, filename)

@app.route('/install.py', methods=['GET'])
def download_installer():
    installer_path = os.path.join(WORKSPACE_ROOT, "remote_install.py")
    if os.path.exists(installer_path):
        with open(installer_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content, mimetype='text/plain')
    return jsonify({'status': 'ERROR', 'message': 'Installer script not found.'}), 404

if __name__ == "__main__":
    port = int(os.environ.get('LEIBNITZ_PORT', 5006))
    print(f"[*] Launching Leibnitz6 Network Server on http://127.0.0.1:{port}")
    print(f"[*] Usage Monitoring Dashboard available on http://127.0.0.1:{port}/admin/dashboard")
    app.run(host='0.0.0.0', port=port, debug=False)
