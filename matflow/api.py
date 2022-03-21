import logging

from hpcflow import RUN_TIME_INFO
from hpcflow.api import *

logger = logging.getLogger(__name__)


def parameter_search():
    logger.info(f"parameter_search; is_venv: {RUN_TIME_INFO.is_venv}")
