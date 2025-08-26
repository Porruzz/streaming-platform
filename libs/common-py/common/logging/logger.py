# libs/common-py/common/logging/logger.py
import logging, structlog

def setup_logging(level: str = "INFO"):
    logging.basicConfig(level=level)
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)))
