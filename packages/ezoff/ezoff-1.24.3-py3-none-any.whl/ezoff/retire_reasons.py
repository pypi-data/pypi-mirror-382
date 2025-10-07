import logging
import os
import time

import requests
from ezoff._helpers import _fetch_page
from ezoff.data_model import RetireReason

logger = logging.getLogger(__name__)


def retire_reasons_return() -> list[RetireReason]:
    """
    Returns all retire reasons.

    :return: A list of all retire reasons.
    :rtype: list[RetireReason]
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/retire_reasons"

    all_retire_reasons = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get retire reasons: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get retire reasons: {e}")
            raise

        data = response.json()

        if "retire_reasons" not in data:
            logger.error(f"Error, could not get retire reasons: {response.content}")
            raise Exception(f"Error, could not get retire reasons: {response.content}")

        all_retire_reasons.extend(data["retire_reasons"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [RetireReason(**x) for x in all_retire_reasons]
