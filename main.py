from __future__ import annotations

import os

from nicegui import ui

from club_strive.config import APP_NAME
from club_strive.views import build_index


@ui.page("/")
def index() -> None:
    build_index()


port = int(os.getenv("PORT", "8080"))

ui.run(
    title=APP_NAME,
    storage_secret=os.getenv("STORAGE_SECRET", "club-strive-nicegui-secret"),
    host="0.0.0.0",
    port=port,
    reload=False,
)
