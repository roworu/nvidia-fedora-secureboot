import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QCheckBox, QPushButton, QTextEdit, QLabel
)
from PyQt6.QtCore import QProcess, Qt


SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "setup.py")


class InstallerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NVIDIA Driver Installer")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)

        # --- Top checkboxes ---
        top = QHBoxLayout()
        self.cuda_box = QCheckBox("Install CUDA")
        self.cuda_box.setChecked(True)
        self.gsp_box = QCheckBox("Disable GSP Firmware")
        self.gsp_box.setChecked(True)

        top.addWidget(self.cuda_box)
        top.addWidget(self.gsp_box)
        layout.addLayout(top)

        # --- Install button ---
        self.install_btn = QPushButton("INSTALL")
        self.install_btn.setFixedHeight(40)
        self.install_btn.clicked.connect(self.on_install)
        layout.addWidget(self.install_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # --- Logs box ---
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # --- QProcess handle ---
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.on_stdout)
        self.process.readyReadStandardError.connect(self.on_stderr)
        self.process.finished.connect(self.on_finished)

    # ------------------------------------------------------

    def on_install(self):
        self.log_area.clear()
        self.log("Starting installation...\n")

        env = os.environ.copy()
        env["INSTALL_CUDA"] = "1" if self.cuda_box.isChecked() else "0"
        env["DISABLE_GSP"] = "1" if self.gsp_box.isChecked() else "0"

        self.log(f"INSTALL_CUDA={env['INSTALL_CUDA']}  DISABLE_GSP={env['DISABLE_GSP']}\n\n")

        # ----------------------------
        # pkexec python3 nvidia_installer.py
        # ----------------------------
        cmd = ["pkexec", sys.executable, SCRIPT_PATH]

        # Start process
        self.process.setProcessEnvironment(
            QProcess.ProcessEnvironment.fromSystemEnvironment()
        )

        # Inject our environment variables
        for k, v in env.items():
            self.process.processEnvironment().insert(k, v)

        self.process.start(cmd[0], cmd[1:])

        if not self.process.waitForStarted(2000):
            self.log("ERROR: Could not start the installer process.\n")

    # ------------------------------------------------------

    def on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.log(data)

    def on_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.log(data)

    def on_finished(self, exit_code, status):
        self.log(f"\n[process finished with exit code {exit_code}]\n")

    # ------------------------------------------------------

    def log(self, text):
        self.log_area.insertPlainText(text)
        self.log_area.moveCursor(self.log_area.textCursor().End)


# ----------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    win = InstallerUI()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
