import logging

from matflow import MatFlow
from hpcflow.api import *

logger = logging.getLogger(__name__)


def parameter_search():
    logger.info(f"parameter_search; is_venv: {MatFlow.run_time_info.is_venv}")
