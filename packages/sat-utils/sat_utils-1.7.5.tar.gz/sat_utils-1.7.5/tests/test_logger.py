import logging
import os
from io import StringIO
from unittest import mock

from sat.logs import ExtraTextFormatter

TMP_FILE = "/tmp/test.log"


@mock.patch.dict(os.environ, {"USELESS": "VALUE"}, clear=True)
def test_default_logger(caplog):
    """Test the default logger"""
    from sat.logs import SATLogger

    logger = SATLogger()
    logger.info("Test message")
    assert "Test message" in caplog.text
    logger.debug("DEBUG message")
    assert "DEBUG message" not in caplog.text
    logger.error("ERROR message")
    assert "ERROR message" in caplog.text


@mock.patch.dict(os.environ, {"DEBUG": "1"}, clear=True)
def test_debug_logger(caplog):
    """Test the debug logger"""
    from sat.logs import SATLogger

    logger = SATLogger()
    logger.debug("DEBUG message")
    assert "DEBUG message" in caplog.text


def test_add_handlers(caplog):
    """Test adding handlers to the logger"""
    from sat.logs import SATLogger

    logger = SATLogger()
    logger.add_handlers([(logging.FileHandler(TMP_FILE), logging.Formatter("%(message)s"))])
    logger.info("Test message")
    assert "Test message" in caplog.text
    assert os.path.exists(TMP_FILE)


def test_django_logger(caplog):
    from sat.logs import DjangoSATLogger

    logger = DjangoSATLogger()
    logger.logger.setLevel(logging.INFO)
    logger.info("Test info")
    assert "Test info" in caplog.text


def test_extra_formatter():
    test_stream = StringIO()
    handler = logging.StreamHandler(test_stream)
    formatter = ExtraTextFormatter()
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info("test", extra={"cid": "test"})
    test_stream.seek(0)
    log_line = test_stream.read()
    assert "cid=test" in log_line


def test_all_args_extra_formatter():
    test_stream = StringIO()
    handler = logging.StreamHandler(test_stream)
    formatter = ExtraTextFormatter()
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info(
        "test",
        extra={"cid": "test", "first_name": "test-first-name", "last_name": "test-last-name"},
    )
    test_stream.seek(0)
    log_line = test_stream.read()
    assert "cid=test" in log_line
    assert "first_name=test-first-name" in log_line
    assert "last_name=test-last-name" in log_line
