#!/usr/bin/env python3
# gui.py
# Very small Tkinter GUI to control PhantomPort (server + scan)
import subprocess
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import sys
import os

PHANTOM = os.path.join(os.path.dirname(__file__), 'phantomport.py')

class App:
    def __init__(self, root):
        self.root = root
        root.title("PhantomPort — Control")
        self.text = ScrolledText(root, width=80, height=20)
        self.text.pack(padx=8, pady=6)
        frame = tk.Frame(root)
        frame.pack(pady=4)
        self.server_btn = tk.Button(frame, text="Start Server", command=self.start_server)
        self.server_btn.grid(row=0, column=0, padx=4)
        tk.Label(frame, text="Scan target:").grid(row=0, column=1, padx=4)
        self.target_entry = tk.Entry(frame, width=20)
        self.target_entry.insert(0, "127.0.0.1")
        self.target_entry.grid(row=0, column=2, padx=4)
        self.scan_btn = tk.Button(frame, text="Scan", command=self.start_scan)
        self.scan_btn.grid(row=0, column=3, padx=4)
        self.proc = None
        self.server_thread = None

    def append(self, s):
        self.text.insert(tk.END, s + "\n")
        self.text.see(tk.END)

    def start_server(self):
        if self.server_thread and self.server_thread.is_alive():
            self.append("[GUI] Server already running.")
            return
        def run():
            self.append("[GUI] Server thread starting...")
            os.execv(sys.executable, [sys.executable, PHANTOM, "server"])
        # run server in a separate process-like thread (execv replaces process, so use subprocess)
        self.server_thread = threading.Thread(target=self._server_process, daemon=True)
        self.server_thread.start()

    def _server_process(self):
        self.append("[GUI] Launching server subprocess...")
        p = subprocess.Popen([sys.executable, PHANTOM, "server"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            self.append("[Server] " + line.rstrip())
        p.wait()
        self.append("[GUI] Server stopped.")

    def start_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            self.append("[GUI] Enter target.")
            return
        def run_scan():
            self.append(f"[GUI] Scanning {target} ...")
            p = subprocess.Popen([sys.executable, PHANTOM, "scan", target, "1-1024", "60"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in p.stdout:
                self.append("[Scanner] " + line.rstrip())
            p.wait()
            self.append("[GUI] Scan finished.")
        t = threading.Thread(target=run_scan, daemon=True)
        t.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
