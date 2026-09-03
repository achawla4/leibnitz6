# -*- coding: utf-8 -*-
"""
Suganita Virtual Machine (VM) and Interpreter Execution Runtime
Executes Suganita AST nodes, maintains stack/memory, and produces .su output payloads.
"""

from .parser import (
    ProgramNode, LiteralNode, PrintNode, PushNode, PopNode,
    AssignNode, FunctionCallNode, IfNode, PlotNode, MultiColumnNode,
    JointAnalysisNode, BatchProcessNode, DelayNode, HaltNode, NopNode, ASTNode
)
from .signal_adapter import SignalAdapter

class SuganitaVM:
    def __init__(self):
        self.stack = []
        self.env = {}
        self.ui_labels = []
        self.input_fields = []
        self.output_logs = []
        self.is_halted = False
        self.signal_adapter = SignalAdapter()

    def run(self, ast: ProgramNode) -> dict:
        """Execute Suganita AST and return execution context & output payload."""
        self.stack.clear()
        self.env.clear()
        self.ui_labels.clear()
        self.input_fields.clear()
        self.output_logs.clear()
        self.is_halted = False

        for stmt in ast.statements:
            if self.is_halted:
                break
            self._exec_node(stmt)

        return self.get_execution_summary()

    def _eval_node(self, node: ASTNode):
        if isinstance(node, LiteralNode):
            return node.value

        if isinstance(node, PushNode):
            val = self._eval_node(node.value)
            self.stack.append(val)
            self.input_fields.append(str(val))
            return val

        if isinstance(node, PopNode):
            if self.stack:
                return self.stack.pop()
            return None

        if isinstance(node, PrintNode):
            val = self._eval_node(node.expression)
            text = str(val)
            self.ui_labels.append(text)
            self.output_logs.append(f"[LIKHO] {text}")
            return text

        if isinstance(node, AssignNode):
            val = self._eval_node(node.value)
            self.env[node.name] = val
            return val

        if isinstance(node, PlotNode):
            target_name = "default_sig"
            if isinstance(node.target, LiteralNode):
                target_name = str(node.target.value)
            title = node.title
            b64_img = self.signal_adapter.render_plot(target_name, title=title)
            self.output_logs.append(f"[PLOT] Generated graph for {target_name}")
            return b64_img

        if isinstance(node, MultiColumnNode):
            target_val = self._eval_node(node.target)
            ds_res = self.signal_adapter.load_csv_signals(target_val)
            ch_names = list(ds_res.get('column_names', []))
            self.output_logs.append(f"[BAHUSTAMBHA] Loaded multi-column spreadsheet signal '{target_val}' ({len(ch_names)} channels: {', '.join(ch_names)})")
            return ds_res

        if isinstance(node, JointAnalysisNode):
            b64_img = self.signal_adapter.render_multi_column_plot(title=node.title)
            joint_summary = self.signal_adapter.process_joint_analysis()
            self.output_logs.append(f"[SAMYUKTA] Executed Leibnitz 7 Joint Multi-Column Signal Analysis ({joint_summary['num_channels']} channels, {len(joint_summary['pair_correlations'])} pairwise correlations)")
            return b64_img

        if isinstance(node, BatchProcessNode):
            dir_val = self._eval_node(node.target)
            batch_res = self.signal_adapter.batch_load_directory(str(dir_val))
            self.output_logs.append(f"[SANCHATMAKA] Batch ingested {len(batch_res)} CSV spreadsheets from directory '{dir_val}'")
            return batch_res

        if isinstance(node, DelayNode):
            ms = self._eval_node(node.ms)
            self.output_logs.append(f"[DELAY] Paused for {ms} ms")
            return ms

        if isinstance(node, HaltNode):
            self.is_halted = True
            self.output_logs.append("[HALT] Program execution halted (Nirodha)")
            return None

        if isinstance(node, NopNode):
            self.output_logs.append("[NOP] Sunya pause (Shu)")
            return None

        return None

    def _exec_node(self, node: ASTNode):
        if isinstance(node, IfNode):
            cond_val = self._eval_node(node.condition)
            if cond_val:
                for stmt in node.then_branch:
                    if self.is_halted:
                        break
                    self._exec_node(stmt)
            else:
                for stmt in node.else_branch:
                    if self.is_halted:
                        break
                    self._exec_node(stmt)
            return

        self._eval_node(node)

    def get_execution_summary(self) -> dict:
        """Return formatted execution dictionary."""
        return {
            'labels': self.ui_labels,
            'input_fields': self.input_fields,
            'logs': self.output_logs,
            'stack': self.stack,
            'env': self.env,
            'plots': self.signal_adapter.plots
        }

    def generate_su_output(self, original_filename: str = "signal1.su") -> str:
        """Format processed result into a .su payload file string for Leibnitz6."""
        out_lines = []
        out_lines.append(f"# Suganita Processed Payload - Leibnitz6")
        out_lines.append(f"# Source File: {original_filename}")
        out_lines.append(f"# Status: PROCESSED_SUCCESS\n")

        out_lines.append("[UI_LABELS]")
        for label in self.ui_labels:
            out_lines.append(f"लिखो {label}")

        out_lines.append("\n[INPUT_FIELDS]")
        for field in self.input_fields:
            out_lines.append(f"प्रवेश {field}")

        out_lines.append("\n[EXECUTION_LOGS]")
        for log in self.output_logs:
            out_lines.append(f"// {log}")

        out_lines.append("\n[PLOTS_DATA]")
        for idx, plot in enumerate(self.signal_adapter.plots):
            out_lines.append(f"// Plot #{idx+1}: {plot['title']}")
            out_lines.append(f"PLOT_B64: {plot['image_b64']}")

        return "\n".join(out_lines)
