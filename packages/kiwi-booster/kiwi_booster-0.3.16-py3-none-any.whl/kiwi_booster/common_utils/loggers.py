import logging
import os
from typing import Tuple

import structlog


def get_loggers() -> Tuple[structlog.stdlib.BoundLogger, logging.Logger]:
    """
    Get the logger for the application using structlog, the logger is configured
    depending on the environment

    Returns:
        A tuple containing the Structlog logger for structured logging and
        Info logger for normal logging

    """
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

    if os.environ["ENV"] == "cloud":
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.render_to_log_kwargs,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.format_exc_info,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    request_logger = structlog.get_logger()
    info_logger = logging.getLogger("info")

    return request_logger, info_logger
