import os

import pytest
from fastapi.testclient import TestClient

os.environ["ENABLE_MOCKS"] = "true"
os.environ["MEMORY_DB_PATH"] = "./data/test_memory.db"

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

