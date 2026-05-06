from __future__ import annotations

from app.core.settings import get_settings
from app.tui.app import AStockTUI
from app.tui.client import BackendClient


def run() -> None:
    settings = get_settings()
    client = BackendClient(settings.tui_backend_url, timeout=settings.request_timeout)
    app = AStockTUI(client, session_id=settings.tui_session_id)
    app.run()


if __name__ == "__main__":
    run()

