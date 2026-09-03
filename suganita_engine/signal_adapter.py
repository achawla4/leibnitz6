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
        self.signals[name] = {'t': t, 'y': signal, 'sr': sr}
        return self.signals[name]

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
