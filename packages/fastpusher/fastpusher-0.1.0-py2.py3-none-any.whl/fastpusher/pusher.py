import logging
from typing import List

import requests

from .exceptions import (
    AuthenticationError,
    ConnectionError,
    FastPusherError,
    RateLimitError,
    ValidationError,
)


class FastPusher:
    """FastPusher - Main class for sending push notifications"""

    def __init__(
        self,
        url: str,
        token: str,
        timeout: int = 10,
        retry_attempts: int = 3,
        debug: bool = False,
    ):
        """
        Initialize FastPusher object

        Args:
            url: API server URL address
            token: Authentication token
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            debug: Debug mode
        """
        self.url = url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session = requests.Session()

        # Setup logger
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)

        # Setup headers
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "FastPusher-Python/0.0.1",
            }
        )

    def _validate_input(self, channel: str, data: dict) -> None:
        """Validate input data"""
        if not channel or not isinstance(channel, str):
            raise ValidationError("Channel name is empty or invalid format")

        if not data or not isinstance(data, dict):
            raise ValidationError("Data is empty or invalid format")

    def _handle_response(self, response: requests.Response) -> dict:
        """Handle API response"""
        try:
            if response.status_code == 401:
                raise AuthenticationError("Token is invalid or expired")
            elif response.status_code == 429:
                raise RateLimitError("Too many requests sent, please wait")
            elif response.status_code >= 500:
                raise ConnectionError(f"Server error: {response.status_code}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.JSONDecodeError:
            raise FastPusherError("Server returned invalid response")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Connection error: {str(e)}")

    def push(self, channel: str, data: dict) -> dict:
        """
        Send message to a single channel

        Args:
            channel: Channel name
            data: Data to be sent

        Returns:
            API response
        """
        self._validate_input(channel, data)

        url = f"{self.url}/api/partners/push"
        payload = {"client_id": channel, "data": data}

        for attempt in range(self.retry_attempts + 1):
            try:
                self.logger.debug(
                    f"Sending message: {channel} - {attempt + 1}/{self.retry_attempts + 1}"
                )

                response = self.session.post(
                    url=url, json=payload, timeout=self.timeout
                )

                result = self._handle_response(response)
                self.logger.info(f"Message sent successfully: {channel}")
                return result

            except (ConnectionError, requests.exceptions.Timeout) as e:
                if attempt == self.retry_attempts:
                    raise e
                self.logger.warning(f"Retrying: {attempt + 1}/{self.retry_attempts}")

    def push_bulk(self, channels: List[str], data: dict) -> List[dict]:
        """
        Send message to multiple channels

        Args:
            channels: List of channel names
            data: Data to be sent

        Returns:
            List of results for each channel
        """
        if not channels:
            raise ValidationError("Channel list is empty")

        results = []
        for channel in channels:
            try:
                result = self.push(channel, data)
                results.append(
                    {
                        "channel": channel,
                        "success": True,
                        "result": result,
                        "error": None,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "channel": channel,
                        "success": False,
                        "result": None,
                        "error": str(e),
                    }
                )

        return results

    def test_connection(self) -> bool:
        """
        Test connection to server

        Returns:
            True if connection is available
        """
        try:
            response = self.session.get(f"{self.url}/api/health", timeout=10)
            return response.status_code == 200
        except:  # noqa
            return False

    def close(self):
        """Close session"""
        self.session.close()
