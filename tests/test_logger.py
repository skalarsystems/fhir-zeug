import logging
from fhirzeug import logger
from testfixtures import LogCapture


def test_setup_logging():
    """Check FHIRparser logger."""
    logger.setup_logging()
    assert logger.logger.level == logging.DEBUG

    with LogCapture() as l:
        logger.logger.info("Test message")

    l.check(("fhirparser", "INFO", "Test message"),)
