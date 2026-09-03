# -*- coding: utf-8 -*-
"""
Signal Engine Adapter for Suganita Runtime
Connects Suganita VM commands to SignalProcessingSuite and NumPy/SciPy execution.
"""

import sys
import os
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Try loading reference SignalProcessingSuite if available
REF_SPS_PATH = r'C:\Users\acer\Documents\REALInstitute\REALWeb\qLeibnitz2'
if os.path.exists(REF_SPS_PATH) and REF_SPS_PATH not in sys.path:
    sys.path.append(REF_SPS_PATH)

try:
    from SignalProcessingSuite.fft_tools import compute_fft
    from SignalProcessingSuite.filters import apply_filter
    from SignalProcessingSuite.time_features import extract_time_features
    HAS_SPS = True
except Exception:
    HAS_SPS = False


class SignalAdapter:
    def __init__(self):
        self.signals = {}
        self.datasets = {}
        self.plots = []
        self.output_logs = []

    def generate_synthetic_signal(self, name: str, sig_type: str = 'sinusoidal', freq: float = 12.0, duration: float = 2.0, sr: int = 1000):
        """Generate a synthetic test signal (e.g. sinusoidal, chirp, noise)."""
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        if sig_type == 'sinusoidal':
            signal = np.sin(2 * np.pi * freq * t) + 0.2 * np.random.normal(size=len(t))
        elif sig_type == 'chirp':
            signal = np.sin(2 * np.pi * (freq + 5 * t) * t)
        else:
            signal = np.random.normal(size=len(t))
        self.signals[name] = {'t': t, 'y': signal, 'sr': sr, 'channel': name}
        return self.signals[name]

    def load_csv_signals(self, csv_input, dataset_name: str = "multi_col_dataset", default_sr: int = 1000) -> dict:
        """
        Load multi-column CSV / spreadsheet signals from file path, string content, or file object.
        Extracts time column if present, and ingests all numeric signal columns simultaneously.
        """
        import csv
        lines = []
        if isinstance(csv_input, str):
            if os.path.exists(csv_input):
                with open(csv_input, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = [line.strip() for line in f if line.strip()]
                if dataset_name == "multi_col_dataset":
                    dataset_name = os.path.basename(csv_input).rsplit('.', 1)[0]
            else:
                lines = [line.strip() for line in csv_input.strip().split('\n') if line.strip()]
        elif hasattr(csv_input, 'readlines'):
            lines = [line.decode('utf-8', errors='ignore').strip() if isinstance(line, bytes) else line.strip() for line in csv_input.readlines()]

        if not lines:
            return {}

        reader = csv.reader(lines)
        header = [col.strip() for col in next(reader)]

        # Classify columns into time vs signal channels
        time_idx = None
        for idx, col in enumerate(header):
            if col.lower() in ('time', 't', 'timestamp', 'sec', 'seconds'):
                time_idx = idx
                break

        col_data = {col: [] for col in header}
        for row in reader:
            if not row or len(row) < len(header):
                continue
            for idx, col in enumerate(header):
                try:
                    col_data[col].append(float(row[idx]))
                except (ValueError, TypeError):
                    pass

        # Convert to numpy arrays
        parsed_data = {col: np.array(vals) for col, vals in col_data.items() if len(vals) > 0}
        
        if time_idx is not None and header[time_idx] in parsed_data:
            t = parsed_data[header[time_idx]]
            dt = np.mean(np.diff(t)) if len(t) > 1 else 1.0 / default_sr
            sr = int(round(1.0 / dt)) if dt > 0 else default_sr
            signal_cols = [c for c in header if c != header[time_idx] and c in parsed_data]
        else:
            signal_cols = list(parsed_data.keys())
            n_samples = max([len(v) for v in parsed_data.values()]) if parsed_data else 100
            t = np.linspace(0, n_samples / default_sr, n_samples, endpoint=False)
            sr = default_sr

        loaded_channels = []
        for col in signal_cols:
            y = parsed_data[col]
            sig_t = t[:len(y)]
            sig_key = f"{dataset_name}:{col}" if dataset_name else col
            self.signals[sig_key] = {
                't': sig_t,
                'y': y,
                'sr': sr,
                'dataset': dataset_name,
                'channel': col
            }
            # Also set direct channel key if not present
            if col not in self.signals:
                self.signals[col] = self.signals[sig_key]
            loaded_channels.append(sig_key)

        self.datasets[dataset_name] = {
            'channels': loaded_channels,
            'time': t,
            'sr': sr,
            'column_names': signal_cols
        }
        return self.datasets[dataset_name]

    def batch_load_directory(self, dir_path: str) -> dict:
        """Batch load all multi-column CSV spreadsheets in a directory."""
        if not os.path.isdir(dir_path):
            return {}
        results = {}
        for fname in os.listdir(dir_path):
            if fname.endswith('.csv') or fname.endswith('.tsv'):
                full_path = os.path.join(dir_path, fname)
                ds_name = fname.rsplit('.', 1)[0]
                results[ds_name] = self.load_csv_signals(full_path, dataset_name=ds_name)
        return results

    def process_fft(self, signal_name: str):
        """Compute Fast Fourier Transform for a named signal buffer."""
        if signal_name not in self.signals:
            self.generate_synthetic_signal(signal_name)

        sig_data = self.signals[signal_name]
        y = sig_data['y']
        sr = sig_data['sr']

        if HAS_SPS:
            try:
                freqs, mag = compute_fft(y, sr)
                return freqs, mag
            except Exception:
                pass

        # Fallback NumPy FFT computation
        n = len(y)
        freqs = np.fft.rfftfreq(n, d=1.0/sr)
        mag = np.abs(np.fft.rfft(y))
        return freqs, mag

    def process_joint_analysis(self, signal_names=None) -> dict:
        """
        Perform Leibnitz 7 Joint Processing & Multi-Column Signal Analysis:
        - Individual descriptive stats per channel (RMS, peak frequency, min, max, std)
        - Joint cross-correlation matrix across all signal columns
        - Signal similarity & cross-channel lag analysis
        """
        if not signal_names:
            signal_names = list(self.signals.keys())

        # Ensure signals exist
        valid_keys = [k for k in signal_names if k in self.signals]
        if len(valid_keys) < 2 and len(self.signals) < 2:
            # Generate synthetic multi-channel signals for joint testing
            self.generate_synthetic_signal("ch1_sine", sig_type="sinusoidal", freq=10.0)
            self.generate_synthetic_signal("ch2_chirp", sig_type="chirp", freq=5.0)
            self.generate_synthetic_signal("ch3_noise", sig_type="noise")
            valid_keys = ["ch1_sine", "ch2_chirp", "ch3_noise"]

        # Truncate to min length for joint comparison
        min_len = min(len(self.signals[k]['y']) for k in valid_keys)
        sig_matrix = np.column_stack([self.signals[k]['y'][:min_len] for k in valid_keys])

        # Pearson cross-correlation matrix
        if sig_matrix.shape[0] > 1:
            corr_matrix = np.corrcoef(sig_matrix, rowvar=False)
            if corr_matrix.ndim == 0:
                corr_matrix = np.array([[1.0]])
        else:
            corr_matrix = np.eye(len(valid_keys))

        # Individual channel metrics
        channel_stats = {}
        for idx, key in enumerate(valid_keys):
            y = self.signals[key]['y'][:min_len]
            freqs, mag = self.process_fft(key)
            peak_freq = float(freqs[np.argmax(mag)]) if len(mag) > 0 else 0.0
            rms = float(np.sqrt(np.mean(y**2)))
            channel_stats[key] = {
                'mean': float(np.mean(y)),
                'std': float(np.std(y)),
                'min': float(np.min(y)),
                'max': float(np.max(y)),
                'rms': rms,
                'peak_freq_hz': peak_freq
            }

        # Joint pair cross-correlations
        pair_correlations = []
        for i in range(len(valid_keys)):
            for j in range(i + 1, len(valid_keys)):
                key_i = valid_keys[i]
                key_j = valid_keys[j]
                r_val = float(corr_matrix[i, j])
                pair_correlations.append({
                    'signal_1': key_i,
                    'signal_2': key_j,
                    'correlation_coefficient': round(r_val, 4)
                })

        summary = {
            'joint_signals': valid_keys,
            'num_channels': len(valid_keys),
            'sample_count': min_len,
            'correlation_matrix': corr_matrix.tolist(),
            'channel_stats': channel_stats,
            'pair_correlations': pair_correlations
        }
        return summary

    def render_plot(self, signal_name: str, title: str = "Signal Analysis") -> str:
        """Render signal waveform and frequency spectrum into base64 PNG image."""
        if signal_name not in self.signals:
            self.generate_synthetic_signal(signal_name)

        sig = self.signals[signal_name]
        freqs, mag = self.process_fft(signal_name)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5))
        fig.suptitle(title, fontsize=12, fontweight='bold')

        # Time domain plot
        ax1.plot(sig['t'][:500], sig['y'][:500], color='#2b5c8f', linewidth=1.5)
        ax1.set_title("Time Domain Waveform")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Amplitude")
        ax1.grid(True, alpha=0.3)

        # Frequency domain plot
        ax2.plot(freqs, mag, color='#c0392b', linewidth=1.5)
        ax2.set_title("FFT Spectrum")
        ax2.set_xlabel("Frequency (Hz)")
        ax2.set_ylabel("Magnitude")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        self.plots.append({'title': title, 'image_b64': img_b64})
        return img_b64

    def render_multi_column_plot(self, signal_names=None, title: str = "Leibnitz 7 Joint Multi-Column Signal Suite") -> str:
        """
        Render multi-column stacked signal waveforms and joint cross-correlation matrix into base64 PNG image.
        """
        joint_res = self.process_joint_analysis(signal_names)
        valid_keys = joint_res['joint_signals']
        n_channels = len(valid_keys)
        corr_mat = np.array(joint_res['correlation_matrix'])

        fig = plt.figure(figsize=(10, 3 + n_channels * 1.5))
        gs = fig.add_gridspec(n_channels + 1, 2, width_ratios=[2, 1])

        colors = ['#10b981', '#3b82f6', '#06b6d4', '#f59e0b', '#8b5cf6', '#ec4899']

        # Plot time domain channels on left column
        ax_first = None
        for i, key in enumerate(valid_keys):
            ax = fig.add_subplot(gs[i, 0], sharex=ax_first if ax_first else None)
            if i == 0:
                ax_first = ax
            sig = self.signals[key]
            c = colors[i % len(colors)]
            disp_name = sig.get('channel', key)
            ax.plot(sig['t'][:500], sig['y'][:500], color=c, linewidth=1.2, label=disp_name)
            ax.set_ylabel(disp_name[:12], fontsize=9)
            ax.grid(True, alpha=0.25)
            ax.legend(loc='upper right', fontsize=8)
            if i == n_channels - 1:
                ax.set_xlabel("Time (s)", fontsize=9)

        # Plot joint FFT spectra stacked below waveforms
        ax_fft = fig.add_subplot(gs[n_channels, 0])
        for i, key in enumerate(valid_keys):
            freqs, mag = self.process_fft(key)
            c = colors[i % len(colors)]
            sig = self.signals[key]
            ax_fft.plot(freqs, mag, color=c, alpha=0.7, linewidth=1.2, label=sig.get('channel', key))
        ax_fft.set_title("Joint Frequency Spectrum (Overlay)", fontsize=10)
        ax_fft.set_xlabel("Frequency (Hz)", fontsize=9)
        ax_fft.set_ylabel("Magnitude", fontsize=9)
        ax_fft.grid(True, alpha=0.25)
        ax_fft.legend(loc='upper right', fontsize=8)

        # Plot Joint Correlation Matrix Heatmap on right side spanning full height
        ax_heatmap = fig.add_subplot(gs[:, 1])
        cax = ax_heatmap.matshow(corr_mat, cmap='coolwarm', vmin=-1.0, vmax=1.0)
        fig.colorbar(cax, ax=ax_heatmap, fraction=0.046, pad=0.04)

        short_labels = [self.signals[k].get('channel', k)[:8] for k in valid_keys]
        ax_heatmap.set_xticks(range(n_channels))
        ax_heatmap.set_yticks(range(n_channels))
        ax_heatmap.set_xticklabels(short_labels, rotation=45, ha='left', fontsize=8)
        ax_heatmap.set_yticklabels(short_labels, fontsize=8)
        ax_heatmap.set_title("Joint Cross-Correlation", fontsize=10, pad=12)

        # Annotate correlation values in heatmap cells
        for i in range(n_channels):
            for j in range(n_channels):
                val = corr_mat[i, j]
                ax_heatmap.text(j, i, f"{val:.2f}", ha='center', va='center',
                                color='white' if abs(val) > 0.5 else 'black', fontsize=8)

        fig.suptitle(title, fontsize=13, fontweight='bold', y=0.98)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        self.plots.append({'title': title, 'image_b64': img_b64})
        return img_b64

    def process_space_time_security_analysis(self, dataset_name: str = "multi_col_dataset") -> dict:
        """
        Perform 2D Space-Time Spectral Analysis for Cybersecurity Telemetry (sigsecurityv1.txt).
        - Column-wise (Time Domain FFT): Detects periodic beaconing, covert channels, C2 communications.
        - Row-wise (Spatial Domain FFT): Detects spatial synchronization across server racks/nodes (botnet propagation).
        - Joint 2D Fourier Transform (FFT2D): Computes 2D Spectral Density Matrix S(f_spatial, f_temporal).
        - Hacker Footprint Anomaly Index: Quantifies anomalous spectral energy concentration.
        """
        keys = self.datasets.get(dataset_name, [])
        if not keys:
            keys = [k for k in self.signals.keys() if dataset_name in k or dataset_name == "multi_col_dataset"]

        if not keys:
            # Fallback to all signals if none match exact dataset name
            keys = list(self.signals.keys())

        if not keys:
            return {'status': 'ERROR', 'message': f"No telemetry signals found for analysis."}

        matrix = []
        node_labels = []
        min_len = min([len(self.signals[k]['y']) for k in keys])
        for k in keys:
            matrix.append(self.signals[k]['y'][:min_len])
            node_labels.append(self.signals[k].get('channel', k))

        X = np.array(matrix)
        n_nodes, n_samples = X.shape

        # 2D Space-Time Fourier Transform
        X_2d_fft = np.fft.fft2(X)
        X_2d_shift = np.fft.fftshift(X_2d_fft)
        spectrogram_2d = np.abs(X_2d_shift)**2

        # Hacker Footprint Anomaly Index (Spectral Energy Anomaly Index)
        mean_energy = np.mean(spectrogram_2d)
        max_energy = np.max(spectrogram_2d)
        std_energy = np.std(spectrogram_2d)
        anomaly_score = float((max_energy - mean_energy) / (std_energy + 1e-6))

        channel_variances = np.var(X, axis=1)
        suspicious_nodes = []
        var_thresh = np.mean(channel_variances) + 1.2 * np.std(channel_variances)
        for idx, var in enumerate(channel_variances):
            if var > var_thresh:
                suspicious_nodes.append(node_labels[idx])

        plot_b64 = self.render_space_time_2d_plot(spectrogram_2d, node_labels, dataset_name, anomaly_score)

        return {
            'status': 'SUCCESS',
            'dataset_name': dataset_name,
            'n_nodes': n_nodes,
            'n_samples': n_samples,
            'hacker_footprint_anomaly_index': round(anomaly_score, 4),
            'threat_level': 'HIGH_ANOMALY' if anomaly_score > 4.5 else ('ELEVATED' if anomaly_score > 2.5 else 'NORMAL'),
            'suspicious_nodes': suspicious_nodes if suspicious_nodes else [node_labels[0]],
            'plot_b64': plot_b64,
            'security_context': 'Haryana Data Center Telemetry Defense (Space-Time 2D Fourier Security)'
        }

    def render_space_time_2d_plot(self, spectrogram_2d: np.ndarray, node_labels: list, dataset_name: str, anomaly_score: float) -> str:
        """Render 2D Space-Time Fourier Spectral Heatmap for Hacker Footprint Detection."""
        fig, ax = plt.subplots(figsize=(9, 4.5), dpi=100)
        cax = ax.imshow(np.log10(spectrogram_2d + 1.0), aspect='auto', cmap='inferno', origin='lower')
        fig.colorbar(cax, ax=ax, label="Log10 Spectral Density |F(f_space, f_time)|^2")

        ax.set_title(f"Haryana Data Center 2D Space-Time Fourier Spectrum [{dataset_name}]\nHacker Anomaly Index: {anomaly_score:.2f} ({'CRITICAL THREAT' if anomaly_score > 4.5 else 'MONITORED baseline'})", fontsize=11, fontweight='bold')
        ax.set_xlabel("Temporal Frequency Index (f_time)", fontsize=9)
        ax.set_ylabel("Spatial Node / Rack Index (f_space)", fontsize=9)
        ax.grid(True, alpha=0.15, color='white')

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        self.plots.append({'title': f"SpaceTime_2D_{dataset_name}", 'image_b64': img_b64})
        return img_b64

