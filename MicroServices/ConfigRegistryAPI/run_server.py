from __future__ import annotations

import os
from pathlib import Path

import uvicorn


def main() -> None:
    service_root = Path(__file__).resolve().parent
    os.chdir(service_root)

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("RELOAD", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload_enabled,
        log_level=os.getenv("UVICORN_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()

