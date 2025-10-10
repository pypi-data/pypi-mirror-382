"""
HTTP client utilities for HiAgent SDK.

This module provides HTTP client functionality with retry logic,
error handling, and logging capabilities.
"""

import json
import time
from typing import Dict, Any, Optional
import httpx
from loguru import logger


class HTTPClientError(Exception):
    """Base exception for HTTP client errors"""
    pass


class HTTPRequestError(HTTPClientError):
    """Exception raised for HTTP request errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RetryConfig:
    """Retry configuration for HTTP requests"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        if attempt <= 0:
            return 0
        
        delay = self.initial_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)


class HTTPClient:
    """
    HTTP client for making API requests with retry logic and error handling.
    """
    
    def __init__(
        self,
        base_url: str,
        headers: Dict[str, str],
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        Initialize HTTP client.
        
        Args:
            base_url: Base URL for API requests
            headers: Default headers for requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.base_url = base_url
        self.default_headers = headers
        self.timeout = timeout
        self.retry_config = RetryConfig(
            max_attempts=max_retries + 1,  # +1 for initial attempt
            initial_delay=1.0
        )
        
        # Configure httpx client
        self.client = httpx.Client(
            timeout=self.timeout,
            headers=self.default_headers
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()
    
    def post(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make POST request with retry logic.
        
        Args:
            url: Request URL
            data: Request data
            headers: Additional headers (optional)
            
        Returns:
            Response data as dictionary
            
        Raises:
            HTTPRequestError: If request fails after all retries
        """
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        last_exception = None
        
        for attempt in range(self.retry_config.max_attempts):
            try:
                logger.debug(f"Making POST request to {url} (attempt {attempt + 1})")
                
                response = self.client.post(
                    url=url,
                    json=data,
                    headers=request_headers
                )
                
                logger.debug(f"Response status: {response.status_code}")
                
                # Check if request was successful
                if response.is_success:
                    try:
                        response_data = response.json()
                        logger.info(f"Request successful: {url}")
                        return response_data
                    except json.JSONDecodeError as e:
                        raise HTTPRequestError(
                            f"Failed to decode JSON response: {e}",
                            status_code=response.status_code
                        )
                else:
                    # Handle HTTP error status codes
                    try:
                        error_data = response.json()
                    except json.JSONDecodeError:
                        error_data = {"error": response.text}
                    
                    error_message = f"HTTP {response.status_code}: {error_data.get('error', 'Unknown error')}"
                    
                    # Don't retry for client errors (4xx)
                    if 400 <= response.status_code < 500:
                        raise HTTPRequestError(
                            error_message,
                            status_code=response.status_code,
                            response_data=error_data
                        )
                    
                    # Retry for server errors (5xx) and other errors
                    last_exception = HTTPRequestError(
                        error_message,
                        status_code=response.status_code,
                        response_data=error_data
                    )
                    
                    if attempt < self.retry_config.max_attempts - 1:
                        delay = self.retry_config.get_delay(attempt + 1)
                        logger.warning(f"Request failed, retrying in {delay}s... (attempt {attempt + 1}/{self.retry_config.max_attempts})")
                        time.sleep(delay)
                    
            except httpx.RequestError as e:
                last_exception = HTTPRequestError(f"Request error: {e}")
                
                if attempt < self.retry_config.max_attempts - 1:
                    delay = self.retry_config.get_delay(attempt + 1)
                    logger.warning(f"Request error, retrying in {delay}s... (attempt {attempt + 1}/{self.retry_config.max_attempts})")
                    time.sleep(delay)
            
            except Exception as e:
                last_exception = HTTPRequestError(f"Unexpected error: {e}")
                break  # Don't retry for unexpected errors
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise HTTPRequestError("All retry attempts failed")
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make GET request with retry logic.
        
        Args:
            url: Request URL
            params: Query parameters (optional)
            headers: Additional headers (optional)
            
        Returns:
            Response data as dictionary
            
        Raises:
            HTTPRequestError: If request fails after all retries
        """
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        last_exception = None
        
        for attempt in range(self.retry_config.max_attempts):
            try:
                logger.debug(f"Making GET request to {url} (attempt {attempt + 1})")
                if params:
                    logger.debug(f"Query params: {params}")
                
                response = self.client.get(
                    url=url,
                    params=params,
                    headers=request_headers
                )
                
                logger.debug(f"Response status: {response.status_code}")
                
                # Check if request was successful
                if response.is_success:
                    try:
                        response_data = response.json()
                        logger.info(f"Request successful: {url}")
                        return response_data
                    except json.JSONDecodeError as e:
                        raise HTTPRequestError(
                            f"Failed to decode JSON response: {e}",
                            status_code=response.status_code
                        )
                else:
                    # Handle HTTP error status codes
                    try:
                        error_data = response.json()
                    except json.JSONDecodeError:
                        error_data = {"error": response.text}
                    
                    error_message = f"HTTP {response.status_code}: {error_data.get('error', 'Unknown error')}"
                    
                    # Don't retry for client errors (4xx)
                    if 400 <= response.status_code < 500:
                        raise HTTPRequestError(
                            error_message,
                            status_code=response.status_code,
                            response_data=error_data
                        )
                    
                    # Retry for server errors (5xx) and other errors
                    last_exception = HTTPRequestError(
                        error_message,
                        status_code=response.status_code,
                        response_data=error_data
                    )
                    
                    if attempt < self.retry_config.max_attempts - 1:
                        delay = self.retry_config.get_delay(attempt + 1)
                        logger.warning(f"Request failed, retrying in {delay}s... (attempt {attempt + 1}/{self.retry_config.max_attempts})")
                        time.sleep(delay)
                    
            except httpx.RequestError as e:
                last_exception = HTTPRequestError(f"Request error: {e}")
                
                if attempt < self.retry_config.max_attempts - 1:
                    delay = self.retry_config.get_delay(attempt + 1)
                    logger.warning(f"Request error, retrying in {delay}s... (attempt {attempt + 1}/{self.retry_config.max_attempts})")
                    time.sleep(delay)
            
            except Exception as e:
                last_exception = HTTPRequestError(f"Unexpected error: {e}")
                break  # Don't retry for unexpected errors
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise HTTPRequestError("All retry attempts failed")