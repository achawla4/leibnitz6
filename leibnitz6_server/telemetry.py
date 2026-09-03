# -*- coding: utf-8 -*-
"""
Leibnitz6 Network Telemetry & Usage Monitor Module
Tracks service usage, active clients, payload volumes, and request activity.
Persists metrics to disk and renders an interactive admin monitoring dashboard.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any

from leibnitz6_server.privacy import pseudonymize_ip

class UsageMonitor:
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'processed'))
            os.makedirs(base_dir, exist_ok=True)
            storage_path = os.path.join(base_dir, 'usage_telemetry.json')

        self.storage_path = storage_path
        self.metrics = {
            "server_start_time": datetime.now().isoformat(),
            "total_requests": 0,
            "suganita_transmissions": 0,
            "sahai_streams": 0,
            "copilot_queries": 0,
            "total_bytes_processed": 0,
            "clients": {},
            "recent_activity": []
        }
        self._load_metrics()

    def _load_metrics(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.metrics.update(saved)
            except Exception as e:
                print(f"[Telemetry Warning] Could not load metrics: {e}")

    def _save_metrics(self):
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"[Telemetry Warning] Could not save metrics: {e}")

    def record_request(self, client_ip: str, client_id: str, action: str, char_count: int = 0):
        # Pseudonymize IP for GDPR, CCPA, and DPDP compliance
        anon_ip = pseudonymize_ip(client_ip)

        self.metrics["total_requests"] += 1
        self.metrics["total_bytes_processed"] += char_count

        if action == "transmit":
            self.metrics["suganita_transmissions"] += 1
        elif action == "transmit_stream":
            self.metrics["sahai_streams"] += 1
        elif action == "copilot_query":
            self.metrics["copilot_queries"] += 1

        # Track client metrics using pseudonymized identifiers
        client_key = client_id or anon_ip or "Unknown_Client"
        now_iso = datetime.now().isoformat()

        if client_key not in self.metrics["clients"]:
            self.metrics["clients"][client_key] = {
                "first_seen": now_iso,
                "last_seen": now_iso,
                "total_requests": 0,
                "ip_address": anon_ip
            }

        client_info = self.metrics["clients"][client_key]
        client_info["last_seen"] = now_iso
        client_info["total_requests"] += 1

        # Record activity event
        event = {
            "timestamp": now_iso,
            "client": client_key,
            "ip": anon_ip,
            "action": action,
            "size_bytes": char_count
        }
        self.metrics["recent_activity"].insert(0, event)
        # Cap recent log to 50 items
        self.metrics["recent_activity"] = self.metrics["recent_activity"][:50]

        self._save_metrics()

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "server_uptime_start": self.metrics.get("server_start_time"),
            "total_requests": self.metrics.get("total_requests", 0),
            "suganita_transmissions": self.metrics.get("suganita_transmissions", 0),
            "sahai_streams": self.metrics.get("sahai_streams", 0),
            "copilot_queries": self.metrics.get("copilot_queries", 0),
            "total_bytes_processed": self.metrics.get("total_bytes_processed", 0),
            "unique_client_count": len(self.metrics.get("clients", {})),
            "clients": self.metrics.get("clients", {}),
            "recent_activity": self.metrics.get("recent_activity", [])
        }

    def render_dashboard_html(self) -> str:
        metrics = self.get_metrics()
        clients_json = json.dumps(metrics["clients"], indent=2)
        activity_json = json.dumps(metrics["recent_activity"][:15], indent=2)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="10">
    <title>Leibnitz 6 Network Usage Monitor & Telemetry Dashboard</title>
    <style>
        :root {{
            --bg: #0b0f19;
            --card-bg: #111827;
            --card-border: #1f293d;
            --accent-green: #10b981;
            --accent-blue: #3b82f6;
            --accent-amber: #f59e0b;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
        }}
        body {{
            background-color: var(--bg);
            color: var(--text-main);
            font-family: 'Segoe UI', system-ui, sans-serif;
            margin: 0; padding: 24px;
        }}
        h1 {{
            font-size: 1.8rem;
            margin-bottom: 8px;
            color: var(--text-main);
            display: flex; align-items: center; gap: 12px;
        }}
        .badge {{
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
            padding: 4px 12px; border-radius: 16px; font-size: 12px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px; margin-top: 24px; margin-bottom: 32px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px; padding: 20px;
        }}
        .card-num {{
            font-size: 2.2rem; font-weight: bold; color: var(--accent-blue);
            margin-top: 8px;
        }}
        .card-label {{
            font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;
        }}
        table {{
            width: 100%; border-collapse: collapse; margin-top: 12px; background: var(--card-bg);
            border-radius: 8px; overflow: hidden; border: 1px solid var(--card-border);
        }}
        th, td {{
            padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--card-border); font-size: 14px;
        }}
        th {{ background: #1f2937; color: var(--text-muted); font-weight: 600; }}
        tr:hover {{ background: #1e293b; }}
        .section-title {{ font-size: 1.2rem; margin-top: 32px; margin-bottom: 12px; color: var(--text-main); }}
    </style>
</head>
<body>

    <h1>
        📡 Leibnitz 6 Network Server Telemetry
        <span class="badge">● LIVE MONITORING (10s Auto Refresh)</span>
    </h1>
    <p style="color: var(--text-muted); font-size: 14px;">Real-time service usage metrics, active client tracking, and payload volume monitoring.</p>

    <div class="grid">
        <div class="card">
            <div class="card-label">Total Requests</div>
            <div class="card-num">{metrics['total_requests']}</div>
        </div>
        <div class="card">
            <div class="card-label">Suganita Executions</div>
            <div class="card-num" style="color: var(--accent-green);">{metrics['suganita_transmissions']}</div>
        </div>
        <div class="card">
            <div class="card-label">Sahai Streaming Sessions</div>
            <div class="card-num" style="color: var(--accent-amber);">{metrics['sahai_streams']}</div>
        </div>
        <div class="card">
            <div class="card-label">Unique Connected Clients</div>
            <div class="card-num">{metrics['unique_client_count']}</div>
        </div>
        <div class="card">
            <div class="card-label">Payload Volume</div>
            <div class="card-num" style="font-size: 1.6rem; color: #a7f3d0;">{metrics['total_bytes_processed']} B</div>
        </div>
    </div>

    <div class="section-title">📊 Active Client Registry</div>
    <table>
        <thead>
            <tr>
                <th>Client Identifier</th>
                <th>IP Address</th>
                <th>Total Requests</th>
                <th>First Seen</th>
                <th>Last Active</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f"<tr><td><b>{ck}</b></td><td>{cv['ip_address']}</td><td>{cv['total_requests']}</td><td>{cv['first_seen']}</td><td>{cv['last_seen']}</td></tr>" for ck, cv in metrics['clients'].items()]) if metrics['clients'] else "<tr><td colspan='5' style='color: var(--text-muted);'>No active clients recorded yet.</td></tr>"}
        </tbody>
    </table>

    <div class="section-title">⏱ Recent Activity Stream</div>
    <table>
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>Client</th>
                <th>IP</th>
                <th>Action</th>
                <th>Size (Bytes)</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f"<tr><td>{ev['timestamp']}</td><td>{ev['client']}</td><td>{ev['ip']}</td><td><span style='color: var(--accent-green);'>{ev['action']}</span></td><td>{ev['size_bytes']}</td></tr>" for ev in metrics['recent_activity'][:15]]) if metrics['recent_activity'] else "<tr><td colspan='5' style='color: var(--text-muted);'>No recent activity.</td></tr>"}
        </tbody>
    </table>

</body>
</html>"""
