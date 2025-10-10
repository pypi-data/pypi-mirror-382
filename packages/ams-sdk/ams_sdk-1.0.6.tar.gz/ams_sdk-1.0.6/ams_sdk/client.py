import requests
from typing import Dict, Any, Optional


class AMSClient:
    """
    Python SDK for the Alternative Macro Signals (AMS) API.
    Provides methods for authentication and querying endpoints like `/nbstat`.
    """

    def __init__(self, service_url: str, api_key: str):
        """
        Initialize the AMSClient with service URL and API key.
        :param service_url: Base URL for the API service.
        :param api_key: API key provided by AMS.
        """
        self.service_url = service_url
        self.api_key = api_key
        self.token = None

    def authenticate(self) -> str:
        """
        Authenticate using the API key to fetch a Bearer token.
        :return: Bearer token as a string.
        :raises: Exception if the authentication request fails.
        """
        headers = {'X-API-Key': self.api_key}
        response = requests.post(f"{self.service_url}/token", headers=headers)

        if response.status_code == 200:
            self.token = response.json()
            return self.token
        else:
            raise Exception(f"Authentication failed! Status: {response.status_code}, Message: {response.text}")

    def _get_headers(self) -> Dict[str, str]:
        """
        Construct headers for authenticated requests.
        :return: A dictionary containing the Authorization header.
        :raises: Exception if the token is missing.
        """
        if not self.token:
            raise Exception("Missing token! Please authenticate first using `authenticate()`.")

        return {"Authorization": f"Bearer {self.token}"}

    def query_endpoint(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generic function to query a specific endpoint.
        :param endpoint: The endpoint path, e.g., "/nbstat".
        :param params: Optional query parameters for the request.
        :return: Response as a dictionary.
        :raises: Exception if the request fails.
        """
        url = f"{self.service_url}{endpoint}"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request to {endpoint} failed! Status: {response.status_code}, Message: {response.text}")

