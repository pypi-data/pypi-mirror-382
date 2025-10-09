import logging
from types import SimpleNamespace

from yt_music_manager_cli import logging_utils


def test_yt_music_manager_cli_logger_initialization(
    tmp_path, reset_settings, monkeypatch
):
    reset_settings.logging.log_file = str(
        tmp_path / "logs" / "yt_music_manager_cli.log"
    )
    reset_settings.logging.level = "DEBUG"

    # Ensure Rich console doesn't try to write to real stdout during tests
    fake_console = SimpleNamespace(print=lambda *args, **kwargs: None)
    monkeypatch.setattr(logging_utils, "Console", lambda theme=None: fake_console)
    monkeypatch.setattr(
        logging_utils, "RichHandler", lambda **kwargs: logging.StreamHandler()
    )

    manager = logging_utils.YTMusicManagerCLILogger()
    logger = manager.get_logger(
        "yt_music_manager_cli.test", context={"request_id": "123"}
    )
    logger.debug("test message")

    # Test context filter application
    manager.add_context("yt_music_manager_cli.test", {"user": "tester"})
    logger.info("context message")

    # Test helper methods
    manager.log_api_call(
        "yt_music_manager_cli.api",
        "yt",
        "/playlists",
        status_code=200,
        response_time=0.12,
    )
    manager.log_download_progress(
        "yt_music_manager_cli.download", "Song", 50.0, speed="1MiB/s", eta="00:01"
    )
    manager.log_sync_summary("yt_music_manager_cli.sync", "Playlist", 1, 0, 0, 0, 1.5)

    manager.print_banner("YT Music Manager CLI", "1.0.2")
    manager.print_success("All good")
    manager.print_warning("Be careful")
    manager.print_error("Something failed")
    manager.print_info("FYI")

    # JSON formatter coverage
    formatter = logging_utils.JsonFormatter()
    record = logging.LogRecord(
        name="yt_music_manager_cli.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "message" in formatted

    # Size parsing
    assert manager._parse_size("10MB") == 10 * 1024 * 1024
    # Unsupported suffixes fall back to default size
    assert manager._parse_size("5GB") == 10 * 1024 * 1024
    assert manager._parse_size("invalid") == 10 * 1024 * 1024

    # Global helpers
    logging_utils._logger_manager = manager
    logging_utils.log_exception(ValueError("boom"))
    assert logging_utils.get_console() is manager.console
    logging_utils.setup_logging()
    assert isinstance(
        logging_utils.get_logger("yt_music_manager_cli.other"), logging.Logger
    )
