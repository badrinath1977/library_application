"""Run the TestLibraryApp consumer application."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Locate the app folder and run app.py safely."""

    app_dir = Path(__file__).resolve().parent
    app_file = app_dir / "app.py"

    try:
        completed_process = subprocess.run(
            [sys.executable, str(app_file)],
            cwd=app_dir,
            check=False,
        )
    except OSError as ex:
        print(f"Failed to start test application: {ex}")
        return 1

    return completed_process.returncode


if __name__ == "__main__":
    raise SystemExit(main())

