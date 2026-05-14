"""Build automation for llm-platform-library."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> int:
    """Clean, validate, audit, and build the library."""

    try:
        print_step("Starting llm-platform-library build")
        clean_build_artifacts()
        run_commands()
        print_step("Build completed successfully")
        return 0
    except subprocess.CalledProcessError as exc:
        print_step(f"Command failed with exit code {exc.returncode}: {exc.cmd}")
        return exc.returncode
    except OSError as exc:
        print_step(f"Build failed due to file system error: {exc}")
        return 1


def clean_build_artifacts() -> None:
    """Delete old build folders and egg-info folders."""

    print_step("Cleaning old build artifacts")
    for folder_name in ("build", "dist"):
        remove_path(PROJECT_ROOT / folder_name)
    for egg_info_path in PROJECT_ROOT.glob("*.egg-info"):
        remove_path(egg_info_path)


def remove_path(path: Path) -> None:
    """Remove a path if it exists."""

    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def run_commands() -> None:
    """Run quality and build commands in order."""

    commands = [
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "setuptools",
            "wheel",
        ],
        [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
        [sys.executable, "-m", "pytest"],
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "mypy", "llm_platform_library"],
        [sys.executable, "-m", "pip_audit"],
        [sys.executable, "-m", "pytest", "--cov=llm_platform_library"],
        [sys.executable, "-m", "build"],
    ]
    for command in commands:
        run_command(command)


def run_command(command: list[str]) -> None:
    """Run one subprocess command and stop on failure."""

    print_step(f"Running: {' '.join(command)}")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def print_step(message: str) -> None:
    """Print build progress."""

    print(f"[llm-platform-library build] {message}")


if __name__ == "__main__":
    raise SystemExit(main())

