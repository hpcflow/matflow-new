import logging

from matflow import MatFlow

logger = logging.getLogger(__name__)


make_workflow = MatFlow.make_workflow


def parameter_search():
    logger.info(f"parameter_search ; is_venv: {MatFlow.run_time_info.is_venv}")
