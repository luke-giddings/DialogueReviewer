"""
Networking Layer for the Gridly REST API

Usage: Create a GridlySocket class with the Gridly View ID and the API key you want, then call its methods
See: https://www.gridly.com/docs/api/ for documentation about what REST calls are available
"""

import json
import logging
from typing import Any, Final, Literal, cast
from urllib.parse import quote

import requests

type SocketResult = tuple[Literal[False], None] | tuple[Literal[True], Any]

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SEC: Final[int] = 30
MAX_RECORDS_PER_PAGE: Final[int] = 1000


class GridlySocket:
    """
    Currently a stateless class that wraps all the ways to communicate with the Gridly Database.
    Construction Args:
        view_id: The Gridly View ID that you want to get the records from.
        api_key: The Gridly API Key that will allow you access to Gridly.
    """

    _api_endpoint: Final[str] = "https://api.gridly.com/v1/views"
    _header_count_id: Final[str] = "X-Total-Count"

    def __init__(self, view_id: str, api_key: str):
        self._view_id: str = view_id
        self._gridly_api_key: Final[str] = api_key
        self._default_api_header: Final[dict[str, str]] = {
            "Content-Type": "application/json",
            "Authorization": f"ApiKey {self._gridly_api_key}",
        }

    def set_view_id(self, view_id: str):
        """
        Change the View you want to get the records from.
        Args:
            view_id: The Gridly View ID that you want to get the records from.
        """
        self._view_id = view_id

    def retrieve_all_records(self) -> SocketResult:
        """
        Get all the records from the current Gridly View.
        Returns:
            SocketResult - A tuple where the 1st value is if the function succeeded.
                If it succeeds, the 2nd value will be the json response containing all the records from the View.
                If it fails, the 2nd value will be None.
        """
        offset_val = 0

        json_response: list[Any] = []

        while True:
            page_string = json.dumps({"offset": offset_val, "limit": MAX_RECORDS_PER_PAGE})
            encoded_page_string = quote(page_string)
            url = f"{self._api_endpoint}/{self._view_id}/records?page={encoded_page_string}"
            debug_url = f"{self._api_endpoint}/{self._view_id}/records?page={page_string}"

            try:
                response = requests.get(url, headers=self._default_api_header, timeout=REQUEST_TIMEOUT_SEC)
            except requests.RequestException as e:
                logger.error("%s: %s", debug_url, e)
                return (False, None)

            logger.info("%s: %s", debug_url, response)

            if response.status_code != 200:
                logger.error("%s\n%s", response.reason, response.text)
                return (False, None)

            try:
                this_response = response.json()
                if not isinstance(this_response, list):
                    logger.error("Expected list response, got %s", type(this_response).__name__)
                    return (False, None)
                json_response.extend(cast(list[Any], this_response))
            except json.JSONDecodeError as e:
                logger.error("Json Failed to parse: %s", e)
                return (False, None)

            total_records = int(response.headers.get(self._header_count_id, "0"))

            offset_val += MAX_RECORDS_PER_PAGE
            if offset_val >= total_records:
                break

        return (True, json_response)

    def get(self, url_fragment: str) -> SocketResult:
        """
        Send the 'get' command to Gridly's REST API.  See docs for available commands.
        Args:
            url_fragment: The part of the URL after the Gridly View ID.
        Example: socket.get("paths/tree?rootPath=Movies") to get all the paths from the root path 'Movies'.
        Returns:
            SocketResult - A tuple where the 1st value is if the function succeeded.
                If it succeeds, the 2nd value will be the json response from that command.
                If it fails, the 2nd value will be None.
        """
        if url_fragment != "":
            offset_val = 0
            page_string = json.dumps({"offset": offset_val, "limit": MAX_RECORDS_PER_PAGE})
            encoded_page_string = quote(page_string)
            url = f"{self._api_endpoint}/{self._view_id}/{url_fragment}?page={encoded_page_string}"
            debug_url = f"{self._api_endpoint}/{self._view_id}/{url_fragment}?page={page_string}"
        else:
            debug_url = url = f"{self._api_endpoint}/{self._view_id}"

        try:
            response = requests.get(url, headers=self._default_api_header, timeout=REQUEST_TIMEOUT_SEC)
        except requests.RequestException as e:
            logger.error("%s: %s", debug_url, e)
            return (False, None)

        logger.info("%s: %s", debug_url, response)

        if response.status_code != 200:
            logger.error("%s\n%s", response.reason, response.text)
            return (False, None)

        try:
            json_response = response.json()
        except json.JSONDecodeError as e:
            logger.error("%s: %s", debug_url, e)
            return (False, None)

        return (True, json_response)

    def patch(self, url_fragment: str, payload: str, debug_string: str) -> SocketResult:
        """
        Send the 'patch' command to Gridly's REST API.  See docs for available commands.
        Args:
            url_fragment: The part of the URL after the Gridly View ID.
            payload: The json payload specified for the command.
            debug_string: If an error happens this debug string will be added to the logs to help with context.
        Returns:
            SocketResult - A tuple where the 1st value is if the function succeeded.
                If it succeeds, the 2nd value will be the json response from that command.
                If it fails, the 2nd value will be None.
        """
        url = f"{self._api_endpoint}/{self._view_id}/{url_fragment}"

        try:
            response = requests.patch(url, headers=self._default_api_header, data=payload, timeout=REQUEST_TIMEOUT_SEC)
        except requests.RequestException as e:
            logger.error("%s: %s", url, e)
            return (False, None)

        logger.info("%s [%s]: %s", url, debug_string, response)

        if response.status_code != 200:
            logger.error("[%s] %s\n%s", debug_string, response.reason, response.text)
            return (False, None)

        try:
            json_response = response.json()
        except json.JSONDecodeError as e:
            logger.error("%s [%s]: %s", url, debug_string, e)
            return (False, None)

        return (True, json_response)

    def put(self, url_fragment: str, payload: str, debug_string: str) -> SocketResult:
        """
        Send the 'put' command to Gridly's REST API.  See docs for available commands.
        Args:
            url_fragment: The part of the URL after the Gridly View ID.
            payload: The json payload specified for the command.
            debug_string: If an error happens this debug string will be added to the logs to help with context.
        Returns:
            SocketResult - A tuple where the 1st value is if the function succeeded.
                If it succeeds, the 2nd value will be the json response from that command.
                If it fails, the 2nd value will be None.
        """
        url = f"{self._api_endpoint}/{self._view_id}/{url_fragment}"

        try:
            response = requests.put(url, headers=self._default_api_header, data=payload, timeout=REQUEST_TIMEOUT_SEC)
        except requests.RequestException as e:
            logger.error("%s [%s]: %s", url, debug_string, e)
            return (False, None)

        logger.info("%s [%s]: %s", url, debug_string, response)

        if response.status_code != 200:
            logger.error("[%s] %s\n%s", debug_string, response.reason, response.text)
            return (False, None)

        try:
            json_response = response.json()
        except json.JSONDecodeError as e:
            logger.error("%s [%s]: %s", url, debug_string, e)
            return (False, None)

        return (True, json_response)
