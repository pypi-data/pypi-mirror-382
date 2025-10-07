import logging
import os
import time
from datetime import datetime

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Package, ResponseMessages

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def package_create(
    name: str,
    description: str | None = None,
    asset_ids: list[int] | None = None,
    arbitration: str | None = None,
) -> Package | None:
    """
    Create a new asset package.

    :param name: Name of the package
    :type name: str
    :param description: Description of the package
    :type description: str, optional
    :param asset_ids: List of asset IDs to include in the package
    :type asset_ids: list[int], optional
    :param arbitration: Arbitration details for the package
    :type arbitration: str, optional
    :return: The created package if successful, else None
    :rtype: Package | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"package": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating package: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating package: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating package: {e}")
        raise Exception(f"Error creating package: {e}")

    if response.status_code == 200 and "package" in response.json():
        return Package(**response.json()["package"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def package_return(package_id: int) -> Package | None:
    """
    Returns a particular package.

    :param package_id: The ID of the package to retrieve
    :return: The package if found, else None
    :rtype: Package | None
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages/{package_id}"

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error getting package: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting package: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting package: {e}")
        raise Exception(f"Error getting package: {e}")

    if response.status_code == 200 and "package" in response.json():
        return Package(**response.json()["package"])
    else:
        return None


@Decorators.check_env_vars
def packages_return() -> list[Package]:
    """
    Returns all packages.

    :return: List of all packages
    :rtype: list[Package]
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages"

    all_packages = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get packages: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get packages: {e}")
            raise

        data = response.json()

        if "packages" not in data:
            logger.error(f"Error, could not get packages: {response.content}")
            raise Exception(f"Error, could not get packages: {response.content}")

        all_packages.extend(data["packages"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Package(**x) for x in all_packages]


@Decorators.check_env_vars
def package_checkin(
    package_id: int, comments: str, location_id: int, checkin_date: datetime
) -> ResponseMessages | None:
    """
    Checks in an asset package.

    :param package_id: The ID of the package to check in
    :type package_id: int
    :param comments: Comments regarding the check-in
    :type comments: str
    :param location_id: The ID of the location where the package is being checked in
    :type location_id: int
    :param checkin_date: The date and time of the check-in
    :type checkin_date: datetime
    :return: Response messages if successful, else None
    :rtype: ResponseMessages | None
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages/{package_id}/checkin"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            json={
                "package": {
                    "comments": comments,
                    "location_id": location_id,
                    "checkin_date": checkin_date,
                }
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error checking in asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error checking in asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking in asset: {e}")
        raise Exception(f"Error checking in asset: {e}")

    if response.status_code == 200 and "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None
