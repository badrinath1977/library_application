from __future__ import annotations

import os
from pathlib import Path

import uvicorn


def main() -> None:
    os.chdir(Path(__file__).resolve().parent)
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8010")),
        reload=os.getenv("RELOAD", "false").lower() in {"1", "true", "yes", "on"},
        log_level=os.getenv("UVICORN_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()

