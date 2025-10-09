from . import utils_old
import sys
import logging

logging.basicConfig(
    level=logging.INFO,  # Or DEBUG for more details
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)