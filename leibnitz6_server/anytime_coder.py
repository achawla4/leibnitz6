# -*- coding: utf-8 -*-
"""
Sahai's Anytime Code Streaming & Successive Refinement Module
Based on Sahai & Mitter (2006) anytime capacity & delay-constrained control theory.
Provides progressive refinement streams for signal processing data and Suganita payloads.
"""

import numpy as np
import base64
import json

class AnytimeRefinementLevel:
    COARSE_BASE = 0      # Delay-free base preview (decimated signal / key metrics)
    MEDIUM_DETAIL = 1    # Filtered band metrics & medium resolution spectral features
    FULL_PRECISION = 2   # High-resolution floats & lossless payload state


class AnytimeEncoder:
    """
    Encodes signal payloads into Sahai anytime code streaming blocks.
    Each block provides immediate delay-free estimation while allowing
    successive refinement as additional streaming frames arrive.
    """
    def __init__(self, tree_depth: int = 4, memory_len: int = 8):
        self.tree_depth = tree_depth
        self.memory_len = memory_len

    def encode_signal_buffer(self, signal: np.ndarray, num_levels: int = 3) -> list[dict]:
        """
        Decompose a 1D signal buffer into progressive refinement layers.
        Level 0: Subsampled coarse baseline (1/4 rate).
        Level 1: Midband residual detail.
        Level 2: Full precision residual delta.
        """
        N = len(signal)
        frames = []

        # Level 0: Coarse base representation (decimated)
        step = max(1, N // 100)
        coarse_indices = np.arange(0, N, step)
        coarse_vals = signal[coarse_indices].astype(np.float32)
        
        # Parity calculation for streaming resilience (Sahai tree parity check)
        parity_0 = int(np.sum(coarse_vals * 100) % 65521)

        frames.append({
            'level': AnytimeRefinementLevel.COARSE_BASE,
            'frame_id': 0,
            'total_samples': N,
            'indices': coarse_indices.tolist(),
            'values': coarse_vals.tolist(),
            'parity': parity_0,
            'description': 'Base Coarse Preview'
        })

        # Level 1: Medium detail residual
        interp_base = np.interp(np.arange(N), coarse_indices, coarse_vals).astype(np.float32)
        residual_1 = signal - interp_base
        med_step = max(1, N // 250)
        med_indices = np.arange(0, N, med_step)
        med_vals = residual_1[med_indices].astype(np.float32)
        parity_1 = int(np.sum(med_vals * 100) % 65521)

        frames.append({
            'level': AnytimeRefinementLevel.MEDIUM_DETAIL,
            'frame_id': 1,
            'total_samples': N,
            'indices': med_indices.tolist(),
            'values': med_vals.tolist(),
            'parity': parity_1,
            'description': 'Midband Successive Refinement'
        })

        # Level 2: Full precision residual
        med_interp = np.interp(np.arange(N), med_indices, med_vals).astype(np.float32)
        residual_2 = (signal - (interp_base + med_interp)).astype(np.float32)
        parity_2 = int(np.sum(residual_2 * 100) % 65521)

        frames.append({
            'level': AnytimeRefinementLevel.FULL_PRECISION,
            'frame_id': 2,
            'total_samples': N,
            'indices': list(range(N)),
            'values': residual_2.tolist(),
            'parity': parity_2,
            'description': 'Full Precision Refinement'
        })

        return frames

    def encode_payload(self, su_payload_str: str) -> list[dict]:
        """
        Encode a Suganita text payload into progressive anytime streaming chunks.
        """
        lines = su_payload_str.splitlines()
        total_lines = len(lines)

        # Level 0: UI Labels & Metadata headers only
        l0_lines = [l for l in lines if l.startswith("[") or l.startswith("लिखो") or l.startswith("#")]
        
        # Level 1: Include Input fields & execution logs
        l1_lines = [l for l in lines if not l.startswith("PLOT_B64:")]

        # Level 2: Full payload including plot images
        l2_lines = lines

        return [
            {
                'level': AnytimeRefinementLevel.COARSE_BASE,
                'content': "\n".join(l0_lines),
                'refinement_score': 0.33
            },
            {
                'level': AnytimeRefinementLevel.MEDIUM_DETAIL,
                'content': "\n".join(l1_lines),
                'refinement_score': 0.66
            },
            {
                'level': AnytimeRefinementLevel.FULL_PRECISION,
                'content': "\n".join(l2_lines),
                'refinement_score': 1.00
            }
        ]


class AnytimeDecoder:
    """
    Decodes Sahai anytime streaming blocks continuously, reconstructing
    progressively refined signal approximations.
    """
    def __init__(self, total_samples: int = 1000):
        self.total_samples = total_samples
        self.current_signal = np.zeros(total_samples, dtype=np.float32)
        self.current_level = -1
        self.received_frames = {}

    def ingest_frame(self, frame: dict) -> np.ndarray:
        """Process incoming frame and update anytime signal estimate."""
        level = frame['level']
        self.received_frames[level] = frame
        self.current_level = max(self.current_level, level)

        N = frame.get('total_samples', self.total_samples)
        if len(self.current_signal) != N:
            self.current_signal = np.zeros(N, dtype=np.float32)

        indices = np.array(frame['indices'])
        values = np.array(frame['values'], dtype=np.float32)

        if level == AnytimeRefinementLevel.COARSE_BASE:
            # Interpolate base signal across full domain
            self.current_signal = np.interp(np.arange(N), indices, values).astype(np.float32)
        
        elif level == AnytimeRefinementLevel.MEDIUM_DETAIL:
            # Add medium residual refinement
            med_residual = np.interp(np.arange(N), indices, values).astype(np.float32)
            self.current_signal += med_residual

        elif level == AnytimeRefinementLevel.FULL_PRECISION:
            # Add full precision exact residual
            self.current_signal[indices] += values

        return self.current_signal

    def get_refinement_status(self) -> dict:
        return {
            'highest_level_received': self.current_level,
            'refinement_name': {
                0: 'Coarse Base',
                1: 'Medium Refinement',
                2: 'Full Precision'
            }.get(self.current_level, 'Uninitialized'),
            'fidelity_pct': (self.current_level + 1) * 33.33 if self.current_level >= 0 else 0.0
        }
