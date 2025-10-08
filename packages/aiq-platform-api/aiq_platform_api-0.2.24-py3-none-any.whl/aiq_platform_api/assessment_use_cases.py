# Example notebook: https://colab.research.google.com/drive/1XpDkCMb1myskcQOILK6XaaF1g0a_8666?usp=sharing
import os
import sys
from enum import Enum
from typing import Optional, Dict, Any, List

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    AssessmentUtils,
    AssessmentExecutionStrategy,
)
from aiq_platform_api.env import ATTACKIQ_PLATFORM_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_assessments(client: AttackIQRestClient, limit: Optional[int] = 10) -> int:
    """List assessments with basic information."""
    logger.info(f"Listing up to {limit} assessments")
    count = 0

    for assessment in AssessmentUtils.get_assessments(client, limit=limit):
        count += 1
        logger.info(f"Assessment {count}:")
        logger.info(f"  ID: {assessment.get('id', 'N/A')}")
        logger.info(f"  Name: {assessment.get('name', 'N/A')}")
        logger.info(f"  Status: {assessment.get('status', 'N/A')}")
        logger.info("---")

    logger.info(f"Total assessments listed: {count}")
    return count


def get_assessment_by_id(client: AttackIQRestClient, assessment_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about an assessment by ID."""
    logger.info(f"Getting assessment with ID: {assessment_id}")
    assessment = AssessmentUtils.get_assessment_by_id(client, assessment_id)

    if assessment:
        logger.info(f"Assessment Name: {assessment.get('name')}")
        logger.info(f"Is Attack Graph: {assessment.get('is_attack_graph')}")  # Add more fields as needed

    return assessment


def list_assessment_runs(client: AttackIQRestClient, assessment_id: str, limit: Optional[int] = 10):
    """List recent runs for an assessment."""
    logger.info(f"Listing up to {limit} runs for assessment {assessment_id}")
    count = 0

    for run in AssessmentUtils.list_assessment_runs(client, assessment_id, limit=limit):
        count += 1
        logger.info(f"Run {count}:")
        logger.info(f"  ID: {run.get('id', 'N/A')}")
        logger.info(f"  Created: {run.get('created_at', 'N/A')}")
        logger.info(f"  Scenario Jobs In Progress: {run.get('scenario_jobs_in_progress', 'N/A')}")
        logger.info(f"  Integration Jobs In Progress: {run.get('integration_jobs_in_progress', 'N/A')}")
        logger.info("---")

    return count


def run_and_monitor_assessment(
    client: AttackIQRestClient,
    assessment_id: str,
    assessment_version: int,
    timeout: int = 600,
    check_interval: int = 5,
) -> Optional[str]:
    """Run an assessment and wait for it to complete."""
    logger.info(f"Running assessment {assessment_id} and monitoring completion")

    try:
        # Start the assessment
        run_id = AssessmentUtils.run_assessment(client, assessment_id, assessment_version)
        logger.info(f"Assessment started with run ID: {run_id}")

        # Wait for completion
        without_detection = True
        completed = AssessmentUtils.wait_for_run_completion(
            client, assessment_id, run_id, timeout, check_interval, without_detection
        )

        if completed:
            logger.info(f"Assessment run {run_id} completed successfully")
            return run_id
        else:
            logger.warning(f"Assessment run {run_id} did not complete within {timeout} seconds")
            return None

    except Exception as e:
        logger.error(f"Error running assessment: {str(e)}")
        return None


def get_run_results(
    client: AttackIQRestClient, run_id: str, assessment_version: int, limit: Optional[int] = 10
) -> List[Dict[str, Any]]:
    """Get results for a completed run and return them as a list."""
    logger.info(f"Getting results for run {run_id}")

    results_generator = AssessmentUtils.get_results_by_run_id(client, run_id, assessment_version, limit=limit)
    collected_results = []
    for i, result in enumerate(results_generator):
        logger.info(f"Result {i + 1}:")
        logger.info(f"  ID: {result.get('id', 'N/A')}")
        logger.info(f"  Outcome: {result.get('outcome', 'N/A')}")
        logger.info(f"  Start: {result.get('started_at', result.get('start_time', 'N/A'))}")
        logger.info(f"  End: {result.get('ended_at', result.get('end_time', 'N/A'))}")
        logger.info("---")
        collected_results.append(result)
    return collected_results


def get_detailed_result(
    client: AttackIQRestClient, result_id: str, assessment_version: int
) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific result, including intermediate results."""
    logger.info(f"Getting detailed information for result {result_id}")
    result = AssessmentUtils.get_result_details(client, result_id, assessment_version)

    if not result:
        logger.error(f"Could not retrieve detailed result for result ID: {result_id}")
        return None

    logger.info("--- Detailed Result ---")
    logger.info(f"  Result ID: {result.get('id', 'N/A')}")
    logger.info(f"  Overall Outcome: {result.get('outcome', 'N/A')}")
    logger.info(f"  Detection Outcome: {result.get('detection_outcome', 'N/A')}")
    logger.info(f"  Run Started At: {result.get('run_started_at', 'N/A')}")

    # Log intermediate results
    intermediate_results = result.get("intermediate_results")
    if intermediate_results and isinstance(intermediate_results, list):
        logger.info("--- Intermediate Results (Nodes/Steps) ---")
        for i, step in enumerate(intermediate_results):
            logger.info(f"  Step {i + 1}:")
            logger.info(f"    Node ID: {step.get('node_id', 'N/A')}")
            logger.info(f"    Scenario Name: {step.get('scenario_name', 'N/A')}")
            logger.info(f"    Outcome: {step.get('outcome', 'N/A')}")

    return result


def list_assets_in_assessment(client: AttackIQRestClient, assessment_id: str, limit: Optional[int] = 10):
    """List assets associated with an assessment."""
    logger.info(f"Listing assets for assessment {assessment_id}")
    count = 0

    for asset in AssessmentUtils.get_assets_in_assessment(client, assessment_id, limit=limit):
        count += 1
        logger.info(f"Asset {count}:")
        logger.info(f"  ID: {asset.get('id', 'N/A')}")
        logger.info(f"  Name: {asset.get('name', 'N/A')}")
        logger.info(f"  Type: {asset.get('type', 'N/A')}")
        logger.info(f"  IP Address: {asset.get('ipv4_address', 'N/A')}")
        logger.info("---")

    return count


def assessment_workflow_demo(client: AttackIQRestClient, assessment_id: str, run_assessment: bool):
    """Demonstrate a complete assessment workflow."""
    logger.info(f"Starting assessment workflow demo for assessment {assessment_id}")

    # Step 1: Get assessment metadata
    assessment = get_assessment_by_id(client, assessment_id)
    if not assessment:
        logger.error("Could not get assessment metadata. Aborting workflow.")
        return

    # Step 2: List recent runs
    list_assessment_runs(client, assessment_id)

    # Step 3: Run the assessment and wait for completion
    run_id = None
    assessment_version = assessment["version"]
    if run_assessment:
        run_id = run_and_monitor_assessment(client, assessment_id, assessment_version, timeout=300, check_interval=5)

    # If we didn't run an assessment or it didn't complete, get the most recent run
    if not run_id:
        run = AssessmentUtils.get_most_recent_run_status(client, assessment_id)
        if not run:
            logger.error("No runs found for assessment. Aborting workflow.")
            return
        run_id = run.get("id")

    # Step 4: Get results for the run
    assessment_version = assessment["version"]
    results = get_run_results(client, run_id, assessment_version)
    if not results:
        logger.error("No results found for run. Aborting workflow.")
        return

    # Step 5: Get detailed results including intermediate results
    for result in results:
        get_detailed_result(client, result["id"], assessment_version)


def test_list_assessments(client: AttackIQRestClient):
    """Test listing assessments."""
    list_assessments(client, limit=5)


def test_get_recent_run(client: AttackIQRestClient, assessment_id: str):
    """Test getting the most recent run."""
    if not assessment_id:
        logger.error("ASSESSMENT_ID required for this test")
        return

    run = AssessmentUtils.get_most_recent_run_status(client, assessment_id)
    if run:
        logger.info(f"Recent run: {run.get('id')}")
        logger.info(f"  Created: {run.get('created', 'N/A')}")
        logger.info(f"  Progress: {run.get('done_count', 0)}/{run.get('total_count', 0)} completed")
        logger.info(f"  Completed: {run.get('completed', False)}")
    else:
        logger.info("No runs found")


def test_run_assessment(client: AttackIQRestClient, assessment_id: str):
    """Test running an assessment."""
    if not assessment_id:
        logger.error("ASSESSMENT_ID required for this test")
        return

    assessment = AssessmentUtils.get_assessment_by_id(client, assessment_id)
    if not assessment:
        logger.error(f"Assessment {assessment_id} not found")
        return

    assessment_version = assessment["version"]
    run_id = run_and_monitor_assessment(client, assessment_id, assessment_version)
    if run_id:
        results = list(AssessmentUtils.get_results_by_run_id(client, run_id, assessment_version, limit=3))
        logger.info(f"Completed with {len(results)} results")


def test_get_results(client: AttackIQRestClient, assessment_id: str):
    """Test getting results for the most recent run."""
    if not assessment_id:
        logger.error("ASSESSMENT_ID required for this test")
        return

    assessment = AssessmentUtils.get_assessment_by_id(client, assessment_id)
    if not assessment:
        logger.error(f"Assessment {assessment_id} not found")
        return

    assessment_version = assessment["version"]
    run = AssessmentUtils.get_most_recent_run_status(client, assessment_id)
    if run:
        run_id = run.get("id")
        results = get_run_results(client, run_id, assessment_version)
        logger.info(f"Retrieved {len(results)} results")


def test_get_recent_run_results(client: AttackIQRestClient, assessment_id: str):
    """Test getting detailed results for the most recent run."""
    if not assessment_id:
        logger.error("ASSESSMENT_ID required for this test")
        return

    assessment = AssessmentUtils.get_assessment_by_id(client, assessment_id)
    if not assessment:
        logger.error(f"Assessment {assessment_id} not found")
        return

    assessment_version = assessment["version"]
    run = AssessmentUtils.get_most_recent_run_status(client, assessment_id)
    if run:
        run_id = run.get("id")
        logger.info(f"Getting results for recent run: {run_id}")
        logger.info(f"  Run completed: {run.get('completed', False)}")
        logger.info(f"  Progress: {run.get('done_count', 0)}/{run.get('total_count', 0)}")

        results = get_run_results(client, run_id, assessment_version, limit=10)
        if results:
            logger.info(f"Successfully retrieved {len(results)} results")
            for result in results[:3]:  # Show first 3 results
                get_detailed_result(client, result["id"], assessment_version)
        else:
            logger.warning("No results found for the most recent run")
    else:
        logger.info("No recent runs found")


def test_execution_with_detection(client: AttackIQRestClient, assessment_id: str):
    """Test setting execution strategy to run with detection validation."""
    if not assessment_id:
        logger.error("ASSESSMENT_ID required for this test")
        return

    result = AssessmentUtils.set_execution_strategy(client, assessment_id, with_detection=True)
    logger.info(f"Set execution WITH detection: {'Success' if result else 'Failed'}")


def test_execution_without_detection(client: AttackIQRestClient, assessment_id: str):
    """Test setting execution strategy to run without detection validation."""
    if not assessment_id:
        logger.error("ASSESSMENT_ID required for this test")
        return

    result = AssessmentUtils.set_execution_strategy(client, assessment_id, with_detection=False)
    logger.info(f"Set execution WITHOUT detection: {'Success' if result else 'Failed'}")


def test_get_execution_strategy(client: AttackIQRestClient, assessment_id: str):
    """Get and display execution strategy for an assessment."""
    if not assessment_id:
        logger.error("ASSESSMENT_ID required for this test")
        return

    strategy = AssessmentUtils.get_execution_strategy(client, assessment_id)
    assessment = AssessmentUtils.get_assessment_by_id(client, assessment_id)

    logger.info(f"Assessment: {assessment.get('name')}")
    logger.info(f"Execution Strategy: {strategy.name} (value={strategy.value})")

    if strategy == AssessmentExecutionStrategy.WITH_DETECTION:
        logger.info("Detection validation is ENABLED")
    else:
        logger.info("Detection validation is DISABLED")

    return strategy


def test_workflow_demo(client: AttackIQRestClient, assessment_id: str):
    """Test the full workflow demo."""
    if not assessment_id:
        logger.error("ASSESSMENT_ID required for this test")
        return

    assessment_workflow_demo(client, assessment_id, run_assessment=True)


def test_all(client: AttackIQRestClient, assessment_id: str):
    """Run all tests."""
    list_assessments(client, limit=3)
    if assessment_id:
        get_assessment_by_id(client, assessment_id)
        run = AssessmentUtils.get_most_recent_run_status(client, assessment_id)
        if run:
            logger.info(f"Most recent run: {run.get('id')}")
            logger.info(f"  Progress: {run.get('done_count', 0)}/{run.get('total_count', 0)} completed")
        list_assessment_runs(client, assessment_id, limit=3)
        assessment_workflow_demo(client, assessment_id, run_assessment=False)


def run_test(choice: "TestChoice", client: AttackIQRestClient, assessment_id: str):
    """Run the selected test."""
    test_functions = {
        TestChoice.LIST_ASSESSMENTS: lambda: test_list_assessments(client),
        TestChoice.GET_RECENT_RUN: lambda: test_get_recent_run(client, assessment_id),
        TestChoice.RUN_ASSESSMENT: lambda: test_run_assessment(client, assessment_id),
        TestChoice.WORKFLOW_DEMO: lambda: test_workflow_demo(client, assessment_id),
        TestChoice.GET_RESULTS: lambda: test_get_results(client, assessment_id),
        TestChoice.GET_RECENT_RUN_RESULTS: lambda: test_get_recent_run_results(client, assessment_id),
        TestChoice.EXECUTION_WITH_DETECTION: lambda: test_execution_with_detection(client, assessment_id),
        TestChoice.EXECUTION_WITHOUT_DETECTION: lambda: test_execution_without_detection(client, assessment_id),
        TestChoice.GET_EXECUTION_STRATEGY: lambda: test_get_execution_strategy(client, assessment_id),
        TestChoice.ALL: lambda: test_all(client, assessment_id),
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
        LIST_ASSESSMENTS = "list_assessments"
        GET_RECENT_RUN = "get_recent_run"
        RUN_ASSESSMENT = "run_assessment"
        WORKFLOW_DEMO = "workflow_demo"
        GET_RESULTS = "get_results"
        GET_RECENT_RUN_RESULTS = "get_recent_run_results"
        EXECUTION_WITH_DETECTION = "execution_with_detection"
        EXECUTION_WITHOUT_DETECTION = "execution_without_detection"
        GET_EXECUTION_STRATEGY = "get_execution_strategy"
        ALL = "all"

    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_PLATFORM_API_TOKEN)
    assessment_id = os.environ.get("ASSESSMENT_ID") or os.environ.get("ATTACKIQ_ATOMIC_ASSESSMENT_ID")

    # Change this to test different functionalities
    # choice = TestChoice.GET_RECENT_RUN
    # choice = TestChoice.LIST_ASSESSMENTS
    # choice = TestChoice.RUN_ASSESSMENT
    # choice = TestChoice.WORKFLOW_DEMO
    # choice = TestChoice.GET_RESULTS
    # choice = TestChoice.GET_RECENT_RUN_RESULTS
    # choice = TestChoice.EXECUTION_WITH_DETECTION
    # choice = TestChoice.EXECUTION_WITHOUT_DETECTION
    choice = TestChoice.GET_EXECUTION_STRATEGY
    # choice = TestChoice.ALL

    run_test(choice, client, assessment_id)
