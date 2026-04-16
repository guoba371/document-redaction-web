from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class DocToDocxConverter:
    def __init__(self) -> None:
        self.mac_command = "textutil"
        self.linux_commands = ("soffice", "libreoffice", "lowriter")

    def convert(self, input_path: Path, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        expected_output = output_dir / f"{input_path.stem}.docx"
        if self._try_textutil(input_path, expected_output):
            return expected_output
        if self._try_libreoffice(input_path, output_dir, expected_output):
            return expected_output

        if not expected_output.exists():
            raise RuntimeError(
                "当前环境缺少可用的 .doc 转换工具。"
                "macOS 需要 textutil，Linux/Render 需要 LibreOffice（soffice）。"
            )

        return expected_output

    def _try_textutil(self, input_path: Path, expected_output: Path) -> bool:
        executable = shutil.which(self.mac_command)
        if not executable:
            return False

        subprocess.run(
            [
                executable,
                "-convert",
                "docx",
                str(input_path),
                "-output",
                str(expected_output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return expected_output.exists()

    def _try_libreoffice(
        self,
        input_path: Path,
        output_dir: Path,
        expected_output: Path,
    ) -> bool:
        executable = next(
            (shutil.which(command) for command in self.linux_commands if shutil.which(command)),
            None,
        )
        if not executable:
            return False

        subprocess.run(
            [
                executable,
                "--headless",
                "--convert-to",
                "docx",
                "--outdir",
                str(output_dir),
                str(input_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return expected_output.exists()
