"""Module Name: rest_adapter.py

Project Name: Rest Adapter

Description:
    A reusable REST API adapter built on top of the popular requests library.

Usage:
    This module can be imported to create an instance of this class:
        from rest_adapter import rest_adapter

Author: HBNet Networks
"""

from enum import Enum

import requests
import requests.packages


class HTTPReturnCode:
    """Contains properties and methods for HTTP codes"""

    _HTTP_STATUS_CODES = {
        100: "Continue",
        101: "Switching Protocols",
        102: "Processing",  # WebDAV

        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",

        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        307: "Temporary Redirect",
        308: "Permanent Redirect",

        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",  # Rarely used
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a teapot",  # Easter egg
        422: "Unprocessable Entity",  # WebDAV
        425: "Too Early",
        426: "Upgrade Required",
        429: "Too Many Requests",

        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
        505: "HTTP Version Not Supported",
        507: "Insufficient Storage",  # WebDAV
        511: "Network Authentication Required"
    }

    @staticmethod
    def message(code:int) -> str:
        """Return the message corressponding to this code"""
        if code in HTTPReturnCode._HTTP_STATUS_CODES.keys():
            return HTTPReturnCode._HTTP_STATUS_CODES[code]
        else:
            return 'Unknown HTTP code'

    @staticmethod
    def valid_code(code:int) -> bool:
        """Is this a valid code?"""
        if code in HTTPReturnCode._HTTP_STATUS_CODES.keys():
            return True
        else:
            return False

class APICallError(Exception):
    """Raised when a non-200 is returned"""
    _message: str
    _msg: str

    def __init__(self, response_code: int):
        if HTTPReturnCode.valid_code(response_code):
            _msg = (
                f"API call returned {response_code}, "
                f"{HTTPReturnCode.message(response_code)}"
            )
        else:
            _msg = f"API call returned HTTP{response_code}"

        self._message = _msg
        super().__init__(self._message)


    @property
    def message(self) -> str:
        """Return exception message"""
        return self._message

class HTTPRequestType(Enum):
    """Supported HTTP request types"""

    GET = 'get'
    PUT = 'put'
    DELETE = 'delete'
    POST = 'post'

class RestAdapter:
    """The main RestAdapter Class"""
    # === Private properties start here ===

    _base_url: str
    _api_key: str
    _ssl_verify: bool = True
    _port: int
    _timeout: int = 10

    _default_headers = {
        'Accept' : 'application/json',
        'Authorization' : str()
        }

    # === Private properties end here ===

    # === Private constants start here ===

    # TCP Ports reserved by IANA. Add any ports you want to exclude here.
    # TODO: Retrieve reserved ports list dynamically
    _RESERVED_TCP_PORTS = (
        0,
        *range(1, 3),
        953,
        994,
        *range(1011, 1021),
        *range(1023, 1024),
        1027,
    )

    # === Private constants end here ===

    # === Public property methods start here ===

    @property
    def base_url(self) -> str:
        """The base URL used for API requests."""
        return self._base_url

    @property
    def api_key(self) -> str:
        """The API key used for authenticating requests."""
        return self._api_key

    @property
    def ssl_verify(self) -> bool:
        """Whether SSL certificates should be verified."""
        return self._ssl_verify

    @property
    def port(self) -> int:
        """The network port used for API communication."""
        return self._port

    # === Public property methods end here ===

    def __init__(self,
                 address: str,
                 api_key: str,
                 *,
                 ssl_verify: bool = True,
                 port: int = 443,
                 timeout: int = _timeout):
        """
        Initializes a Rest Adapter instance.

        **PLEASE NOTE:**
        - Connections are required to be HTTPS, but cert checking can be disabled.

        Args:
            address (str): Base address (IP or FQDN) to build the request URL.
            api_key (str): API key for authentication.
            ssl_verify (bool, optional): Verify SSL certificates? Defaults to True.
            port (int, optional): Valid TCP port number. Defaults to 443.
            timeout (int, optional): API connection timeout. Defaults to golbal value.

        Raises:
            ValueError: If required parameters are not specified.
            ConnectionError: If the device cannot be reached for whatever reason.

        """
        self._ssl_verify = ssl_verify

        if not address: # Raise exception if no address supplied
            raise ValueError('Address is required')
        if not self._valid_port(port):
            raise ValueError('Invalid port specified')
        if not api_key:
            raise ValueError('API Key is required')

        # Set base URL
        if port == 443:
            self._base_url = f'https://{address}/'
        else:
            self._base_url = f'https://{address}:{str(port)}/'

        #Set timeout
        if timeout:
            self._timeout = timeout

        # Set base headers
        self._base_headers = self._default_headers.copy()
        self._base_headers['Authorization'] = f'Token: {api_key}'

        if not ssl_verify:
            requests.packages.urllib3.disable_warnings() # type: ignore

    # === Private methods start here ===

    def _do_call(
            self,
            url: str,
            method: HTTPRequestType = HTTPRequestType.GET, # Not yet implemented
            headers: dict | None = None,
            params: dict | None = None,
            data: dict | None = None,
            timeout: int = _timeout) -> dict:
        """Do an API call. Currently only supports GET.

        Args:
            url (str): API endpoint.
            method (HTTPRequestType, optional): Request type to do. Defaults to GET
            headers (dict, optional): Any additional parameters.
            params (dict, optional): Additional query parameters.
            timeout (int, optional): Override the global timeout setting
            data (dict, optional): Any additional data to pass to the call

        Raises:
            ValueError if required parameters are not specified.

        Returns:
            dict: JSON with response from the API call

        """
        data = data or {}
        _headers: dict = {}
        _response = {}
        _status_code: int = 0
        _json_return = {}
        _request_type: str

        if method != HTTPRequestType.GET:
            raise NotImplementedError('Only GET is currently implemented')

        if params is None: # If no params specified, use empty dict
            params = {}

        # Set headers
        if headers:
            for key, value in self._base_headers.items():
                _headers[key] = value

        # If additional headers are provided
        if headers:
            for key, value in headers:
                _headers[key] = value

        try:
            _response = requests.get(
                url,
                headers=_headers,
                params=params,
                json=data,
                verify=self._ssl_verify,
                timeout=timeout
                )
            _status_code = _response.status_code
            _json_return = _response.json()
        except (requests.RequestException, ValueError) as e:
            raise e

        if _status_code == 200:
            return _json_return
        else:
            raise APICallError(_status_code)

    def _valid_port(self, port:int) -> bool:
        """Check if port number is valid"""
        if port > 65535 or port < 1: # Outside valid range of 1-65535
            return False

        if port in self._RESERVED_TCP_PORTS: # Port is marked as reserved
            return False

        return True

    # === Private methods end here ===

    # === API call methods start here ===

    def do_get(self,
            url: str,
            headers: dict | None = None,
            params: dict | None = None,
            data: dict | None = None,
            timeout: int = _timeout) -> dict:
        """Do an HTTP GET call.

        Args:
            url (str): API endpoint.
            headers (dict, optional): Any additional parameters.
            params (dict, optional): Additional query parameters.
            timeout (int, optional): Override the global timeout setting.
            data (dict, optional): Any additional data to pass.

        Raises:
            ValueError if required parameters are not specified.

        Returns:
            dict: JSON with response from the API call

        """
        try:
            return self._do_call(url=url,
                                params=params,
                                data=data,
                                headers=headers,
                                timeout=timeout)
        except (requests.RequestException, ValueError) as e:
            raise e

    def do_put(self):
        """Not yet implemented"""
        raise NotImplementedError("do_put is not yet implemented.")

        # TODO: Implement do_put method

        ...

    def do_delete(self):
        """Not yet implemented"""
        raise NotImplementedError("do_delete is not yet implemented.")

        # TODO: Implement do_delete method

        ...

    def do_post(self):
        """Not yet implemented"""
        raise NotImplementedError("do_post is not yet implemented.")

        # TODO: Implement do_post method

        ...

    # === API call methods end here ===
