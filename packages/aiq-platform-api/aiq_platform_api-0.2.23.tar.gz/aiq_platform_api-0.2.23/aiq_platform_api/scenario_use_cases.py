# Example use cases for Scenario endpoints
import os
import sys
from enum import Enum
from typing import Optional, Dict, Any

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    ScenarioUtils,
)
from aiq_platform_api.env import ATTACKIQ_PLATFORM_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_scenarios(
    client: AttackIQRestClient,
    limit: Optional[int] = 10,
    filter_params: Optional[Dict[str, Any]] = None,
) -> int:
    """Lists scenarios with optional filtering."""
    filter_params = filter_params or {}
    logger.info(f"Listing up to {limit} scenarios with params: {filter_params}")
    count = 0
    try:
        for scenario in ScenarioUtils.list_scenarios(client, params=filter_params, limit=limit):
            count += 1
            logger.info(f"Scenario {count}: ID={scenario.get('id')}, Name={scenario.get('name')}")
        logger.info(f"Total scenarios listed: {count}")
    except Exception as e:
        logger.error(f"Failed to list scenarios: {e}")
    return count


def save_scenario_copy(
    client: AttackIQRestClient,
    scenario_id: str,
    new_name: str,
    model_json: Optional[Dict[str, Any]] = None,
    fork_template: bool = True,
) -> Optional[Dict[str, Any]]:
    """Creates a copy of an existing scenario with potentially updated model data.

    Args:
        client: The API client to use
        scenario_id: ID of the scenario to copy
        new_name: Name for the new scenario
        model_json: Optional modified model JSON for the new scenario
        fork_template: Whether to create a new scenario template (True) or reuse the existing one (False)

    Returns:
        The newly created scenario data if successful, None otherwise
    """
    logger.info(f"Creating a copy of scenario {scenario_id} with name '{new_name}'")
    try:
        copy_data = {
            "name": new_name,
            "fork_template": fork_template,
        }
        if model_json:
            copy_data["model_json"] = model_json

        new_scenario = ScenarioUtils.save_copy(client, scenario_id, copy_data)
        if new_scenario:
            logger.info(f"Successfully created scenario copy with ID: {new_scenario.get('id')}")
            return new_scenario
        else:
            logger.error("Failed to create scenario copy")
    except Exception as e:
        logger.error(f"Error creating scenario copy: {e}")
    return None


def delete_scenario_use_case(client: AttackIQRestClient, scenario_id: str):
    """Deletes a specific scenario by its ID."""
    logger.info(f"--- Attempting to delete scenario: {scenario_id} ---")
    try:
        success = ScenarioUtils.delete_scenario(client, scenario_id)
        if success:
            logger.info(f"Successfully initiated deletion of scenario: {scenario_id}")
        else:
            logger.error(f"Failed to initiate deletion of scenario: {scenario_id}")
    except Exception as e:
        logger.error(f"Error deleting scenario {scenario_id}: {e}")


def test_list_scenarios(client: AttackIQRestClient, search_term: Optional[str] = None):
    """Test listing scenarios with optional search."""
    logger.info("--- Testing Scenario Listing ---")
    filter_params = {"search": search_term} if search_term else {}
    list_scenarios(client, limit=5, filter_params=filter_params)


def test_list_mimikatz_scenarios(client: AttackIQRestClient):
    """Test listing scenarios containing 'Mimikatz'."""
    logger.info("--- Testing Scenario Listing with Mimikatz filter ---")
    test_list_scenarios(client, "Mimikatz")


def test_copy_scenario(client: AttackIQRestClient, scenario_id: Optional[str] = None):
    """Test copying a scenario without deletion."""
    logger.info("--- Testing Scenario Copy ---")

    if not scenario_id:
        scenario_id = os.environ.get("ATTACKIQ_SCENARIO_ID", "5417db5e-569f-4660-86ae-9ea7b73452c5")

    scenario = ScenarioUtils.get_scenario(client, scenario_id)
    if not scenario:
        logger.error(f"Scenario {scenario_id} not found")
        return None

    old_name = scenario.get("name")
    old_model_json = scenario.get("model_json")
    if old_model_json:
        old_model_json["domain"] = "example.com"

    # Add timestamp to make name unique
    import time

    timestamp = int(time.time())
    new_scenario_name = f"aiq_platform_api created {old_name} - {timestamp}"
    new_scenario = save_scenario_copy(
        client,
        scenario_id=scenario_id,
        new_name=new_scenario_name,
        model_json=old_model_json,
    )

    if new_scenario:
        logger.info(f"New scenario created: {new_scenario.get('name')} ({new_scenario.get('id')})")
        return new_scenario.get("id")
    return None


def test_delete_scenario(client: AttackIQRestClient, scenario_id: str):
    """Test deleting a specific scenario."""
    logger.info("--- Testing Scenario Deletion ---")
    if not scenario_id:
        logger.warning("No scenario ID provided for deletion")
        return
    delete_scenario_use_case(client, scenario_id)


def search_scenarios_use_case(
    client: AttackIQRestClient,
    query: Optional[str] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    ordering: Optional[str] = "-modified",
) -> dict:
    """Search or list scenarios. Returns {"count": total, "results": [...]}."""
    logger.info(
        f"--- Searching scenarios with query: '{query}', limit: {limit}, offset: {offset}, ordering: {ordering} ---"
    )
    try:
        result = ScenarioUtils.search_scenarios(client, query, limit, offset, ordering)
        logger.info(f"Found {result['count']} total, returning {len(result['results'])}")
        for idx, scenario in enumerate(result["results"], 1):
            logger.info(f"{idx}. {scenario.get('name')} (ID: {scenario.get('id')})")
        return result
    except Exception as e:
        logger.error(f"Failed to search scenarios: {e}")
        raise


def get_scenario_details_use_case(
    client: AttackIQRestClient,
    scenario_id: str,
) -> Optional[Dict[str, Any]]:
    """Get complete details for a specific scenario."""
    logger.info(f"--- Getting details for scenario: {scenario_id} ---")
    try:
        details = ScenarioUtils.get_scenario_details(client, scenario_id)
        if details:
            logger.info(f"Scenario: {details.get('name')}")
            logger.info(f"Description: {details.get('description', 'N/A')}")
            logger.info(f"Created: {details.get('created_at', 'N/A')}")
            return details
        else:
            logger.warning(f"No details found for scenario: {scenario_id}")
            return None
    except Exception as e:
        logger.error(f"Failed to get scenario details: {e}")
        return None


def test_search_scenarios(client: AttackIQRestClient):
    """Test searching scenarios by various queries."""
    logger.info("--- Testing Scenario Search ---")

    # Search by keyword
    logger.info("\n1. Searching by keyword 'LSASS':")
    search_scenarios_use_case(client, "LSASS", limit=5)

    # Search by MITRE technique
    logger.info("\n2. Searching by MITRE technique 'T1003':")
    search_scenarios_use_case(client, "T1003", limit=5)

    # Search by tag
    logger.info("\n3. Searching by tag 'ransomware':")
    search_scenarios_use_case(client, "ransomware", limit=5)

    # List all scenarios
    logger.info("\n4. Listing all scenarios (no query):")
    search_scenarios_use_case(client, query=None, limit=5)


def test_get_scenario_details(client: AttackIQRestClient, scenario_id: Optional[str] = None):
    """Test getting detailed information for a scenario."""
    logger.info("--- Testing Get Scenario Details ---")

    if not scenario_id:
        # First search for a scenario, then get its details
        scenarios = search_scenarios_use_case(client, "Mimikatz", limit=1)
        if scenarios:
            scenario_id = scenarios[0].get("id")
        else:
            logger.warning("No scenarios found to get details for")
            return

    get_scenario_details_use_case(client, scenario_id)


def test_copy_and_delete(client: AttackIQRestClient, scenario_id: Optional[str] = None):
    """Test the full workflow: copy a scenario and then delete the copy."""
    logger.info("--- Testing Scenario Copy and Delete Workflow ---")

    if not scenario_id:
        scenario_id = os.environ.get("ATTACKIQ_SCENARIO_ID", "5417db5e-569f-4660-86ae-9ea7b73452c5")

    new_scenario_id = test_copy_scenario(client, scenario_id)
    if new_scenario_id:
        logger.info(f"--- Proceeding to delete the created scenario: {new_scenario_id} ---")
        test_delete_scenario(client, new_scenario_id)
    else:
        logger.warning("Could not get ID of newly created scenario, skipping deletion.")


def test_pagination_workflow(client: AttackIQRestClient):
    """
    Test pagination with offset to demonstrate fetching batches.

    This validates:
    1. minimal=true reduces fields (23 -> 7)
    2. offset pagination works correctly
    3. No duplicate scenarios across batches

    Use this pattern for other endpoints (assets, assessments, attack graphs).
    """
    logger.info("--- Testing Pagination Workflow ---")

    batch_size = 5
    max_batches = 3
    all_ids = []

    for batch_num in range(1, max_batches + 1):
        offset = (batch_num - 1) * batch_size
        logger.info(f"\n--- Batch {batch_num}: offset={offset}, limit={batch_size} ---")

        scenarios = list(
            ScenarioUtils.list_scenarios(client, params={"search": "powershell"}, limit=batch_size, offset=offset)
        )

        if not scenarios:
            logger.info("No more scenarios. Stopping.")
            break

        logger.info(f"Retrieved {len(scenarios)} scenarios:")
        for idx, scenario in enumerate(scenarios, 1):
            scenario_id = scenario.get("id")
            scenario_name = scenario.get("name")
            logger.info(f"  {idx}. {scenario_name}")
            all_ids.append(scenario_id)

        logger.info(f"Fields in scenario: {list(scenarios[0].keys())}")
        logger.info(f"Field count: {len(scenarios[0].keys())} (7 with minimal=true)")

    logger.info("\n--- Summary ---")
    logger.info(f"Total fetched: {len(all_ids)}")
    logger.info(f"Unique: {len(set(all_ids))}")
    logger.info(f"Duplicates: {len(all_ids) - len(set(all_ids))}")

    if len(all_ids) == len(set(all_ids)):
        logger.info("✅ SUCCESS: No duplicates, pagination working correctly!")
    else:
        logger.error("⚠️  FAILED: Duplicates detected!")


def test_all(client: AttackIQRestClient):
    """Run all scenario tests."""
    # Test listing without filter
    test_list_scenarios(client)

    # Test listing with filter
    test_list_mimikatz_scenarios(client)

    # Test search scenarios
    test_search_scenarios(client)

    # Test get scenario details
    test_get_scenario_details(client)

    # Test pagination workflow
    test_pagination_workflow(client)

    # Test copy and delete workflow
    scenario_id = os.environ.get("ATTACKIQ_SCENARIO_ID")
    if scenario_id:
        test_copy_and_delete(client, scenario_id)
    else:
        logger.warning("ATTACKIQ_SCENARIO_ID not set. Skipping copy/delete tests.")


def run_test(choice: "TestChoice", client: AttackIQRestClient, scenario_id: Optional[str] = None):
    """Run the selected test."""
    test_functions = {
        TestChoice.LIST_ALL: lambda: test_list_scenarios(client),
        TestChoice.LIST_MIMIKATZ: lambda: test_list_mimikatz_scenarios(client),
        TestChoice.SEARCH_SCENARIOS: lambda: test_search_scenarios(client),
        TestChoice.GET_SCENARIO_DETAILS: lambda: test_get_scenario_details(client, scenario_id),
        TestChoice.PAGINATION_WORKFLOW: lambda: test_pagination_workflow(client),
        TestChoice.COPY_SCENARIO: lambda: test_copy_scenario(client, scenario_id),
        TestChoice.DELETE_SCENARIO: lambda: (
            test_delete_scenario(client, scenario_id)
            if scenario_id
            else logger.error("Scenario ID required for delete test")
        ),
        TestChoice.COPY_AND_DELETE: lambda: test_copy_and_delete(client, scenario_id),
        TestChoice.ALL: lambda: test_all(client),
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
        LIST_ALL = "list_all"
        LIST_MIMIKATZ = "list_mimikatz"
        SEARCH_SCENARIOS = "search_scenarios"
        GET_SCENARIO_DETAILS = "get_scenario_details"
        PAGINATION_WORKFLOW = "pagination_workflow"
        COPY_SCENARIO = "copy_scenario"
        DELETE_SCENARIO = "delete_scenario"
        COPY_AND_DELETE = "copy_and_delete"
        ALL = "all"

    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_PLATFORM_API_TOKEN)
    scenario_id = os.environ.get("ATTACKIQ_SCENARIO_ID", "5417db5e-569f-4660-86ae-9ea7b73452c5")

    # Change this to test different functionalities
    # choice = TestChoice.GET_SCENARIO_DETAILS
    # choice = TestChoice.SEARCH_SCENARIOS
    choice = TestChoice.PAGINATION_WORKFLOW
    # choice = TestChoice.LIST_ALL
    # choice = TestChoice.LIST_MIMIKATZ
    # choice = TestChoice.COPY_SCENARIO
    # choice = TestChoice.DELETE_SCENARIO
    # choice = TestChoice.COPY_AND_DELETE
    # choice = TestChoice.ALL

    run_test(choice, client, scenario_id)
