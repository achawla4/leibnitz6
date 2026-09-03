# -*- coding: utf-8 -*-
"""
Leibnitz6 Protocol & Payload Handler
Handles transmit header parsing, Suganita payload execution, and output file generation.
"""

import os
import sys

# Ensure suganita_engine is importable
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from suganita_engine import compile_and_run

class TransmitProtocolHandler:
    def __init__(self, processed_dir: str = "processed"):
        self.processed_dir = os.path.abspath(processed_dir)
        os.makedirs(self.processed_dir, exist_ok=True)

    def parse_header(self, header_text: str) -> dict:
        """
        Parse initial Suganita transmit header lines.
        Example header:
            SUGANITA_TRANSMIT_HEADER v1.0
            FILE: signal1.su
            CLIENT: StructuredNotepad_v3
        """
        meta = {
            'version': '1.0',
            'filename': 'signal1.su',
            'client': 'StructuredNotepad_v3',
            'preamble': []
        }
        lines = header_text.strip().splitlines()
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("SUGANITA_TRANSMIT_HEADER"):
                parts = line_str.split()
                if len(parts) > 1:
                    meta['version'] = parts[1]
            elif line_str.startswith("FILE:"):
                meta['filename'] = line_str.split(":", 1)[1].strip()
            elif line_str.startswith("CLIENT:"):
                meta['client'] = line_str.split(":", 1)[1].strip()
            elif line_str:
                meta['preamble'].append(line_str)
        return meta

    def process_transmission(self, raw_header: str, su_source_code: str) -> dict:
        """
        Execute full transmission workflow:
        1. Parse preamble header.
        2. Compile & execute Suganita script.
        3. Save and return signal1out.su output payload.
        """
        header_meta = self.parse_header(raw_header)
        input_filename = header_meta['filename']

        # Determine output filename (e.g. signal1.su -> signal1out.su)
        if input_filename.endswith(".su"):
            base_name = input_filename[:-3]
            out_filename = f"{base_name}out.su"
        else:
            out_filename = f"{input_filename}_out.su"

        # Combine preamble (if any) with main source code
        if header_meta['preamble']:
            full_code = "\n".join(header_meta['preamble']) + "\n" + su_source_code
        else:
            full_code = su_source_code

        # Run Suganita Engine
        summary, su_output = compile_and_run(full_code, input_filename)

        # Save output to processed directory
        out_path = os.path.join(self.processed_dir, out_filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(su_output)

        return {
            'status': 'SUCCESS',
            'header': header_meta,
            'input_filename': input_filename,
            'output_filename': out_filename,
            'output_path': out_path,
            'summary': summary,
            'payload': su_output
        }
