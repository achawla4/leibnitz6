# -*- coding: utf-8 -*-
"""
Structured Notepad v3 - Interactive Jupyter-Style Suganita Notebook Extension
Provides interactive cells with inline evaluation, instant output & inline plot rendering below cells,
Solar AI Copilot assistance, and Leibnitz6 server transmission.
"""

import sys
import os
import io
import json
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    tk = None
    ttk = filedialog = messagebox = None
from PIL import Image, ImageTk

# Import workspace components
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from suganita_engine import compile_and_run
from leibnitz6_server import TransmitProtocolHandler
from solar_copilot import SolarLLMClient

DEFAULT_SERVER_URL = os.environ.get("LEIBNITZ_SERVER_URL", "https://leibnitz6.onrender.com")

DEVANAGARI_KEYWORDS = [
    'लिखो', 'प्रवेश', 'विसर्जन', 'रुको', 'रूपरेखा', 'निरोध',
    'शु', 'शूः', 'यदि', 'अन्यथा', 'हेतु', 'उदाहरण', 'कार्य',
    'मुख्य', 'गुणन', 'भागहार', 'शेष', 'योग', 'व्यवकलन'
]

class SuganitaNotebookCell(tk.Frame):
    """
    Jupyter-style Notebook Cell Widget for Suganita commands.
    Contains code input editor and instant inline output container below the command.
    """
    def __init__(self, parent, cell_num: int, app_reference, default_code: str = ""):
        super().__init__(parent, bg='#181825', bd=1, relief=tk.SOLID, padx=5, pady=5)
        self.cell_num = cell_num
        self.app = app_reference

        self._build_header()
        self._build_editor(default_code)
        self._build_output_area()

    def _build_header(self):
        header_frame = tk.Frame(self, bg='#181825')
        header_frame.pack(fill=tk.X, side=tk.TOP, pady=2)

        self.cell_label = tk.Label(header_frame, text=f"In [{self.cell_num}]:", bg='#181825', fg='#89b4fa', font=('Consolas', 10, 'bold'))
        self.cell_label.pack(side=tk.LEFT)

        btn_run = tk.Button(header_frame, text="▶ Run Cell (Shift+Enter)", bg='#a6e3a1', fg='#11111b', font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, command=self.evaluate_cell)
        btn_run.pack(side=tk.LEFT, padx=5)

        btn_ai = tk.Button(header_frame, text="✨ Solar AI", bg='#f9e2af', fg='#11111b', font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, command=self.ai_complete_cell)
        btn_ai.pack(side=tk.LEFT, padx=3)

        btn_del = tk.Button(header_frame, text="🗑 Delete", bg='#f38ba8', fg='#11111b', font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, command=self.delete_cell)
        btn_del.pack(side=tk.RIGHT, padx=3)

        btn_add = tk.Button(header_frame, text="+ Cell Below", bg='#313244', fg='#cdd6f4', font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, command=self.add_cell_below)
        btn_add.pack(side=tk.RIGHT, padx=3)

    def _build_editor(self, default_code: str):
        self.text_editor = tk.Text(self, wrap=tk.WORD, bg='#1e1e2e', fg='#cdd6f4', insertbackground='#89b4fa', font=('Consolas', 11), height=5, undo=True)
        self.text_editor.pack(fill=tk.BOTH, expand=True, pady=3)
        
        if default_code:
            self.text_editor.insert(tk.END, default_code)

        # Keybindings: Shift+Enter to run cell, Ctrl+Space for AI
        self.text_editor.bind('<Shift-Return>', lambda e: self._on_shift_enter(e))
        self.text_editor.bind('<Control-space>', lambda e: self._on_ctrl_space(e))
        self.text_editor.bind('<KeyRelease>', lambda e: self._highlight_syntax())
        self._highlight_syntax()

    def _build_output_area(self):
        self.output_frame = tk.Frame(self, bg='#11111b', padx=5, pady=5)
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=3)

        self.out_label = tk.Label(self.output_frame, text=f"Out [{self.cell_num}]:", bg='#11111b', fg='#a6e3a1', font=('Consolas', 9, 'bold'))
        self.out_label.pack(anchor='w')

        self.out_text = tk.Label(self.output_frame, text="[ Ready for evaluation ]", bg='#11111b', fg='#a6adc8', font=('Consolas', 9), justify=tk.LEFT, anchor='w')
        self.out_text.pack(fill=tk.X, anchor='w', pady=2)

        self.img_label = tk.Label(self.output_frame, bg='#11111b')
        self.img_label.pack(fill=tk.BOTH, expand=True, pady=3)

    def evaluate_cell(self):
        code = self.text_editor.get("1.0", tk.END).strip()
        if not code:
            return

        target_url = getattr(self.app, 'server_url', DEFAULT_SERVER_URL)
        self.app.statusbar.config(text=f"Transmitting Cell [{self.cell_num}] to Central Cloud Server ({target_url})...")
        
        # Priority 1: Transmit to Central Cloud Server on Render (Zero user-server setup)
        server_online = False
        try:
            import requests
            resp = requests.post(f"{target_url}/api/transmit", json={
                "header": f"SUGANITA_TRANSMIT_HEADER v1.0\nFILE: cell_{self.cell_num}.su\nCLIENT: StructuredNotepad_v4",
                "source_code": code
            }, timeout=4.0)
            if resp.status_code == 200:
                server_online = True
                data = resp.json()
                summary = data.get("summary", {})
                self.app.statusbar.config(text=f"🌐 Cell [{self.cell_num}] Processed via Central Cloud Server ({target_url}).")
        except Exception:
            # Fallback check local port 5006 if cloud endpoint unreachable
            try:
                import requests
                resp = requests.post("http://127.0.0.1:5006/api/transmit", json={
                    "header": f"SUGANITA_TRANSMIT_HEADER v1.0\nFILE: cell_{self.cell_num}.su\nCLIENT: StructuredNotepad_v4",
                    "source_code": code
                }, timeout=2.0)
                if resp.status_code == 200:
                    server_online = True
                    data = resp.json()
                    summary = data.get("summary", {})
                    target_url = "http://127.0.0.1:5006"
                    self.app.statusbar.config(text=f"🌐 Cell [{self.cell_num}] Processed via Local Server Engine.")
            except Exception:
                server_online = False

        # Priority 2: Offline Fallback Mode if cloud server is unreachable
        if not server_online:
            self.app.statusbar.config(text=f"⚠️ Cloud Server Unreachable: Running Cell [{self.cell_num}] in Offline Fallback Mode...")
            summary, su_output = compile_and_run(code, f"cell_{self.cell_num}.su")
        
        # Update Out label and text instantly below the cell!
        mode_prefix = f"🌐 [Cloud Server Mode: {target_url}]\n" if server_online else "⚠️ [Offline Fallback Mode]\n"
        logs_str = mode_prefix + ("\n".join(summary.get('logs', [])) if summary.get('logs') else "Execution Complete")
        self.out_text.config(text=logs_str, fg='#a6e3a1' if server_online else '#f9e2af')

        # Display inline plot graph directly below input code command
        if summary.get('plots'):
            b64_img = summary['plots'][0]['image_b64']
            self._display_inline_b64_image(b64_img)

    def ai_complete_cell(self):
        code = self.text_editor.get("1.0", tk.END).strip()
        completion = self.app.solar_client.complete_code(code)
        self.text_editor.insert(tk.END, f"\n{completion}")
        self._highlight_syntax()

    def delete_cell(self):
        self.app.delete_cell(self)

    def add_cell_below(self):
        self.app.add_cell(after_cell=self)

    def _on_shift_enter(self, event):
        self.evaluate_cell()
        return 'break' # Prevent extra newline insertion

    def _on_ctrl_space(self, event):
        self.ai_complete_cell()
        return 'break'

    def _highlight_syntax(self):
        self.text_editor.tag_remove("keyword", "1.0", tk.END)
        self.text_editor.tag_config("keyword", foreground="#f9e2af", font=('Consolas', 11, 'bold'))

        for kw in DEVANAGARI_KEYWORDS:
            start = "1.0"
            while True:
                pos = self.text_editor.search(kw, start, stopindex=tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(kw)}c"
                self.text_editor.tag_add("keyword", pos, end)
                start = end

    def _display_inline_b64_image(self, b64_str):
        try:
            img_data = base64.b64decode(b64_str)
            image = Image.open(io.BytesIO(img_data))
            image.thumbnail((500, 320))
            photo = ImageTk.PhotoImage(image)
            self.img_label.config(image=photo, text="")
            self.img_label.image = photo
        except Exception as e:
            self.img_label.config(text=f"Plot Error: {e}")


class StructuredNotepadApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Structured Notepad v4 - Suganita Jupyter-Style Interactive Platform")
        self.geometry("1150x800")
        self.configure(bg="#1e1e2e")

        self.solar_client = SolarLLMClient()
        self.protocol_handler = TransmitProtocolHandler()
        self.cells = []

        self._setup_styles()
        self._build_menu()
        self._build_toolbar()
        self._build_scrollable_container()
        self._build_statusbar()

        # Add initial default Suganita notebook cells
        self._load_default_notebook()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')

    def _build_menu(self):
        menubar = tk.Menu(self, bg='#181825', fg='#cdd6f4', activebackground='#89b4fa')
        
        file_menu = tk.Menu(menubar, tearoff=0, bg='#181825', fg='#cdd6f4')
        file_menu.add_command(label="New Cell (+)", command=lambda: self.add_cell())
        file_menu.add_command(label="Run All Cells (Ctrl+Shift+Enter)", command=self.run_all_cells)
        file_menu.add_command(label="Save Notebook (.su)", command=self.save_notebook)
        file_menu.add_command(label="Open Notebook (.su)", command=self.open_notebook)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        leibnitz_menu = tk.Menu(menubar, tearoff=0, bg='#181825', fg='#cdd6f4')
        leibnitz_menu.add_command(label="Evaluate All Cells (F5)", command=self.run_all_cells)
        menubar.add_cascade(label="Leibnitz6 Server", menu=leibnitz_menu)

        ai_menu = tk.Menu(menubar, tearoff=0, bg='#181825', fg='#cdd6f4')
        ai_menu.add_command(label="Solar AI Autocomplete (Ctrl+Space)", command=self.ai_assist_active)
        ai_menu.add_separator()
        ai_menu.add_command(label="Select Custom .gguf Model File...", command=self.select_custom_gguf_model)
        menubar.add_cascade(label="Solar AI Copilot", menu=ai_menu)

        self.config(menu=menubar)

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg='#181825', pady=6, padx=10)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        btn_add = tk.Button(toolbar, text="+ Add Cell", bg='#313244', fg='#cdd6f4', font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, command=lambda: self.add_cell())
        btn_add.pack(side=tk.LEFT, padx=3)

        btn_run_all = tk.Button(toolbar, text="▶ Run All Cells (F5)", bg='#a6e3a1', fg='#11111b', font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, command=self.run_all_cells)
        btn_run_all.pack(side=tk.LEFT, padx=6)

        btn_save = tk.Button(toolbar, text="💾 Save Notebook", bg='#313244', fg='#cdd6f4', font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, command=self.save_notebook)
        btn_save.pack(side=tk.LEFT, padx=3)

        btn_open = tk.Button(toolbar, text="📂 Open Notebook", bg='#313244', fg='#cdd6f4', font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, command=self.open_notebook)
        btn_open.pack(side=tk.LEFT, padx=3)

        btn_ai_all = tk.Button(toolbar, text="✨ Solar Copilot Assist", bg='#f9e2af', fg='#11111b', font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, command=self.ai_assist_active)
        btn_ai_all.pack(side=tk.LEFT, padx=6)

    def _build_scrollable_container(self):
        # Canvas + Scrollbar container for notebook cells
        self.canvas = tk.Canvas(self, bg='#1e1e2e', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.notebook_frame = tk.Frame(self.canvas, bg='#1e1e2e')
        self.notebook_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.notebook_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_statusbar(self):
        self.statusbar = tk.Label(self, text="Suganita Interactive Notebook Environment | Leibnitz6 Ready", bg='#11111b', fg='#a6adc8', anchor='w', padx=10, pady=3, font=('Segoe UI', 9))
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def add_cell(self, after_cell=None, default_code: str = "") -> SuganitaNotebookCell:
        cell_num = len(self.cells) + 1
        cell = SuganitaNotebookCell(self.notebook_frame, cell_num=cell_num, app_reference=self, default_code=default_code)
        
        if after_cell and after_cell in self.cells:
            idx = self.cells.index(after_cell) + 1
            self.cells.insert(idx, cell)
        else:
            self.cells.append(cell)

        self._repack_cells()
        return cell

    def delete_cell(self, cell: SuganitaNotebookCell):
        if cell in self.cells:
            self.cells.remove(cell)
            cell.destroy()
            self._repack_cells()

    def _repack_cells(self):
        for cell in self.notebook_frame.winfo_children():
            cell.pack_forget()

        for idx, cell in enumerate(self.cells, start=1):
            cell.cell_num = idx
            cell.cell_label.config(text=f"In [{idx}]:")
            cell.out_label.config(text=f"Out [{idx}]:")
            cell.pack(fill=tk.X, expand=True, pady=8, padx=5)

    def run_all_cells(self):
        for cell in self.cells:
            cell.evaluate_cell()
        self.statusbar.config(text="Executed All Suganita Cells Successfully.")

    def ai_assist_active(self):
        if self.cells:
            self.cells[-1].ai_complete_cell()

    def select_custom_gguf_model(self):
        filepath = filedialog.askopenfilename(filetypes=[("GGUF LLM Models", "*.gguf"), ("All Files", "*.*")])
        if filepath:
            if self.solar_client.select_gguf_model(filepath):
                model_name = os.path.basename(filepath)
                messagebox.showinfo("GGUF Model Selected", f"Successfully activated GGUF model:\n{model_name}")
                self.statusbar.config(text=f"Active GGUF Model: {model_name}")
            else:
                messagebox.showerror("Error", f"Failed to activate model file:\n{filepath}")

    def save_notebook(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".su", filetypes=[("Suganita Notebooks", "*.su")])
        if filepath:
            code_blocks = [cell.text_editor.get("1.0", tk.END).strip() for cell in self.cells]
            full_content = "\n\n# --- Suganita Cell Divider ---\n\n".join(code_blocks)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            self.statusbar.config(text=f"Saved Notebook: {filepath}")

    def open_notebook(self):
        filepath = filedialog.askopenfilename(filetypes=[("Suganita Notebooks", "*.su"), ("All Files", "*.*")])
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            blocks = content.split("# --- Suganita Cell Divider ---")
            for c in self.cells:
                c.destroy()
            self.cells.clear()
            for block in blocks:
                self.add_cell(default_code=block.strip())
            self.statusbar.config(text=f"Loaded Notebook: {filepath}")

    def _load_default_notebook(self):
        c1_code = """# Cell 1: Initialize Signal Labels & Parameters
लिखो "REALInstitute"
लिखो "Leibnitz6_Interactive_Notebook"
प्रवेश "Sinusoidal_12Hz_Input_Buffer"
"""
        c2_code = """# Cell 2: Spectral Analysis & Inline Spectrum Graph
रुको ५००
रूपरेखा "Sinusoidal_12Hz_Spectral_Analysis"
निरोध
"""
        self.add_cell(default_code=c1_code)
        self.add_cell(default_code=c2_code)

if __name__ == "__main__":
    app = StructuredNotepadApp()
    app.mainloop()
