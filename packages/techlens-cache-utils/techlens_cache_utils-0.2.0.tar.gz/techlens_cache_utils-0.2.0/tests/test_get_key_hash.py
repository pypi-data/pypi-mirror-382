import os
import datetime
import tempfile
from pathlib import Path
from time import sleep

from techlens_cache_utils.main import Cache


def test_two_writes_same_hash():
    test_db = Path("test3.db")
    if test_db.exists():
        os.remove(test_db)
    assert not test_db.exists(), "Test3 DB exists"
    cache = Cache("test3.db")
    file1 = Path("./tests/fixtures/file1.txt")
    file2 = Path("./tests/fixtures/file2.txt")
    cache.set(file1, {"file": str(file1)})
    file1data = cache.get(file1)
    assert file1data["file"] == str(file1), "Invalid file1"
    cache.set(file2, {"file": str(file2)})
    file2data = cache.get(file2)
    assert file2data["file"] == str(file2), "Invalid file2"
    os.remove(test_db)
    assert not test_db.exists(), "Test DB not removed"
