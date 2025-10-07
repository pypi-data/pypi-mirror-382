import os
from echolog import Logger


def test_basic_logging(tmp_path, monkeypatch):
    # Redirect logs folder to tmp path
    monkeypatch.setenv("ECHOLOG_LOGS_FOLDER", str(tmp_path))
    logger = Logger("test")
    logger.info("hello world")
    logs = logger.get_logs()
    # Should contain at least one line
    assert any("hello world" in line for line in logs)
