# Example notebook: https://colab.research.google.com/drive/1lkBknmfM3Ygt2X4NBxDVecz8Z7LKaECB?usp=sharing
import sys
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    ResultsUtils,
)
from aiq_platform_api.env import ATTACKIQ_PLATFORM_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_results(
    client: AttackIQRestClient,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: Optional[int] = 10,
):
    logger.info(f"Listing up to {limit} results...")
    count = 0

    for result in ResultsUtils.get_results(
        client,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    ):
        count += 1
        logger.info(f"Result {count}:")
        logger.info(f"  Result ID: {result.get('id')}")
        logger.info("---")
    logger.info(f"Total results listed: {count}")
    return count


def iterate_results_from(client: AttackIQRestClient, hours_ago: int):
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours_ago)
    logger.info(f"Iterating over results from {start_date} to {end_date}")
    return list_results(client, start_date=start_date, end_date=end_date)


def test_list_all_results(client: AttackIQRestClient):
    """Test listing results from last 3 months."""
    # Use 3 months (90 days) instead of no filter to avoid server issues
    hours_ago = 90 * 24  # 90 days
    total_results = iterate_results_from(client, hours_ago)
    logger.info(f"Total results from last 3 months: {total_results}")


def test_recent_results(client: AttackIQRestClient):
    """Test listing results from last 2 hours."""
    hours_ago = 2
    total_results = iterate_results_from(client, hours_ago)
    logger.info(f"Total results from {hours_ago} hours ago: {total_results}")


def test_daily_results(client: AttackIQRestClient):
    """Test listing results from last 24 hours."""
    hours_ago = 24
    total_results = iterate_results_from(client, hours_ago)
    logger.info(f"Total results from {hours_ago} hours ago: {total_results}")


def run_test(choice: "TestChoice", client: AttackIQRestClient):
    """Run the selected test."""
    test_functions = {
        TestChoice.LIST_ALL: lambda: test_list_all_results(client),
        TestChoice.RECENT_RESULTS: lambda: test_recent_results(client),
        TestChoice.DAILY_RESULTS: lambda: test_daily_results(client),
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
        RECENT_RESULTS = "recent_results"
        DAILY_RESULTS = "daily_results"

    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_PLATFORM_API_TOKEN)

    # Change this to test different functionalities
    # choice = TestChoice.RECENT_RESULTS
    choice = TestChoice.LIST_ALL
    # choice = TestChoice.DAILY_RESULTS

    run_test(choice, client)
