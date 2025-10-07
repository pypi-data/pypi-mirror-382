import logging

from festo_python_logging import configure_logging

logger = logging.getLogger(__name__)

configure_logging(verbose=True)

logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")

verys = "very " * 50
logger.debug(f"This is a {verys} long  debug message.")
logger.info(f"This is an {verys} long  info message.")
logger.warning(f"This is a {verys} long  warning message.")
logger.error(f"This is an {verys} long  error message.")
some_list = [i for i in range(100)]
logger.debug(f"{some_list}")
