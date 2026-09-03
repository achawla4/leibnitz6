# -*- coding: utf-8 -*-
"""
Tests for Leibnitz 7 Multi-Column CSV & Spreadsheet Batch/Joint Processing Engine.
"""

import os
import sys
import tempfile
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from suganita_engine.signal_adapter import SignalAdapter
from suganita_engine import Lexer, Parser, SuganitaVM, compile_and_run, TokenType
from leibnitz6_sdk import Leibnitz7Client
from leibnitz6_server.server import app


def test_load_multi_column_csv():
    adapter = SignalAdapter()
    sample_csv = "time,channel_a,channel_b,channel_c\n0.0,1.0,0.5,0.2\n0.01,0.8,0.4,0.3\n0.02,0.6,0.3,0.4\n0.03,0.4,0.2,0.5\n"
    ds = adapter.load_csv_signals(sample_csv, dataset_name="test_multi_col")
    
    assert "channel_a" in ds['column_names']
    assert "channel_b" in ds['column_names']
    assert "channel_c" in ds['column_names']
    assert len(ds['channels']) == 3
    assert "test_multi_col:channel_a" in adapter.signals
    assert "channel_a" in adapter.signals


def test_batch_load_directory():
    adapter = SignalAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        csv1 = os.path.join(tmpdir, "signals_1.csv")
        csv2 = os.path.join(tmpdir, "signals_2.csv")
        
        with open(csv1, "w", encoding="utf-8") as f:
            f.write("time,ch1,ch2\n0.0,1.2,0.4\n0.1,1.5,0.8\n")
        with open(csv2, "w", encoding="utf-8") as f:
            f.write("time,ch3,ch4\n0.0,0.1,0.9\n0.1,0.3,0.7\n")

        batch_res = adapter.batch_load_directory(tmpdir)
        assert "signals_1" in batch_res
        assert "signals_2" in batch_res
        assert len(adapter.datasets) == 2


def test_joint_analysis_calculation():
    adapter = SignalAdapter()
    t = np.linspace(0, 1.0, 100, endpoint=False)
    adapter.signals["sig_1"] = {'t': t, 'y': np.sin(2 * np.pi * 5 * t), 'sr': 100, 'channel': 'sig_1'}
    adapter.signals["sig_2"] = {'t': t, 'y': np.cos(2 * np.pi * 5 * t), 'sr': 100, 'channel': 'sig_2'}
    
    res = adapter.process_joint_analysis(["sig_1", "sig_2"])
    assert res['num_channels'] == 2
    assert len(res['correlation_matrix']) == 2
    assert len(res['pair_correlations']) == 1
    assert "sig_1" in res['channel_stats']
    assert "sig_2" in res['channel_stats']

    b64_plot = adapter.render_multi_column_plot(title="Test Joint Multi-Column Plot")
    assert b64_plot is not None
    assert len(b64_plot) > 100


def test_suganita_devanagari_batch_dsl():
    code = """
    बहुस्तम्भ "sample_signal.csv"
    संयुक्त "Joint Signal Matrix"
    निरोध
    """
    summary, su_output = compile_and_run(code, "test_batch.su")
    
    logs = summary['logs']
    assert any("BAHUSTAMBHA" in l for l in logs)
    assert any("SAMYUKTA" in l for l in logs)
    assert len(summary['plots']) >= 1


def test_server_batch_and_joint_api_endpoints():
    client = app.test_client()
    
    # Test /api/batch_process endpoint
    sample_csv = "time,chA,chB\n0.0,1.0,0.5\n0.001,0.9,0.4\n0.002,0.8,0.3\n"
    res1 = client.post("/api/batch_process", json={"csv_data": sample_csv, "dataset_name": "api_batch_test"})
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert data1["status"] == "SUCCESS"
    assert data1["server"] == "Leibnitz7"
    assert "joint_analysis" in data1
    assert "plot_b64" in data1

    # Test /api/joint_analysis endpoint
    signals = {
        "ch1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "ch2": [5.0, 4.0, 3.0, 2.0, 1.0]
    }
    res2 = client.post("/api/joint_analysis", json={"signals": signals})
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2["status"] == "SUCCESS"
    assert data2["joint_analysis"]["num_channels"] == 2


def test_sdk_batch_and_joint_methods():
    client = Leibnitz7Client(server_url="http://127.0.0.1:5006", client_id="UnitTest_SDK")
    
    sample_csv = "time,signal1,signal2\n0.0,0.1,0.2\n0.01,0.3,0.4\n"
    res_batch = client.batch_process_csv(sample_csv, dataset_name="sdk_batch_test")
    assert res_batch is not None
    assert "joint_analysis" in res_batch

    res_joint = client.joint_analysis({"sigA": [1, 2, 3], "sigB": [3, 2, 1]})
    assert res_joint is not None
    assert "joint_analysis" in res_joint


if __name__ == "__main__":
    pytest.main([__file__])
