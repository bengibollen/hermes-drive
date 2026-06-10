from __future__ import annotations

import uvicorn

from hermes_drive.api.app import create_app

app = create_app()


def run() -> None:
    uvicorn.run("hermes_drive.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
