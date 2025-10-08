# Example notebook: https://colab.research.google.com/drive/1YKniUVbEKglCmYQV0I6tia1QObBgX3xB?usp=sharing
import os
import sys
from enum import Enum
from typing import Optional

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    PhaseResultsUtils,
)
from aiq_platform_api.env import ATTACKIQ_PLATFORM_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_phase_results(
    client: AttackIQRestClient,
    assessment_id: str,
    project_run_id: Optional[str] = None,
    result_summary_id: Optional[str] = None,
    limit: Optional[int] = 10,
):
    logger.info(f"Listing up to {limit} phase results ...")
    count = 0

    for phase_result in PhaseResultsUtils.get_phase_results(
        client,
        assessment_id=assessment_id,
        project_run_id=project_run_id,
        result_summary_id=result_summary_id,
        limit=limit,
    ):
        count += 1
        logger.info(f"Phase Result {count}:")
        logger.info(f"  Result ID: {phase_result.get('id')}")
        phase = phase_result.get("phase")
        if phase:
            logger.info(f"  Phase ID: {phase.get('id')}")
            logger.info(f"  Phase Name: {phase.get('name')}")
        logger.info(f"  Created: {phase_result.get('created')}")
        logger.info(f"  Modified: {phase_result.get('modified')}")
        logger.info(f"  Outcome: {phase_result.get('outcome_description')}")
        logger.info("---")
    logger.info(f"Total phase results listed: {count}")


def test_list_phase_results(client: AttackIQRestClient, assessment_id: str):
    """Test listing phase results for an assessment."""
    if not assessment_id:
        logger.error("ATTACKIQ_ATOMIC_ASSESSMENT_ID environment variable not set.")
        return
    list_phase_results(client, assessment_id, limit=100)


def run_test(choice: "TestChoice", client: AttackIQRestClient, assessment_id: str):
    """Run the selected test."""
    test_functions = {
        TestChoice.LIST_PHASE_RESULTS: lambda: test_list_phase_results(client, assessment_id),
    }

    test_func = test_functions.get(choice)
    if test_func:
        test_func()
    else:
        logger.error(f"Unknown test choice: {choice}")


if __name__ == "__main__":
    if not ATTACKIQ_PLATFORM_URL or not ATTACKIQ_PLATFORM_API_TOKEN:
        logger.error("Missing ATTACKIQ_PLATFORM_URL or ATTACKIQ_PLATFORM_API_TOKEN")
        sys.exit(1)

    class TestChoice(Enum):
        LIST_PHASE_RESULTS = "list_phase_results"

    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_PLATFORM_API_TOKEN)
    assessment_id = os.environ.get("ATTACKIQ_ATOMIC_ASSESSMENT_ID")

    # Change this to test different functionalities
    choice = TestChoice.LIST_PHASE_RESULTS

    run_test(choice, client, assessment_id)
