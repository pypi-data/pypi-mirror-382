import json
from urllib.parse import urlparse

from cdp import __version__
from cdp.auth.utils.http import GetAuthHeadersOptions, get_auth_headers
from cdp.openapi_client import rest
from cdp.openapi_client.api_client import ApiClient
from cdp.openapi_client.api_response import ApiResponse, T as ApiResponseT
from cdp.openapi_client.configuration import Configuration
from cdp.openapi_client.constants import ERROR_DOCS_PAGE_URL, SDK_DEFAULT_SOURCE
from cdp.openapi_client.errors import ApiError, NetworkError, HttpErrorType, is_openapi_error
from cdp.openapi_client.exceptions import ApiException


class CdpApiClient(ApiClient):
    """CDP API Client that handles authentication and API calls for Coinbase."""

    def __init__(
        self,
        api_key_id: str,
        api_key_secret: str,
        wallet_secret: str = None,
        debugging: bool = False,
        base_path: str = "https://api.cdp.coinbase.com/platform",
        max_network_retries: int = 3,
        source: str = SDK_DEFAULT_SOURCE,
        source_version: str = __version__,
    ):
        """Initialize the CDP API Client.

        Args:
            api_key_id (str): The API key id for authentication.
            api_key_secret (str): The API key secret for authentication.
            wallet_secret (str): The wallet secret for authentication.
            debugging (bool): Whether debugging is enabled.
            base_path (str, optional): The base URL for the API. Defaults to "https://api.cdp.coinbase.com/platform".
            max_network_retries (int): The maximum number of network retries. Defaults to 3.
            source (str): Specifies whether the sdk is being used directly or if it's an Agentkit extension.
            source_version (str): The version of the source package.

        """
        configuration = Configuration(host=base_path, retries=max_network_retries)
        super().__init__(configuration)

        self.api_key_id = api_key_id
        self.api_key_secret = api_key_secret
        self.wallet_secret = wallet_secret
        self.source = source
        self.source_version = source_version
        self._debugging = debugging

    async def call_api(
        self,
        method,
        url,
        header_params=None,
        body=None,
        post_params=None,
        _request_timeout=None,
    ) -> rest.RESTResponse:
        """Make the HTTP request (asynchronous)."""
        if self._debugging is True:
            print(f"CDP API REQUEST: {method} {url}")

        # Parse URL for auth headers
        parsed_url = urlparse(
            url if url.startswith("http") else self.configuration.host + url
        )

        # Get auth headers
        auth_headers = get_auth_headers(
            GetAuthHeadersOptions(
                api_key_id=self.api_key_id,
                api_key_secret=self.api_key_secret,
                request_method=method,
                request_host=parsed_url.netloc,
                request_path=parsed_url.path,
                request_body=body,
                wallet_secret=self.wallet_secret,
                source=self.source,
                source_version=self.source_version,
            )
        )

        # Merge headers
        request_headers = header_params or {}
        request_headers.update(auth_headers)

        if self._debugging is True:
            print(f"Request headers: {request_headers}")

        # Make request through parent class
        try:
            response = await super().call_api(
                method, url, request_headers, body, post_params, _request_timeout
            )
            return response
        except ApiException as e:
            if self._debugging:
                print(f"Error: {e}")

            # Try to parse response body as JSON
            try:
                error_data = json.loads(e.body) if e.body else None
                if error_data and is_openapi_error(error_data):
                    # Handle OpenAPI formatted error
                    raise ApiError(
                        http_code=e.status,
                        error_type=error_data["errorType"],
                        error_message=error_data["errorMessage"],
                        correlation_id=error_data.get("correlationId"),
                        error_link=error_data.get(
                            "errorLink",
                            f"{ERROR_DOCS_PAGE_URL}#{error_data['errorType'].lower()}",
                        ),
                    ) from None
            except (json.JSONDecodeError, AttributeError):
                pass

            # Handle HTTP status code based errors
            if e.status == 401:
                raise ApiError(
                    http_code=401,
                    error_type=HttpErrorType.UNAUTHORIZED,
                    error_message="Unauthorized.",
                    error_link=f"{ERROR_DOCS_PAGE_URL}#unauthorized",
                ) from None
            elif e.status == 403:
                # Special handling for IP blocklist and other gateway-level 403s
                response_data = e.body
                is_gateway_error = False

                if response_data:
                    response_str = str(response_data).lower()
                    is_gateway_error = any(keyword in response_str for keyword in ["forbidden", "ip", "blocked", "gateway"])

                if is_gateway_error:
                    raise NetworkError(
                        error_type=HttpErrorType.NETWORK_IP_BLOCKED,
                        error_message="Access denied. Your IP address may be blocked or restricted.",
                        network_details={
                            "code": "IP_BLOCKED",
                            "message": str(response_data) if response_data else None,
                            "retryable": False,
                        },
                        error_link=f"{ERROR_DOCS_PAGE_URL}#network-errors",
                    ) from None

                # Regular 403 forbidden error
                raise ApiError(
                    http_code=403,
                    error_type=HttpErrorType.UNAUTHORIZED,
                    error_message="Forbidden. You don't have permission to access this resource.",
                    error_link=f"{ERROR_DOCS_PAGE_URL}#forbidden",
                ) from None
            elif e.status == 404:
                raise ApiError(
                    http_code=404,
                    error_type=HttpErrorType.NOT_FOUND,
                    error_message="API not found",
                    error_link=f"{ERROR_DOCS_PAGE_URL}#not_found",
                ) from None
            elif e.status == 502:
                raise ApiError(
                    http_code=502,
                    error_type=HttpErrorType.BAD_GATEWAY,
                    error_message="Bad gateway.",
                    error_link=ERROR_DOCS_PAGE_URL,
                ) from None
            elif e.status == 503:
                raise ApiError(
                    http_code=503,
                    error_type=HttpErrorType.SERVICE_UNAVAILABLE,
                    error_message="Service unavailable. Please try again later.",
                    error_link=ERROR_DOCS_PAGE_URL,
                ) from None

            # Default to unexpected error
            error_text = ""

            if e.body:
                try:
                    error_text = json.dumps(e.body)
                except (TypeError, ValueError):
                    error_text = str(e.body)

            error_message = (
                f"An unexpected error occurred: {error_text}"
                if error_text
                else "An unexpected error occurred."
            )

            raise ApiError(
                http_code=e.status or 500,
                error_type=HttpErrorType.UNEXPECTED_ERROR,
                error_message=error_message,
                error_link=ERROR_DOCS_PAGE_URL,
            ) from None
        except Exception as e:
            if self._debugging:
                print(f"Error: {e}")

            # Handle network errors
            error_str = str(e).lower()

            # Connection refused errors
            if "connection refused" in error_str or "econnrefused" in error_str:
                raise NetworkError(
                    error_type=HttpErrorType.NETWORK_CONNECTION_FAILED,
                    error_message="Unable to connect to CDP service. The service may be unavailable.",
                    network_details={
                        "code": "ECONNREFUSED",
                        "message": str(e),
                        "retryable": True,
                    },
                    error_link=f"{ERROR_DOCS_PAGE_URL}#network-errors",
                ) from None

            # Timeout errors
            elif any(timeout_keyword in error_str for timeout_keyword in ["timeout", "timed out", "etimedout", "econnaborted"]):
                raise NetworkError(
                    error_type=HttpErrorType.NETWORK_TIMEOUT,
                    error_message="Request timed out. Please try again.",
                    network_details={
                        "code": "ETIMEDOUT",
                        "message": str(e),
                        "retryable": True,
                    },
                    error_link=f"{ERROR_DOCS_PAGE_URL}#network-errors",
                ) from None

            # DNS resolution errors
            elif any(dns_keyword in error_str for dns_keyword in ["nodename nor servname provided", "getaddrinfo failed", "name or service not known", "enotfound"]):
                raise NetworkError(
                    error_type=HttpErrorType.NETWORK_DNS_FAILURE,
                    error_message="DNS resolution failed. Please check your network connection.",
                    network_details={
                        "code": "ENOTFOUND",
                        "message": str(e),
                        "retryable": False,
                    },
                    error_link=f"{ERROR_DOCS_PAGE_URL}#network-errors",
                ) from None

            # Generic network errors
            elif any(network_keyword in error_str for network_keyword in ["network", "econnreset", "connection reset", "connection aborted"]):
                raise NetworkError(
                    error_type=HttpErrorType.NETWORK_CONNECTION_FAILED,
                    error_message="Network error occurred. Please check your connection and try again.",
                    network_details={
                        "code": "NETWORK_ERROR",
                        "message": str(e),
                        "retryable": True,
                    },
                    error_link=f"{ERROR_DOCS_PAGE_URL}#network-errors",
                ) from None

            # Default unexpected error
            raise ApiError(
                http_code=500,
                error_type=HttpErrorType.UNEXPECTED_ERROR,
                error_message=f"An unexpected error occurred: {e!s}",
                error_link=ERROR_DOCS_PAGE_URL,
            ) from None

    def response_deserialize(
        self,
        response_data: rest.RESTResponse,
        response_types_map: dict[str, ApiResponseT] | None = None,
    ) -> ApiResponse[ApiResponseT]:
        """Deserialize the API response.

        Args:
            response_data: REST response data.
            response_types_map: Map of response types.

        Returns:
            ApiResponse[ApiResponseT]

        """
        try:
            return super().response_deserialize(response_data, response_types_map)
        except ApiException as e:
            # Try to parse response body as JSON
            try:
                error_data = json.loads(e.body) if e.body else None
                if error_data and is_openapi_error(error_data):
                    raise ApiError(
                        http_code=e.status,
                        error_type=error_data["errorType"],
                        error_message=error_data["errorMessage"],
                        correlation_id=error_data.get("correlationId"),
                        error_link=error_data.get(
                            "errorLink",
                            f"{ERROR_DOCS_PAGE_URL}#{error_data['errorType'].lower()}",
                        ),
                    ) from None
            except (json.JSONDecodeError, AttributeError) as parse_error:
                # If we can't parse as OpenAPI error, include the parse error details
                raise ApiError(
                    http_code=e.status,
                    error_type="unexpected_error",
                    error_message=f"An unexpected error occurred: {parse_error!s}. Original error message: {e!s}.",
                    error_link=f"{ERROR_DOCS_PAGE_URL}",
                ) from None
