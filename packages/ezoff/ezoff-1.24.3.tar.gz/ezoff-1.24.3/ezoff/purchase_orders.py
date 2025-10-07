import logging
import os
import time

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import PurchaseOrder

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def purchase_order_create(title: str, vendor_id: int) -> PurchaseOrder | None:
    """
    Creates a new purchase order.

    :param title: Title of the purchase order.
    :type title: str
    :param vendor_id: ID of the vendor for the purchase order.
    :type vendor_id: int
    :return: The created purchase order or None if creation failed.
    :rtype: PurchaseOrder | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/purchase_orders"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"purchase_order": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating purchase order: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating purchase order: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating purchase order: {e}")
        raise Exception(f"Error creating purchase order: {e}")

    if response.status_code == 200 and "purchase_order" in response.json():
        return PurchaseOrder(**response.json()["purchase_order"])
    else:
        return None


@Decorators.check_env_vars
def purchase_order_return(purchase_order_id: int) -> PurchaseOrder | None:
    """
    Returns a particular purchase order.

    :param purchase_order_id: ID of the purchase order to return.
    :type purchase_order_id: int
    :return: The requested purchase order or None if not found.
    :rtype: PurchaseOrder | None
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/purchase_orders/{purchase_order_id}"

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
            f"Error getting purchase order: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting purchase order: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting purchase order: {e}")
        raise Exception(f"Error getting purchase order: {e}")

    if response.status_code == 200 and "purchase_order" in response.json():
        return PurchaseOrder(**response.json()["purchase_order"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def purchase_orders_return() -> list[PurchaseOrder]:
    """
    Returns all purchase orders.

    :return: A list of all purchase orders.
    :rtype: list[PurchaseOrder]
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/purchase_orders"

    all_purchase_orders = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get purchase orders: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get purchase orders: {e}")
            raise

        data = response.json()

        if "purchase_orders" not in data:
            logger.error(f"Error, could not get purchase orders: {response.content}")
            raise Exception(f"Error, could not get purchase orders: {response.content}")

        all_purchase_orders.extend(data["purchase_orders"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [PurchaseOrder(**x) for x in all_purchase_orders]


# TODO Update

# TODO Mark void

# TODO Add items

# TODO Receive items

# TODO Mark Confirmed

# TODO Add items

# TODO Delete
