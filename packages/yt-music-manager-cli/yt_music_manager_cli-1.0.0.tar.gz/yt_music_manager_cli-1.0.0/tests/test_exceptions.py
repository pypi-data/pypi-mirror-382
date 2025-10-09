import logging
from pathlib import Path

import pytest

from yt_music_manager_cli.exceptions import (
    ConfigurationError,
    ErrorCollector,
    FileSystemError,
    YTMusicManagerCLIError,
    ProgressTracker,
    ValidationError,
    handle_errors,
    retry_on_exception,
    safe_cleanup,
    validate_file_path,
    validate_url,
)


def test_custom_exception_to_dict():
    error = ConfigurationError("bad config", error_code="cfg", context={"k": "v"})
    data = error.to_dict()
    assert data["error_code"] == "cfg"
    assert data["context"] == {"k": "v"}


def test_retry_on_exception_success():
    calls = {"count": 0}

    @retry_on_exception(max_attempts=3, delay=0, backoff=1, exceptions=(ValueError,))
    def flaky():
        calls["count"] += 1
        if calls["count"] < 2:
            raise ValueError("fail")
        return "ok"

    assert flaky() == "ok"
    assert calls["count"] == 2

    @retry_on_exception(max_attempts=2, delay=0, backoff=1, exceptions=(ValueError,))
    def always_fail():
        raise ValueError("nope")

    with pytest.raises(ValueError):
        always_fail()


def test_handle_errors_decorator(caplog):
    caplog.set_level(logging.ERROR)

    @handle_errors(
        logger_name="yt_music_manager_cli.test",
        default_return="fallback",
        reraise=False,
    )
    def safe_function():
        raise ValidationError("invalid")

    assert safe_function() == "fallback"
    assert any(
        "YT Music Manager CLI error" in record.message for record in caplog.records
    )

    @handle_errors(logger_name="yt_music_manager_cli.test2")
    def unsafe():
        raise RuntimeError("boom")

    with pytest.raises(YTMusicManagerCLIError):
        unsafe()


def test_error_collector_and_progress_tracker(caplog):
    collector = ErrorCollector(max_errors=2)
    try:
        raise ValidationError("bad")
    except ValidationError as exc:
        collector.add_error(exc, context={"item": 1})

    collector.add_warning("careful")
    summary = collector.get_error_summary()
    assert summary["total_errors"] == 1
    assert summary["total_warnings"] == 1

    logger = logging.getLogger("yt_music_manager_cli.errors")
    collector.log_summary(logger)

    tracker = ProgressTracker(total_items=2, description="Download")
    tracker.increment_completed()
    tracker.increment_failed(error=ValidationError("bad"), context={"item": 2})
    assert tracker.get_progress_percent() == 100.0
    assert tracker.is_complete() is True
    tracker.interrupt()
    assert tracker.is_interrupted() is True
    summary = tracker.get_summary()
    assert summary["failed_items"] == 1


def test_validate_url_and_file_path(tmp_path):
    with pytest.raises(ValidationError):
        validate_url("https://example.com")

    with pytest.raises(ValidationError):
        validate_url("https://youtube.com/watch?v=abc")

    valid_url = "https://www.youtube.com/playlist?list=PL123"
    validate_url(valid_url)

    with pytest.raises(FileSystemError):
        validate_file_path(str(tmp_path / "missing"), must_exist=True)

    directory = tmp_path / "dir"
    directory.mkdir()
    validate_file_path(str(directory), must_exist=True, must_be_writable=True)

    file_path = directory / "file.txt"
    file_path.write_text("data")
    with pytest.raises(FileSystemError):
        validate_file_path(str(file_path), must_be_writable=True)


def test_safe_cleanup(tmp_path):
    called = {"count": 0}

    def cleanup():
        called["count"] += 1

    safe_cleanup(
        cleanup, logging.getLogger("yt_music_manager_cli.cleanup"), "test cleanup"
    )
    assert called["count"] == 1
