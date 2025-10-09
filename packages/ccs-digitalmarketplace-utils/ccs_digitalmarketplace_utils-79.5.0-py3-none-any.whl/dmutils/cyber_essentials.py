from datetime import datetime, timezone
from logging import Logger

from typing import Tuple, Union, Literal

from dmapiclient import DataInsightsAPIClient
from dmapiclient.errors import APIError
from dmutils.timing import logged_duration_for_external_request as log_external_request


def cyber_essentials_certificate_check(
    insights_api_client: DataInsightsAPIClient,
    certificate_number: str,
    certificate_type: Union[Literal['CE'], Literal['CE+']],
    logger: Logger
) -> Union[Tuple[Literal[False], str], Tuple[Literal[True], None]]:
    """
    Function to check if the cyber essentials certificate exists and that it is valid
    """
    try:
        with log_external_request(service="IASME Cyber essentials"):
            response = insights_api_client.get_cyber_essentials_certificate(
                certificate_number
            )["cyberEssentialsCertificateDetails"]

            if response['CertificateLevel'] != certificate_type:
                return False, 'certificate_not_right_level'

            if response['CertificationExpiryDate'] <= datetime.now(timezone.utc).strftime("%Y-%m-%d"):
                return False, 'certificate_expired'

            return True, None
    except APIError as e:
        if e.status_code == 404:
            return False, 'certificate_not_found'

        logger.error(
            "Error when getting a certificate",
            extra={
                "error": str(e),
            },
        )
        return False, 'api_error'
