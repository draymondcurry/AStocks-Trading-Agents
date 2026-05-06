import shutil
import uuid
from pathlib import Path

from app.services.memory.store import MemoryStore


async def test_memory_store_creates_missing_parent_directory():
    test_root = Path("pytest-cache-files-memory-store") / uuid.uuid4().hex
    db_path = test_root / "nested" / "data" / "memory.db"
    store = MemoryStore(str(db_path))

    try:
        await store.initialize()
        await store.close()

        assert db_path.exists()
    finally:
        shutil.rmtree(test_root.parent, ignore_errors=True)
