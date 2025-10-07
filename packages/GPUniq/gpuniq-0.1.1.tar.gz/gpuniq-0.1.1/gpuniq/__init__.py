"""GPUniq - Python client for GPUniq LLM API."""

import requests
from typing import Optional

__version__ = "0.1.1"

API_BASE_URL = "https://api.gpuniq.ru/v1"


class GPUniqError(Exception):
    """Base exception for GPUniq errors."""
    def __init__(self, message: str, error_code: Optional[str] = None, http_status: Optional[int] = None):
        self.message = message
        self.error_code = error_code
        self.http_status = http_status
        super().__init__(self.message)


class GPUniqClient:
    """Client for interacting with GPUniq LLM API."""

    def __init__(self, api_key: str):
        """Initialize GPUniq client.

        Args:
            api_key: Your GPUniq API key (starts with 'gpuniq_')
        """
        if not api_key:
            raise ValueError("API key is required")
        if not api_key.startswith("gpuniq_"):
            raise ValueError("Invalid API key format. Key should start with 'gpuniq_'")

        self.api_key = api_key
        self.base_url = API_BASE_URL

    def request(
        self,
        model: str,
        message: str,
        role: str = "user",
        timeout: int = 30
    ) -> str:
        """Send a request to GPUniq LLM API.

        Args:
            model: Model identifier (e.g., 'openai/gpt-oss-120b')
            message: Message content to send
            role: Message role (default: 'user')
            timeout: Request timeout in seconds (default: 30)

        Returns:
            str: Response content from the LLM

        Raises:
            GPUniqError: If the API request fails
        """
        if not message:
            raise ValueError("Message cannot be empty")

        url = f"{self.base_url}/llm/chat/completions"
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "messages": [
                {
                    "role": role,
                    "content": message
                }
            ],
            "model": model
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            data = response.json()

            # Check for API error
            if data.get("exception", 0) != 0:
                error_data = data.get("data", {})
                error_message = data.get("message", "Unknown error")
                error_code = error_data.get("error_code")

                raise GPUniqError(
                    message=error_message,
                    error_code=error_code,
                    http_status=response.status_code
                )

            # Extract content from successful response
            return data.get("data", {}).get("content", "")

        except requests.exceptions.RequestException as e:
            raise GPUniqError(f"Request failed: {str(e)}")


def init(api_key: str) -> GPUniqClient:
    """Initialize and return a GPUniq client.

    Args:
        api_key: Your GPUniq API key (starts with 'gpuniq_')

    Returns:
        GPUniqClient: Initialized client instance

    Example:
        >>> import gpuniq
        >>> client = gpuniq.init("gpuniq_your_key_here")
        >>> response = client.request("openai/gpt-oss-120b", "Hello!")
        >>> print(response)
    """
    return GPUniqClient(api_key)
