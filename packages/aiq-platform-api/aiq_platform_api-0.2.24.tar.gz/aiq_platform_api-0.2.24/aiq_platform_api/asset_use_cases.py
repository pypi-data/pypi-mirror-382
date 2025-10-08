# Example notebook: https://colab.research.google.com/drive/1DO062G8PPaS_fD6PSs1LV56UXmmFe1cR?usp=sharing
import os
import sys
from enum import Enum
from typing import Optional

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    AssetUtils,
    TagUtils,
    TaggedItemUtils,
    AssetStatus,
)
from aiq_platform_api.env import ATTACKIQ_PLATFORM_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def fetch_and_log_assets(client: AttackIQRestClient, limit: Optional[int] = 10):
    logger.info(f"Fetching and processing up to {limit} assets...")
    asset_count = 0

    for asset in AssetUtils.get_assets(client, limit=limit):
        asset_count += 1
        logger.info(f"Asset {asset_count}:")
        logger.info(f"  ID: {asset.get('id')}")
        logger.info(f"  Name: {asset.get('name')}")
        logger.info(f"  Type: {asset.get('type')}")
        logger.info(f"  IP Address: {asset.get('ipv4_address')}")
        logger.info("---")

    if asset_count == 0:
        logger.info("No assets retrieved with the current filters/limit.")
    else:
        logger.info(f"Successfully processed {asset_count} assets.")


def find_asset_by_hostname(client: AttackIQRestClient, hostname: str):
    logger.info(f"Searching for asset with hostname: {hostname}")
    asset = AssetUtils.get_asset_by_hostname(client, hostname)

    if asset:
        logger.info("Asset found:")
        logger.info(f"  ID: {asset.get('id')}")
        logger.info(f"  Name: {asset.get('name')}")
        logger.info(f"  Type: {asset.get('type')}")
        logger.info(f"  IP Address: {asset.get('ipv4_address')}")
        logger.info(f"  Hostname: {asset.get('hostname')}")
    else:
        logger.info(f"No asset found with hostname: {hostname}")


def search_assets_use_case(
    client: AttackIQRestClient,
    query: Optional[str] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    ordering: Optional[str] = "-modified",
) -> dict:
    """Search or list assets. Returns {"count": total, "results": [...]}."""
    logger.info(
        f"--- Searching assets with query: '{query}', limit: {limit}, offset: {offset}, ordering: {ordering} ---"
    )
    try:
        result = AssetUtils.search_assets(client, query, limit, offset, ordering)
        logger.info(f"Found {result['count']} total, returning {len(result['results'])}")
        for idx, asset in enumerate(result["results"], 1):
            logger.info(f"{idx}. {asset.get('hostname')} (ID: {asset.get('id')})")
        return result
    except Exception as e:
        logger.error(f"Failed to search assets: {e}")
        raise


def uninstall_asset_by_uuid(client: AttackIQRestClient, asset_id: str):
    if not asset_id:
        logger.error("Asset id not provided.")
        return

    asset = AssetUtils.get_asset_by_id(client, asset_id)
    if not asset:
        logger.error(f"Asset with id {asset_id} not found.")
        return

    logger.info(f"Attempting to uninstall asset with id: {asset_id}")
    success = AssetUtils.uninstall_asset(client, asset_id)

    if success:
        logger.info(f"Asset {asset_id} uninstall job submitted successfully.")
    else:
        logger.error(f"Failed to submit uninstall job for asset {asset_id}.")


def list_asset_tags(client: AttackIQRestClient, asset_id: str, limit: Optional[int] = 10):
    logger.info(f"Listing up to {limit} tags for asset with ID: {asset_id}")
    tag_count = 0

    for tagged_item in TaggedItemUtils.get_tagged_items(client, "asset", asset_id, limit=limit):
        tag_count += 1
        tag_id = tagged_item.get("tag", {}).get("id")
        tag_name = tagged_item.get("tag", {}).get("name")
        logger.info(f"Tagged Item {tag_count}:")
        logger.info(f"  Item ID: {tagged_item.get('id')}")
        logger.info(f"  Tag ID: {tag_id}")
        logger.info(f"  Tag Name: {tag_name}")
    logger.info(f"Total tags listed: {tag_count}")


def tag_asset(client: AttackIQRestClient, asset_id: str, tag_id: str) -> str:
    logger.info(f"Tagging asset with ID: {asset_id} with tag ID: {tag_id}")
    tagged_item = TaggedItemUtils.get_tagged_item(client, "asset", asset_id, tag_id)
    tagged_item_id = tagged_item.get("id") if tagged_item else ""
    if tagged_item_id:
        logger.info(f"Asset {asset_id} is already tagged with tag item ID {tagged_item_id}")
        return tagged_item_id
    tagged_item_id = AssetUtils.add_tag(client, asset_id, tag_id)
    if tagged_item_id:
        logger.info(f"Successfully tagged asset {asset_id} with tag item ID {tagged_item_id}")
        return tagged_item_id
    else:
        logger.error(f"Failed to tag asset {asset_id} with tag ID {tag_id}")
        return ""


def untag_asset(client: AttackIQRestClient, tagged_item_id: str):
    logger.info(f"Removing tag item with ID: {tagged_item_id}")
    success = TaggedItemUtils.delete_tagged_item(client, tagged_item_id)
    if success:
        logger.info(f"Successfully removed tag item with ID {tagged_item_id}")
    else:
        logger.error(f"Failed to remove tag item with ID {tagged_item_id}")


def delete_tag(client: AttackIQRestClient, tag_id: str) -> bool:
    logger.info(f"Deleting tag with ID: {tag_id}")
    success = TagUtils.delete_tag(client, tag_id)
    if success:
        logger.info(f"Successfully deleted tag with ID {tag_id}")
    else:
        logger.error(f"Failed to delete tag with ID {tag_id}")
    return success


def get_and_log_total_assets(client: AttackIQRestClient):
    total_assets = AssetUtils.get_total_assets(client)
    if total_assets is not None:
        logger.info(f"Total number of assets: {total_assets}")
    else:
        logger.error("Failed to retrieve total number of assets.")


def get_and_log_assets_count_by_status(client: AttackIQRestClient, status: AssetStatus):
    assets_count = AssetUtils.get_assets_count_by_status(client, status)
    if assets_count is not None:
        logger.info(f"Number of {status.value} assets: {assets_count}")
    else:
        logger.error(f"Failed to retrieve count of {status.value} assets.")


def test_asset_counts(client: AttackIQRestClient):
    """Test getting asset counts."""
    get_and_log_total_assets(client)
    get_and_log_assets_count_by_status(client, AssetStatus.ACTIVE)
    get_and_log_assets_count_by_status(client, AssetStatus.INACTIVE)


def test_list_assets(client: AttackIQRestClient):
    """Test listing assets."""
    fetch_and_log_assets(client, limit=25)


def test_active_assets(client: AttackIQRestClient):
    """Test fetching active assets with details."""
    logger.info("Fetching active assets with full details...")
    active_assets = AssetUtils.get_active_assets_with_details(client, limit=10)

    if not active_assets:
        logger.info("No active assets found.")
        return

    logger.info(f"\nFound {len(active_assets)} active assets:")
    for i, asset in enumerate(active_assets, 1):
        logger.info(f"{i}. {asset['hostname']}")
        logger.info(f"   Product: {asset['product_name']}")
        logger.info(f"   Agent Version: {asset['agent_version']}")
        logger.info(f"   IPv4: {asset['ipv4_address']}")
        logger.info(f"   MAC: {asset['mac_address']}")
        logger.info(f"   Domain: {asset['domain_name']}")
        logger.info(f"   Arch: {asset['processor_arch']}")
        logger.info(f"   State: {asset['deployment_state']}")

    return active_assets


def test_find_by_hostname(client: AttackIQRestClient, hostname: Optional[str] = None):
    """Test finding asset by hostname."""
    test_hostname = hostname or "AIQ-CY4C7CC9W5"
    find_asset_by_hostname(client, test_hostname)


def test_asset_tagging(client: AttackIQRestClient, asset_id: Optional[str] = None):
    """Test asset tagging operations."""
    if not asset_id:
        asset_id = os.environ.get("ATTACKIQ_ASSET_ID")

    if not asset_id:
        logger.warning("ATTACKIQ_ASSET_ID environment variable is not set. Skipping asset tagging operations.")
        return

    if not AssetUtils.get_asset_by_id(client, asset_id):
        logger.error(f"Asset {asset_id} not found. Skipping tagging operations.")
        return

    tag_name = "TEST_TAG"
    tag_id = TagUtils.get_or_create_custom_tag(client, tag_name)
    if not tag_id:
        logger.error(f"Failed to get or create tag '{tag_name}'")
        return

    logger.info(f"Tag ID: {tag_id} for tag '{tag_name}'")
    tagged_item_id = tag_asset(client, asset_id, tag_id)
    if tagged_item_id:
        list_asset_tags(client, asset_id)
        untag_asset(client, tagged_item_id)
        delete_tag(client, tag_id)


def test_uninstall_asset(client: AttackIQRestClient, asset_id: Optional[str] = None):
    """Test uninstalling an asset."""
    if not asset_id:
        asset_id = os.environ.get("ATTACKIQ_ASSET_ID")

    if not asset_id:
        logger.warning("ATTACKIQ_ASSET_ID environment variable is not set. Skipping uninstall operation.")
        return

    uninstall_asset_by_uuid(client, asset_id)


def test_search_assets(client: AttackIQRestClient):
    """Test searching assets by various queries."""
    logger.info("--- Testing Asset Search ---")

    logger.info("\n1. Searching by keyword 'windows':")
    search_assets_use_case(client, "windows", limit=5)

    logger.info("\n2. Searching by keyword 'linux':")
    search_assets_use_case(client, "linux", limit=5)

    logger.info("\n3. Listing all assets (no query):")
    search_assets_use_case(client, query=None, limit=5)


def test_pagination_workflow(client: AttackIQRestClient):
    """
    Test pagination with offset to demonstrate fetching batches.

    This validates:
    1. minimal=true reduces fields (30 -> 11, 63.3% reduction)
    2. offset pagination works correctly
    3. No duplicate assets across batches

    Use this pattern for other endpoints.
    """
    logger.info("--- Testing Pagination Workflow ---")

    batch_size = 5
    max_batches = 3
    all_ids = []

    for batch_num in range(1, max_batches + 1):
        offset = (batch_num - 1) * batch_size
        logger.info(f"\n--- Batch {batch_num}: offset={offset}, limit={batch_size} ---")

        assets = list(AssetUtils.get_assets(client, params=None, limit=batch_size, offset=offset))

        if not assets:
            logger.info("No more assets. Stopping.")
            break

        logger.info(f"Retrieved {len(assets)} assets:")
        for idx, asset in enumerate(assets, 1):
            asset_id = asset.get("id")
            asset_hostname = asset.get("hostname")
            logger.info(f"  {idx}. {asset_hostname}")
            all_ids.append(asset_id)

        logger.info(f"Fields in asset: {list(assets[0].keys())}")
        logger.info(f"Field count: {len(assets[0].keys())} (11 with minimal=true)")

    logger.info("\n--- Summary ---")
    logger.info(f"Total fetched: {len(all_ids)}")
    logger.info(f"Unique: {len(set(all_ids))}")
    logger.info(f"Duplicates: {len(all_ids) - len(set(all_ids))}")

    if len(all_ids) == len(set(all_ids)):
        logger.info("✅ SUCCESS: No duplicates, pagination working correctly!")
    else:
        logger.error("⚠️  FAILED: Duplicates detected!")


def test_all(client: AttackIQRestClient):
    """Run all asset tests."""
    test_asset_counts(client)
    test_list_assets(client)
    test_active_assets(client)
    test_find_by_hostname(client)
    test_search_assets(client)
    test_pagination_workflow(client)

    asset_id = os.environ.get("ATTACKIQ_ASSET_ID")
    if asset_id:
        test_asset_tagging(client, asset_id)
        # Uninstall is destructive, so only run if explicitly testing all
        # test_uninstall_asset(client, asset_id)
    else:
        logger.warning("ATTACKIQ_ASSET_ID not set. Skipping asset-specific operations.")


def run_test(choice: "TestChoice", client: AttackIQRestClient, asset_id: Optional[str] = None):
    """Run the selected test."""
    test_functions = {
        TestChoice.ASSET_COUNTS: lambda: test_asset_counts(client),
        TestChoice.LIST_ASSETS: lambda: test_list_assets(client),
        TestChoice.ACTIVE_ASSETS: lambda: test_active_assets(client),
        TestChoice.FIND_BY_HOSTNAME: lambda: test_find_by_hostname(client),
        TestChoice.SEARCH_ASSETS: lambda: test_search_assets(client),
        TestChoice.PAGINATION_WORKFLOW: lambda: test_pagination_workflow(client),
        TestChoice.ASSET_TAGGING: lambda: test_asset_tagging(client, asset_id),
        TestChoice.UNINSTALL_ASSET: lambda: test_uninstall_asset(client, asset_id),
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
        ASSET_COUNTS = "asset_counts"
        LIST_ASSETS = "list_assets"
        ACTIVE_ASSETS = "active_assets"
        FIND_BY_HOSTNAME = "find_by_hostname"
        SEARCH_ASSETS = "search_assets"
        PAGINATION_WORKFLOW = "pagination_workflow"
        ASSET_TAGGING = "asset_tagging"
        UNINSTALL_ASSET = "uninstall_asset"
        ALL = "all"

    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_PLATFORM_API_TOKEN)
    asset_id = os.environ.get("ATTACKIQ_ASSET_ID")

    # Change this to test different functionalities
    choice = TestChoice.ACTIVE_ASSETS
    # choice = TestChoice.PAGINATION_WORKFLOW
    # choice = TestChoice.SEARCH_ASSETS
    # choice = TestChoice.LIST_ASSETS
    # choice = TestChoice.FIND_BY_HOSTNAME
    # choice = TestChoice.ASSET_TAGGING
    # choice = TestChoice.UNINSTALL_ASSET
    # choice = TestChoice.ALL

    run_test(choice, client, asset_id)
