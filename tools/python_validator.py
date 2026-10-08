import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))



class PythonValidator:

    def __init__(self, workspace_dir: str | Path):
        self.workspace_dir = Path(workspace_dir).resolve()

    def validate(self, file_path: str | Path) -> dict:
        """
        Execute a Python file and return validation information.

        Returns:
            {
                "ok": bool,
                "file": str,
                "return_code": int,
                "stdout": str,
                "stderr": str,
            }
        """

        file_path = Path(file_path)

        # اگر مسیر نسبی بود، نسبت به workspace حسابش کن
        if not file_path.is_absolute():
            file_path = self.workspace_dir / file_path

        file_path = file_path.resolve()

        # جلوگیری از اجرای فایل خارج از workspace
        try:
            file_path.relative_to(self.workspace_dir)
        except ValueError:
            return {
                "ok": False,
                "file": str(file_path),
                "return_code": -1,
                "stdout": "",
                "stderr": "File is outside the Python workspace.",
            }

        # بررسی وجود فایل
        if not file_path.exists():
            return {
                "ok": False,
                "file": str(file_path),
                "return_code": -1,
                "stdout": "",
                "stderr": f"File not found: {file_path}",
            }

        # بررسی Python file
        if file_path.suffix.lower() != ".py":
            return {
                "ok": False,
                "file": str(file_path),
                "return_code": -1,
                "stdout": "",
                "stderr": "Only .py files can be validated.",
            }

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    str(file_path),
                ],
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=10,
            )

            return {
                "ok": result.returncode == 0,
                "file": str(file_path),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:

            return {
                "ok": False,
                "file": str(file_path),
                "return_code": -1,
                "stdout": "",
                "stderr": "Execution timed out after 10 seconds.",
            }

        except Exception as e:

            return {
                "ok": False,
                "file": str(file_path),
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
            }