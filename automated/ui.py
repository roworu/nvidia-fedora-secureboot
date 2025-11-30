import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import os
import sys


SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "setup.py")


def stream_process(cmd, env, log_widget):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )

    for line in process.stdout:
        log_widget.insert(tk.END, line)
        log_widget.see(tk.END)

    process.wait()
    log_widget.insert(tk.END, f"\n[exit code: {process.returncode}]\n")
    log_widget.see(tk.END)


def run_async(cmd, env, log_widget):
    t = threading.Thread(
        target=stream_process,
        args=(cmd, env, log_widget),
        daemon=True
    )
    t.start()


class InstallerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NVIDIA Driver Installer")
        self.geometry("650x500")

        top = ttk.Frame(self)
        top.pack(pady=10)

        self.cuda_var = tk.BooleanVar(value=True)
        self.gsp_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(top, text="Install CUDA", variable=self.cuda_var).grid(row=0, column=0, padx=20)
        ttk.Checkbutton(top, text="Disable GSP", variable=self.gsp_var).grid(row=0, column=1, padx=20)

        ttk.Button(self, text="INSTALL", command=self.on_install)\
            .pack(pady=20)

        self.log_area = ScrolledText(self, height=18)
        self.log_area.pack(fill="both", expand=True, padx=10, pady=10)

    def on_install(self):
        env = os.environ.copy()
        env["INSTALL_CUDA"] = "1" if self.cuda_var.get() else "0"
        env["DISABLE_GSP"] = "1" if self.gsp_var.get() else "0"

        self.log_area.insert(tk.END, "Starting installation...\n")
        self.log_area.insert(
            tk.END,
            f"INSTALL_CUDA={env['INSTALL_CUDA']}  DISABLE_GSP={env['DISABLE_GSP']}\n\n"
        )
        self.log_area.see(tk.END)

        cmd = [
            "pkexec",
            sys.executable,
            SCRIPT_PATH
        ]

        run_async(cmd, env, self.log_area)


if __name__ == "__main__":
    InstallerUI().mainloop()
