import requests


class ReleaseAPIClient:
    """
    A client for interacting with the Release API.
    Supports authentication via username/password or personal access token.
    """

    def __init__(self, server_address, username=None, password=None, personal_access_token=None, **kwargs):
        """
        Initializes the API client.

        :param server_address: Base URL of the Release API server.
        :param username: Optional username for basic authentication.
        :param password: Optional password for basic authentication.
        :param personal_access_token: Optional personal access token for authentication.
        :param kwargs: Additional session parameters (e.g., headers, timeout).
        """
        if not server_address:
            raise ValueError("server_address must not be empty.")

        self.server_address = server_address.rstrip('/')  # Remove trailing slash if present
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

        # Set authentication method
        if username and password:
            self.session.auth = (username, password)
        elif personal_access_token:
            self.session.headers.update({"x-release-personal-token": personal_access_token})
        else:
            raise ValueError("Either username and password or a personal access token must be provided.")

        # Apply additional session configurations
        for key, value in kwargs.items():
            if key == 'headers':
                self.session.headers.update(value)  # Merge custom headers
            elif hasattr(self.session, key) and key != 'auth':  # Skip 'auth' key
                setattr(self.session, key, value)

    def _request(self, method, endpoint, params=None, json=None, data=None, **kwargs):
        """
        Internal method to send an HTTP request.

        :param method: HTTP method (GET, POST, PUT, DELETE, PATCH).
        :param endpoint: API endpoint (relative path).
        :param params: Optional query parameters.
        :param json: Optional JSON payload.
        :param data: Optional raw data payload.
        :param kwargs: Additional request options.
        :return: Response object.
        """
        if not endpoint:
            raise ValueError("Endpoint must not be empty.")

        kwargs.pop('auth', None)  # Remove 'auth' key if present to avoid conflicts
        url = f"{self.server_address}/{endpoint.lstrip('/')}"  # Construct full URL

        response = self.session.request(
            method, url, params=params, data=data, json=json, **kwargs
        )

        return response

    def get(self, endpoint, params=None, **kwargs):
        """Sends a GET request to the specified endpoint."""
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint, json=None, data=None, **kwargs):
        """Sends a POST request to the specified endpoint."""
        return self._request("POST", endpoint, data=data, json=json, **kwargs)

    def put(self, endpoint, json=None, data=None, **kwargs):
        """Sends a PUT request to the specified endpoint."""
        return self._request("PUT", endpoint, data=data, json=json, **kwargs)

    def delete(self, endpoint, params=None, **kwargs):
        """Sends a DELETE request to the specified endpoint."""
        return self._request("DELETE", endpoint, params=params, **kwargs)

    def patch(self, endpoint, json=None, data=None, **kwargs):
        """Sends a PATCH request to the specified endpoint."""
        return self._request("PATCH", endpoint, data=data, json=json, **kwargs)

    def close(self):
        """Closes the session."""
        self.session.close()

    def __enter__(self):
        """Enables the use of 'with' statements for automatic resource management."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensures the session is closed when exiting a 'with' block."""
        self.close()