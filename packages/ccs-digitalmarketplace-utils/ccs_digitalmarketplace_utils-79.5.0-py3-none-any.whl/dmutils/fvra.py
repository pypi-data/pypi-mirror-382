from dmapiclient.errors import APIError

from dmapiclient import DataInsightsAPIClient
from logging import Logger
from typing import List
from dmutils.timing import logged_duration_for_external_request as log_external_request


def supplier_financial_viablitity_risk_assessments(
    insights_api_client: DataInsightsAPIClient,
    duns_numbers: List[str],
    logger: Logger
):
    """
    Function to collect the metrics results for a list of suppliers.
    If an exception is raised then the error is logged and an empty array is returned
    """
    try:
        with log_external_request(service="Spotlight FVRA"):
            return insights_api_client.get_financials_from_duns_numbers(duns_numbers)["organisationMetrics"]
    except APIError as e:
        logger.error(
            "Failed to get metrics for all suppliers",
            extra={
                "error": str(e),
            },
        )
        return []
