# Example use cases for Unified Mitigation endpoints
import os
import sys
from enum import Enum
from typing import Optional, Dict, Any

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    UnifiedMitigationUtils,
    UnifiedMitigationProjectUtils,
    UnifiedMitigationWithRelationsUtils,
    UnifiedMitigationReportingUtils,
    AssessmentUtils,
    DetectionStatus,
    DetectionOutcome,
    INTEGRATION_NAMES,
)
from aiq_platform_api.env import ATTACKIQ_PLATFORM_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_mitigation_rules(client: AttackIQRestClient, limit: Optional[int] = 10) -> int:
    """Lists unified mitigation rules."""
    logger.info(f"Listing up to {limit} unified mitigations...")
    count = 0
    try:
        for rule in UnifiedMitigationUtils.list_mitigations(client, limit=limit):
            count += 1
            logger.info(f"Mitigation Rule {count}: ID={rule.get('id')}, Name={rule.get('name')}")
        logger.info(f"Total mitigation rules listed: {count}")
    except Exception as e:
        logger.error(f"Failed to list mitigation rules: {e}")
    return count


def create_and_delete_mitigation_rule(client: AttackIQRestClient, rule_data: Dict[str, Any]) -> None:
    """Creates a mitigation rule and then deletes it."""
    mitigation_id = None
    try:
        logger.info("Attempting to create a new mitigation rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            mitigation_id = created_rule["id"]
            logger.info(f"Successfully created mitigation rule with ID: {mitigation_id}")

            # Example: Get the created rule
            retrieved_rule = UnifiedMitigationUtils.get_mitigation(client, mitigation_id)
            if retrieved_rule:
                logger.info(f"Retrieved rule: {retrieved_rule.get('name')}")
            else:
                logger.warning("Could not retrieve the newly created rule.")

        else:
            logger.error("Failed to create mitigation rule or ID not found in response.")
            return

    except Exception as e:
        logger.error(f"Error during mitigation rule creation/retrieval: {e}")
    finally:
        if mitigation_id:
            logger.info(f"Attempting to delete mitigation rule: {mitigation_id}")
            deleted = UnifiedMitigationUtils.delete_mitigation(client, mitigation_id)
            if deleted:
                logger.info(f"Successfully deleted mitigation rule: {mitigation_id}")
            else:
                logger.error(f"Failed to delete mitigation rule: {mitigation_id}")


def create_sigma_detection_rule(client: AttackIQRestClient) -> Optional[str]:
    """Creates a Sigma detection rule for PowerShell encoded command detection.

    IMPORTANT: Required fields for creating detection rules:
    - 'unifiedmitigationtype': The mitigation type ID (integer)
    - 'name': Name of the rule
    - 'content': The actual rule content/query (despite docs saying 'rule_content')

    Common mitigation type IDs:
    - 1: Sigma
    - 2: YARA
    - 3: Snort
    - 4: Suricata
    - 5: SPL (Splunk)
    - 6: KQL (Kusto Query Language)
    - 7: EQL (Elastic Query Language)
    - 8: Lucene/Elasticsearch
    - 9: Custom
    - 12: Chronicle YARA-L
    """
    sigma_rule_content = """
title: Suspicious PowerShell Encoded Command
status: experimental
description: Detects suspicious PowerShell execution with encoded commands
logsource:
    product: windows
    service: process_creation
detection:
    selection:
        CommandLine|contains:
            - '-EncodedCommand'
            - '-enc'
        Image|endswith: '\\powershell.exe'
    condition: selection
falsepositives:
    - Administrative scripts
level: medium
"""

    rule_data = {
        "name": "Sigma - Suspicious PowerShell Encoded Command",
        "description": "Detects PowerShell execution with encoded commands that may indicate malicious activity",
        "unifiedmitigationtype": 1,  # REQUIRED: 1 = Sigma (integer type ID)
        "content": sigma_rule_content,  # REQUIRED: The actual rule content (field name is 'content')
    }

    try:
        logger.info("Creating Sigma detection rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            rule_id = created_rule["id"]
            logger.info(f"Successfully created Sigma rule with ID: {rule_id}")
            return rule_id
        else:
            logger.error("Failed to create Sigma rule")
            return None
    except Exception as e:
        logger.error(f"Error creating Sigma rule: {e}")
        return None


def create_yara_detection_rule(client: AttackIQRestClient) -> Optional[str]:
    """Creates a YARA detection rule for malware detection."""
    yara_rule_content = """
rule Detect_Mimikatz_Patterns {
    meta:
        description = "Detects common Mimikatz patterns and strings"
        author = "Security Team"
        date = "2025-01-20"
    strings:
        $a = "sekurlsa::logonpasswords" nocase
        $b = "privilege::debug" nocase
        $c = "mimikatz" nocase
        $d = "gentilkiwi" nocase
        $e = "lsadump::sam" nocase
    condition:
        2 of them
}
"""

    rule_data = {
        "name": "YARA - Detect Mimikatz Patterns",
        "description": "YARA rule to detect common Mimikatz tool patterns",
        "unifiedmitigationtype": 2,
        # REQUIRED: 2 = YARA (integer type ID)
        "content": yara_rule_content,  # REQUIRED: The actual rule content
    }

    try:
        logger.info("Creating YARA detection rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            rule_id = created_rule["id"]
            logger.info(f"Successfully created YARA rule with ID: {rule_id}")
            return rule_id
        else:
            logger.error("Failed to create YARA rule")
            return None
    except Exception as e:
        logger.error(f"Error creating YARA rule: {e}")
        return None


def create_snort_detection_rule(client: AttackIQRestClient) -> Optional[str]:
    """Creates a Snort IDS rule for network detection."""
    snort_rule_content = """alert tcp $EXTERNAL_NET any -> $HOME_NET 445 (msg:"Possible SMB Exploitation Attempt"; flow:to_server,established; content:"|FF|SMB"; offset:4; depth:4; content:"|00 00 00 00|"; distance:0; content:"|00 00 00 00 00 00 00 00|"; distance:4; within:8; sid:1000001; rev:1;)"""

    rule_data = {
        "name": "Snort - SMB Exploitation Detection",
        "description": "Snort rule to detect potential SMB exploitation attempts",
        "unifiedmitigationtype": 3,
        # REQUIRED: 3 = Snort (integer type ID)
        "content": snort_rule_content,  # REQUIRED: The actual rule content
    }

    try:
        logger.info("Creating Snort detection rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            rule_id = created_rule["id"]
            logger.info(f"Successfully created Snort rule with ID: {rule_id}")
            return rule_id
        else:
            logger.error("Failed to create Snort rule")
            return None
    except Exception as e:
        logger.error(f"Error creating Snort rule: {e}")
        return None


def create_splunk_spl_detection_rule(client: AttackIQRestClient) -> Optional[str]:
    """Creates a Splunk SPL detection rule."""
    spl_rule_content = """index=windows EventCode=4688 (CommandLine="*-EncodedCommand*" OR CommandLine="*-enc*") Image="*\\powershell.exe" | stats count by Computer, User, CommandLine | where count > 5"""

    rule_data = {
        "name": "SPL - PowerShell Encoded Command Detection",
        "description": "Splunk query to detect encoded PowerShell commands",
        "unifiedmitigationtype": 5,
        # REQUIRED: 5 = SPL/Splunk (integer type ID)
        "content": spl_rule_content,  # REQUIRED: The actual rule content
    }

    try:
        logger.info("Creating Splunk SPL detection rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            rule_id = created_rule["id"]
            logger.info(f"Successfully created SPL rule with ID: {rule_id}")
            return rule_id
        else:
            logger.error("Failed to create SPL rule")
            return None
    except Exception as e:
        logger.error(f"Error creating SPL rule: {e}")
        return None


def list_project_associations(client: AttackIQRestClient, limit: Optional[int] = 10) -> int:
    """Lists unified mitigation project associations."""
    logger.info(f"Listing up to {limit} unified mitigation project associations...")
    count = 0
    try:
        for assoc in UnifiedMitigationProjectUtils.list_associations(client, limit=limit):
            count += 1
            logger.info(
                f"Association {count}: ID={assoc.get('id')}, RuleID={assoc.get('unified_mitigation')}, ProjectID={assoc.get('project')}"
            )
        logger.info(f"Total associations listed: {count}")
    except Exception as e:
        logger.error(f"Failed to list project associations: {e}")
    return count


def list_mitigations_with_relations(client: AttackIQRestClient, limit: Optional[int] = 10) -> int:
    """Lists unified mitigations including related project and detection data."""
    logger.info(f"Listing up to {limit} unified mitigations with relations...")
    count = 0
    try:
        for rule in UnifiedMitigationWithRelationsUtils.list_mitigations_with_relations(client, limit=limit):
            count += 1
            logger.info(f"Mitigation+Relations {count}: ID={rule.get('id')}, Name={rule.get('name')}")
            # Add more details as needed, e.g., project info
            if rule.get("project"):
                logger.info(f"  Associated Project: {rule.get('project').get('name')}")
        logger.info(f"Total mitigations with relations listed: {count}")
    except Exception as e:
        logger.error(f"Failed to list mitigations with relations: {e}")
    return count


def get_detection_timeline(client: AttackIQRestClient, params: Optional[Dict[str, Any]] = None):
    """Gets the detection performance timeline data."""
    logger.info(f"Getting detection performance timeline with params: {params}")
    try:
        timeline_data = UnifiedMitigationReportingUtils.get_detection_performance_timeline(client, params)
        if timeline_data:
            logger.info(
                "Successfully retrieved detection timeline data."
            )  # Process or display data as needed  # logger.info(f"Timeline Data: {timeline_data}") # Potentially large output
        else:
            logger.warning("No detection timeline data returned.")
    except Exception as e:
        logger.error(f"Failed to get detection timeline: {e}")


def associate_rule_with_assessment(client: AttackIQRestClient, rule_id: str, assessment_id: str) -> Optional[str]:
    """Associates a detection rule with an assessment/project.

    Args:
        client: The AttackIQ REST client
        rule_id: The ID of the detection rule to associate
        assessment_id: The ID of the assessment/project

    Returns:
        The association ID if successful, None otherwise
    """
    try:
        logger.info(f"Associating rule {rule_id} with assessment {assessment_id}")

        association_data = {"unified_mitigation": rule_id, "project": assessment_id, "enabled": True}

        association = UnifiedMitigationProjectUtils.create_association(client, association_data)

        if association and association.get("id"):
            logger.info(f"Successfully associated rule with assessment. Association ID: {association['id']}")
            return association["id"]
        else:
            logger.error("Failed to associate rule with assessment")
            return None

    except Exception as e:
        logger.error(f"Error associating rule with assessment: {str(e)}")
        return None


def delete_detection_rule(client: AttackIQRestClient, rule_id: str) -> bool:
    """Deletes a detection rule by ID.

    Args:
        client: The AttackIQ REST client
        rule_id: The ID of the rule to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Deleting detection rule: {rule_id}")
        deleted = UnifiedMitigationUtils.delete_mitigation(client, rule_id)
        if deleted:
            logger.info(f"Successfully deleted rule: {rule_id}")
            return True
        else:
            logger.error(f"Failed to delete rule: {rule_id}")
            return False
    except Exception as e:
        logger.error(f"Error deleting rule: {str(e)}")
        return False


def get_detection_results(client: AttackIQRestClient, mitigation_id: str, limit: Optional[int] = 10) -> int:
    """Get detection results for a mitigation rule."""
    logger.info(f"Getting detection results for rule {mitigation_id}")
    count = 0
    try:
        for result in UnifiedMitigationUtils.get_detection_results(client, mitigation_id, limit=limit):
            count += 1
            logger.info(f"Result {count}:")
            logger.info(f"  ID: {result.get('id', 'N/A')}")
            logger.info(f"  Status: {result.get('detection_status', 'N/A')}")
            logger.info(f"  Outcome: {result.get('detection_outcome', 'N/A')}")
            logger.info(f"  Run ID: {result.get('project_run_id', 'N/A')}")
            logger.info(f"  Modified: {result.get('modified', 'N/A')}")
            logger.info("---")

        if count == 0:
            logger.info("No detection results found. Assessment may not have been run yet.")
        else:
            logger.info(f"Total results: {count}")
    except Exception as e:
        logger.error(f"Failed to get detection results: {e}")
    return count


def set_detection_detected(client: AttackIQRestClient, mitigation_id: str) -> Optional[Dict[str, Any]]:
    """Mark a rule as detected (true positive)."""
    logger.info(f"Setting rule {mitigation_id} as DETECTED (TRUE_POSITIVE)")
    try:
        result = UnifiedMitigationUtils.set_detection_status(
            client,
            mitigation_id,
            DetectionStatus.DETECTED.value,
            detection_outcome=DetectionOutcome.TRUE_POSITIVE.value,
            metadata={"updated_by": "manual_test", "reason": "Rule successfully detected the attack"},
        )

        if result:
            logger.info(f"Successfully updated detection status: {result.get('detection_status')}")
            logger.info(f"Outcome: {result.get('detection_outcome')}")
            return result
        else:
            logger.warning("No assessment runs found for this rule")
            return None
    except Exception as e:
        logger.error(f"Failed to set detection status: {e}")
        return None


def set_detection_not_detected(client: AttackIQRestClient, mitigation_id: str) -> Optional[Dict[str, Any]]:
    """Mark a rule as not detected (false negative)."""
    logger.info(f"Setting rule {mitigation_id} as NOT_DETECTED (FALSE_NEGATIVE)")
    try:
        result = UnifiedMitigationUtils.set_detection_status(
            client,
            mitigation_id,
            DetectionStatus.NOT_DETECTED.value,
            detection_outcome=DetectionOutcome.FALSE_NEGATIVE.value,
            metadata={"updated_by": "manual_test", "reason": "Rule failed to detect the attack"},
        )

        if result:
            logger.info(f"Successfully updated detection status: {result.get('detection_status')}")
            logger.info(f"Outcome: {result.get('detection_outcome')}")
            return result
        else:
            logger.warning("No assessment runs found for this rule")
            return None
    except Exception as e:
        logger.error(f"Failed to set detection status: {e}")
        return None


def get_latest_detection_status(client: AttackIQRestClient, mitigation_id: str) -> Optional[Dict[str, Any]]:
    """Get the latest detection status for a rule."""
    logger.info(f"Getting latest detection status for rule {mitigation_id}")
    try:
        latest = UnifiedMitigationUtils.get_latest_detection_result(client, mitigation_id)

        if latest:
            logger.info("Latest Detection Status:")
            logger.info(f"  Status: {latest.get('detection_status', 'N/A')}")
            logger.info(f"  Outcome: {latest.get('detection_outcome', 'N/A')}")
            logger.info(f"  Run ID: {latest.get('project_run_id', 'N/A')}")
            logger.info(f"  Modified: {latest.get('modified', 'N/A')}")

            if latest.get("metadata"):
                logger.info(f"  Metadata: {latest.get('metadata')}")
        else:
            logger.info("No detection results found. Assessment has not been run yet.")

        return latest
    except Exception as e:
        logger.error(f"Failed to get latest detection status: {e}")
        return None


def test_list_rules(client: AttackIQRestClient):
    """Test listing mitigation rules."""
    list_mitigation_rules(client, limit=5)


def test_get_rules_by_integration_name(client: AttackIQRestClient):
    """Test getting rules filtered by integration name."""
    # Test with the confirmed integration names from API URLs and integration-monorepo
    integration_names = ["sentinel", "chronicle", "splunk_es", "splunk", "elastic", "qradar"]

    for integration_name in integration_names:
        logger.info(f"\n--- Testing rules for integration name: {integration_name} ---")
        try:
            count = 0
            for rule in UnifiedMitigationUtils.get_rules_by_integration_name(client, integration_name, limit=3):
                count += 1
                integration_info = rule.get("integration", {})
                actual_integration_name = integration_info.get("name", "N/A") if integration_info else "N/A"
                logger.info(f"Rule {count}: ID={rule.get('id')}, Name={rule.get('name')}")
                logger.info(f"  Integration: {actual_integration_name}")
                logger.info(f"  Type: {rule.get('unifiedmitigationtype')}")

            if count == 0:
                logger.info(f"No rules found for integration name: {integration_name}")
            else:
                logger.info(f"Total {integration_name} rules found: {count}")

        except Exception as e:
            logger.error(f"Failed to get rules for {integration_name}: {e}")


def test_create_sigma(client: AttackIQRestClient):
    """Test creating and deleting a Sigma rule."""
    sigma_rule_id = create_sigma_detection_rule(client)
    if sigma_rule_id:
        logger.info(f"Created Sigma rule: {sigma_rule_id}")
        delete_detection_rule(client, sigma_rule_id)


def test_create_yara(client: AttackIQRestClient):
    """Test creating and deleting a YARA rule."""
    yara_rule_id = create_yara_detection_rule(client)
    if yara_rule_id:
        logger.info(f"Created YARA rule: {yara_rule_id}")
        delete_detection_rule(client, yara_rule_id)


def test_create_snort(client: AttackIQRestClient):
    """Test creating and deleting a Snort rule."""
    snort_rule_id = create_snort_detection_rule(client)
    if snort_rule_id:
        logger.info(f"Created Snort rule: {snort_rule_id}")
        delete_detection_rule(client, snort_rule_id)


def test_create_spl(client: AttackIQRestClient):
    """Test creating and deleting a Splunk SPL rule."""
    spl_rule_id = create_splunk_spl_detection_rule(client)
    if spl_rule_id:
        logger.info(f"Created SPL rule: {spl_rule_id}")
        delete_detection_rule(client, spl_rule_id)


def test_create_minimal(client: AttackIQRestClient):
    """Test creating and deleting a minimal rule."""
    minimal_rule_data = {
        "name": "Minimal Test Rule - Delete Me",
        "description": "Test rule with minimal required fields",
        "unifiedmitigationtype": 9,
        "content": "Basic rule content",
    }
    create_and_delete_mitigation_rule(client, minimal_rule_data)


def test_list_associations(client: AttackIQRestClient):
    """Test listing project associations."""
    list_project_associations(client, limit=5)


def test_list_with_relations(client: AttackIQRestClient):
    """Test listing mitigations with relations."""
    list_mitigations_with_relations(client, limit=5)


def test_get_timeline(client: AttackIQRestClient):
    """Test getting detection performance timeline."""
    timeline_params = {"time_interval": "monthly"}
    get_detection_timeline(client, timeline_params)


def test_get_detection_results(client: AttackIQRestClient, mitigation_id: str):
    """Test getting detection results for a rule."""
    if not mitigation_id:
        logger.error("MITIGATION_ID or RULE_ID environment variable required for this test")
        return
    get_detection_results(client, mitigation_id, limit=5)


def test_set_detected(client: AttackIQRestClient, mitigation_id: str):
    """Test setting rule as detected."""
    if not mitigation_id:
        logger.error("MITIGATION_ID or RULE_ID environment variable required for this test")
        return
    set_detection_detected(client, mitigation_id)


def test_set_not_detected(client: AttackIQRestClient, mitigation_id: str):
    """Test setting rule as not detected."""
    if not mitigation_id:
        logger.error("MITIGATION_ID or RULE_ID environment variable required for this test")
        return
    set_detection_not_detected(client, mitigation_id)


def test_get_latest_status(client: AttackIQRestClient, mitigation_id: str):
    """Test getting latest detection status."""
    if not mitigation_id:
        logger.error("MITIGATION_ID or RULE_ID environment variable required for this test")
        return
    get_latest_detection_status(client, mitigation_id)


def test_get_associated_assessment(client: AttackIQRestClient, mitigation_id: str):
    """Test getting associated assessment for a rule."""
    if not mitigation_id:
        logger.error("MITIGATION_ID or RULE_ID environment variable required for this test")
        return

    logger.info(f"Getting associated assessment for rule {mitigation_id}")
    assessment = UnifiedMitigationUtils.get_associated_assessment(client, mitigation_id)

    if assessment:
        logger.info(f"Found assessment: {assessment['name']} [ID: {assessment['id']}]")
        logger.info(f"  Version: {assessment.get('version', 'N/A')}")
        logger.info(f"  Created: {assessment.get('created', 'N/A')}")
    else:
        logger.info("No assessment associated with this rule")


def test_get_latest_assessment_run_status(client: AttackIQRestClient, mitigation_id: str):
    """Test getting latest assessment run status for a rule."""
    if not mitigation_id:
        logger.error("MITIGATION_ID or RULE_ID environment variable required for this test")
        return

    logger.info(f"Getting latest assessment run status for rule {mitigation_id}")
    run_status = UnifiedMitigationUtils.get_latest_assessment_run_status(client, mitigation_id)

    if run_status:
        logger.info(f"Found run: {run_status['id']}")
        logger.info(f"  Completed: {'✅ Yes' if run_status['completed'] else '⏳ In Progress'}")
        logger.info(f"  Progress: {run_status['done_count']}/{run_status['total_count']}")
        logger.info(f"  Created: {run_status.get('created', 'N/A')}")
    else:
        logger.info("No assessment runs found for this rule")


def test_analyst_verdicts(client: AttackIQRestClient, mitigation_id: str):
    """Test analyst verdict functions."""
    if not mitigation_id:
        logger.error("MITIGATION_ID or RULE_ID environment variable required for this test")
        return

    logger.info(f"Testing analyst verdict functions for rule {mitigation_id}")

    # Get current verdict
    current = UnifiedMitigationUtils.get_analyst_verdict(client, mitigation_id)
    logger.info(f"Current verdict: {current or 'None'}")

    # Test marking as true positive
    if UnifiedMitigationUtils.mark_true_positive(client, mitigation_id):
        logger.info("✅ Successfully marked as TRUE_POSITIVE")
        verdict = UnifiedMitigationUtils.get_analyst_verdict(client, mitigation_id)
        logger.info(f"  New verdict: {verdict}")

    # Test marking as false positive
    if UnifiedMitigationUtils.mark_false_positive(client, mitigation_id):
        logger.info("✅ Successfully marked as FALSE_POSITIVE")
        verdict = UnifiedMitigationUtils.get_analyst_verdict(client, mitigation_id)
        logger.info(f"  New verdict: {verdict}")


def test_all(client: AttackIQRestClient):
    """Run all tests."""
    logger.info("--- Listing Existing Unified Mitigation Rules ---")
    list_mitigation_rules(client, limit=5)

    logger.info("\n--- Creating Detection Rules Examples ---")

    sigma_rule_id = create_sigma_detection_rule(client)
    if sigma_rule_id:
        delete_detection_rule(client, sigma_rule_id)

    yara_rule_id = create_yara_detection_rule(client)
    if yara_rule_id:
        delete_detection_rule(client, yara_rule_id)

    snort_rule_id = create_snort_detection_rule(client)
    if snort_rule_id:
        delete_detection_rule(client, snort_rule_id)

    spl_rule_id = create_splunk_spl_detection_rule(client)
    if spl_rule_id:
        delete_detection_rule(client, spl_rule_id)

    logger.info("\n--- Creating Rule with Minimal Required Fields ---")
    minimal_rule_data = {
        "name": "Minimal Test Rule - Delete Me",
        "description": "Test rule with minimal required fields",
        "unifiedmitigationtype": 9,
        "content": "Basic rule content",
    }
    create_and_delete_mitigation_rule(client, minimal_rule_data)

    logger.info("\n--- Testing Project Associations ---")
    list_project_associations(client, limit=5)

    logger.info("\n--- Testing Mitigations With Relations ---")
    list_mitigations_with_relations(client, limit=5)

    logger.info("\n--- Testing Detection Performance Timeline ---")
    timeline_params = {"time_interval": "monthly"}
    get_detection_timeline(client, timeline_params)


def run_test(choice: "TestChoice", client: AttackIQRestClient, mitigation_id: Optional[str] = None):
    """Run the selected test."""
    test_functions = {
        TestChoice.LIST_RULES: lambda: test_list_rules(client),
        TestChoice.GET_RULES_BY_INTEGRATION_NAME: lambda: test_get_rules_by_integration_name(client),
        TestChoice.CREATE_SIGMA: lambda: test_create_sigma(client),
        TestChoice.CREATE_YARA: lambda: test_create_yara(client),
        TestChoice.CREATE_SNORT: lambda: test_create_snort(client),
        TestChoice.CREATE_SPL: lambda: test_create_spl(client),
        TestChoice.CREATE_MINIMAL: lambda: test_create_minimal(client),
        TestChoice.LIST_ASSOCIATIONS: lambda: test_list_associations(client),
        TestChoice.LIST_WITH_RELATIONS: lambda: test_list_with_relations(client),
        TestChoice.GET_TIMELINE: lambda: test_get_timeline(client),
        TestChoice.GET_DETECTION_RESULTS: lambda: test_get_detection_results(client, mitigation_id),
        TestChoice.SET_DETECTED: lambda: test_set_detected(client, mitigation_id),
        TestChoice.SET_NOT_DETECTED: lambda: test_set_not_detected(client, mitigation_id),
        TestChoice.GET_LATEST_STATUS: lambda: test_get_latest_status(client, mitigation_id),
        TestChoice.GET_ASSOCIATED_ASSESSMENT: lambda: test_get_associated_assessment(client, mitigation_id),
        TestChoice.GET_LATEST_ASSESSMENT_RUN_STATUS: lambda: test_get_latest_assessment_run_status(
            client, mitigation_id
        ),
        TestChoice.ANALYST_VERDICTS: lambda: test_analyst_verdicts(client, mitigation_id),
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
        LIST_RULES = "list_rules"
        GET_RULES_BY_INTEGRATION_NAME = "get_rules_by_integration_name"
        CREATE_SIGMA = "create_sigma"
        CREATE_YARA = "create_yara"
        CREATE_SNORT = "create_snort"
        CREATE_SPL = "create_spl"
        CREATE_MINIMAL = "create_minimal"
        LIST_ASSOCIATIONS = "list_associations"
        LIST_WITH_RELATIONS = "list_with_relations"
        GET_TIMELINE = "get_timeline"
        GET_DETECTION_RESULTS = "get_detection_results"
        SET_DETECTED = "set_detected"
        SET_NOT_DETECTED = "set_not_detected"
        GET_LATEST_STATUS = "get_latest_status"
        GET_ASSOCIATED_ASSESSMENT = "get_associated_assessment"
        GET_LATEST_ASSESSMENT_RUN_STATUS = "get_latest_assessment_run_status"
        ANALYST_VERDICTS = "analyst_verdicts"
        ALL = "all"

    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_PLATFORM_API_TOKEN)
    mitigation_id = os.environ.get("MITIGATION_ID") or os.environ.get("RULE_ID")

    # Change this to test different functionalities
    choice: TestChoice = TestChoice.ANALYST_VERDICTS
    # choice = TestChoice.CREATE_SIGMA
    # choice = TestChoice.CREATE_YARA
    # choice = TestChoice.CREATE_SNORT
    # choice = TestChoice.CREATE_SPL
    # choice = TestChoice.CREATE_MINIMAL
    # choice = TestChoice.LIST_ASSOCIATIONS
    # choice = TestChoice.LIST_WITH_RELATIONS
    # choice = TestChoice.GET_TIMELINE
    # choice = TestChoice.GET_DETECTION_RESULTS
    # choice = TestChoice.SET_DETECTED
    # choice = TestChoice.SET_NOT_DETECTED
    # choice = TestChoice.GET_LATEST_STATUS
    # choice = TestChoice.ALL

    run_test(choice, client, mitigation_id)
