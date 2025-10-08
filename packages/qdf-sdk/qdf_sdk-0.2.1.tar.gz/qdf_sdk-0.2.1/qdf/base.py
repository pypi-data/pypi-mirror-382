"""
Base HTTP client with retry logic and error handling
"""

import time
import requests
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
import logging

from .exceptions import APIError, NetworkError, NotFoundError, RateLimitError

logger = logging.getLogger(__name__)


class BaseClient:
    """Base HTTP client with retry and error handling"""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize base client

        Args:
            base_url: Base URL for API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Setup session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'qdf-sdk/0.1.0'
        })

        # Add API key to headers if provided
        if api_key:
            self.session.headers['X-API-Key'] = api_key

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[Dict, list]:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be joined with base_url)
            params: URL parameters
            json_data: JSON payload for POST/PUT requests
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON data

        Raises:
            APIError: API returned an error
            NetworkError: Network-related error
        """
        url = urljoin(self.base_url, endpoint)

        # Remove None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=self.timeout,
                    **kwargs
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                        time.sleep(retry_after)
                        continue
                    raise RateLimitError(retry_after=retry_after)

                # Handle 404
                if response.status_code == 404:
                    raise NotFoundError(f"Resource not found: {endpoint}")

                # Handle other errors
                if response.status_code >= 400:
                    error_msg = f"API error {response.status_code}: {response.text}"
                    raise APIError(error_msg, status_code=response.status_code, response_text=response.text)

                # Success
                return response.json()

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Request timeout, retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                raise NetworkError(f"Request timeout after {self.max_retries} attempts")

            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Connection error, retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                raise NetworkError(f"Connection error: {str(e)}")

            except requests.exceptions.RequestException as e:
                raise NetworkError(f"Request failed: {str(e)}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Union[Dict, list]:
        """Make GET request"""
        return self._make_request('GET', endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Union[Dict, list]:
        """Make POST request"""
        return self._make_request('POST', endpoint, json_data=json_data, **kwargs)

    def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Union[Dict, list]:
        """Make PUT request"""
        return self._make_request('PUT', endpoint, json_data=json_data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Union[Dict, list]:
        """Make DELETE request"""
        return self._make_request('DELETE', endpoint, **kwargs)