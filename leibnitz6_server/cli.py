# -*- coding: utf-8 -*-
"""
Leibnitz6 Command-Line Interface (CLI) & Interactive Suganita Terminal REPL
Provides full terminal-based interaction for users who prefer working in terminal.
Features interactive REPL, single-file Sahai anytime streaming, and Solar AI copilot assistance.
"""

import sys
import os
import argparse
import requests
import json

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from suganita_engine import compile_and_run
from leibnitz6_server.protocol import TransmitProtocolHandler
from leibnitz6_server.anytime_coder import AnytimeDecoder

DEFAULT_SERVER_URL = os.environ.get("LEIBNITZ_SERVER_URL", "https://leibnitz6.onrender.com")

def run_interactive_repl(server_url: str = DEFAULT_SERVER_URL):
    """Interactive Devanagari Suganita Terminal REPL Environment."""
    print("==========================================================================")
    print("           LEIBNITZ 7 BATCH & JOINT SUGANITA TERMINAL REPL v7.0          ")
    print("==========================================================================")
    print(f"[*] Target Network Server: {server_url}")
    print("[*] Commands: Type Suganita code, 'copilot <prompt>' for AI assist, 'help', or 'exit'.\n")

    cmd_buffer = []

    while True:
        try:
            prompt_str = "... " if cmd_buffer else "suganita> "
            line = input(prompt_str).strip()
            
            if not line:
                if cmd_buffer:
                    code = "\n".join(cmd_buffer)
                    cmd_buffer = []
                    _execute_repl_code(code, server_url)
                continue

            if line.lower() in ('exit', 'quit'):
                print("Exiting Suganita Terminal REPL. Namaste!")
                break

            if line.lower() == 'help':
                print("\n  [Suganita Terminal Help — Leibnitz 7]")
                print("  • Keyword Reference: लिखो, प्रवेश, विसर्जन, रुको, रूपरेखा, बहुस्तम्भ, संयुक्त, संचात्मक, निरोध, शु, यदि, अन्यथा")
                print("  • Multi-Column CSV Load: बहुस्तम्भ 'data.csv'")
                print("  • Joint Signal Analysis: संयुक्त 'Multi-Channel Analysis'")
                print("  • Batch Directory Load:  संचात्मक 'signals_folder/'")
                print("  • Solar AI Assist:       Type 'copilot <your query>'")
                print("  • Multiline Code:        Enter lines, press Enter twice to evaluate.\n")
                continue

            if line.lower().startswith('copilot '):
                query = line[8:].strip()
                _query_terminal_copilot(query, server_url)
                continue

            cmd_buffer.append(line)
            
            # Single line immediate evaluation if not a block start
            if len(cmd_buffer) == 1 and not line.endswith('{') and not line.startswith('यदि'):
                code = cmd_buffer[0]
                cmd_buffer = []
                _execute_repl_code(code, server_url)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting Suganita Terminal REPL. Goodbye!")
            break

def _execute_repl_code(code: str, server_url: str):
    """Execute Suganita snippet via Network Server or local fallback."""
    print("\n--- [Execution Output] ---")
    server_online = False
    try:
        resp = requests.post(f"{server_url}/api/transmit", json={
            'header': "SUGANITA_TRANSMIT_HEADER v1.0\nFILE: repl.su\nCLIENT: Suganita_Terminal_REPL",
            'source_code': code
        }, headers={'X-Client-ID': 'Terminal_REPL_Client'}, timeout=2.5)
        
        if resp.status_code == 200:
            server_online = True
            data = resp.json()
            summary = data.get('summary', {})
            logs = summary.get('logs', [])
            print("🌐 [Processed via Leibnitz 6 Network Server]")
            for log in logs:
                print(f"  {log}")
            if summary.get('plots'):
                print(f"  [+] Spectral Plot generated: {summary['plots'][0]['title']}")
    except Exception:
        server_online = False

    if not server_online:
        print("⚠️ [Offline Fallback Mode]")
        summary, su_output = compile_and_run(code, "repl.su")
        for log in summary.get('logs', []):
            print(f"  {log}")
        if summary.get('plots'):
            print(f"  [+] Spectral Plot generated: {summary['plots'][0]['title']}")

    print("--------------------------\n")

def _query_terminal_copilot(prompt: str, server_url: str):
    print(f"\n✨ [Solar AI Copilot Querying: '{prompt}']...")
    try:
        resp = requests.post(f"{server_url}/api/copilot/complete", json={"prompt": prompt}, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            completion = data.get('completion', '').strip()
            print("🌐 [Server-Provided Solar GGUF Response]:")
            print(f"{completion}\n")
            return
    except Exception:
        pass

    # Offline fallback
    from solar_copilot import SolarLLMClient
    solar = SolarLLMClient()
    completion = solar.complete_code(prompt)
    print("⚠️ [Offline Copilot Fallback Response]:")
    print(f"{completion}\n")

def run_cli_transmit(filepath: str, server_url: str = DEFAULT_SERVER_URL, stream: bool = True):
    if not os.path.exists(filepath):
        print(f"[ERR] Input file '{filepath}' not found.")
        sys.exit(1)

    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        source_code = f.read()

    header = f"SUGANITA_TRANSMIT_HEADER v1.0\nFILE: {filename}\nCLIENT: Leibnitz6_Terminal_CLI"

    print(f"============================================================")
    print(f"          LEIBNITZ 6 TRANSMISSION TERMINAL                 ")
    print(f"============================================================")
    print(f"[*] Transmitting Header:\n{header}")
    print(f"------------------------------------------------------------")
    print(f"[*] Target Server: {server_url}")

    try:
        if stream:
            resp = requests.post(f"{server_url}/api/transmit_stream", json={
                'header': header,
                'source_code': source_code
            }, headers={'X-Client-ID': 'Terminal_CLI'}, stream=True, timeout=5)
            
            print("\n[+] Sahai Anytime Code Streaming Active (Successive Refinement):")
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        payload_data = json.loads(decoded[6:])
                        status = payload_data.get('status')
                        if status == 'STREAMING_REFINEMENT':
                            score = payload_data['refinement_score'] * 100
                            level = payload_data['refinement_level']
                            print(f"  --> Received Layer {level} Refinement ({score:.0f}% fidelity)")
                        elif status == 'STREAM_COMPLETE':
                            res = payload_data['result']
                            out_path = res['output_path']
                            print(f"\n[OK] Stream Completed! Response written to: {out_path}")
                            return out_path
        else:
            resp = requests.post(f"{server_url}/api/transmit", json={
                'header': header,
                'source_code': source_code
            }, headers={'X-Client-ID': 'Terminal_CLI'}, timeout=5)
            res = resp.json()
            out_path = res['output_path']
            print(f"\n[OK] Response received! Output written to: {out_path}")
            return out_path

    except Exception as e:
        print(f"[*] Server connection failed ({e}). Executing via local Protocol Engine...")
        handler = TransmitProtocolHandler()
        res = handler.process_transmission(header, source_code)
        out_path = res['output_path']
        print(f"[OK] Direct Execution Complete! File saved to: {out_path}")
        return out_path


def main():
    parser = argparse.ArgumentParser(description="Leibnitz6 Suganita Terminal Client & REPL")
    parser.add_argument("file", nargs="?", default=None, help="Path to .su file (If omitted, starts interactive REPL)")
    parser.add_argument("--server", default=DEFAULT_SERVER_URL, help="Leibnitz6 Server URL")
    parser.add_argument("--no-stream", action="store_true", help="Disable anytime streaming")
    args = parser.parse_args()

    if args.file:
        run_cli_transmit(args.file, server_url=args.server, stream=not args.no_stream)
    else:
        run_interactive_repl(server_url=args.server)

if __name__ == "__main__":
    main()
